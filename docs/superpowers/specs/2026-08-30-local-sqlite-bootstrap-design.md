# Design: Local SQLite bootstrap

Date: 2026-08-30  
Repo: Never-lab/FuelPyTracker  
Status: draft for review

## Problem

1. Public demo (`fuelpytracker-demo.streamlit.app`) returns HTTP 303 to Streamlit share auth — not usable as an open showcase.
2. Fresh clone cannot start: `src/database/core.py` requires `.streamlit/secrets.toml` with a live Postgres URL; missing file → `st.stop()` / hard failure.
3. `tests/unit/services/test_auth.py` calls `sys.exit(1)` when secrets are absent, aborting the whole pytest session.
4. Onboarding docs assume Supabase + Docker before any UI is visible.

## Goal

Allow a **zero-cloud** first run and green unit tests via an explicit local SQLite path, while keeping Supabase Postgres as the production/demo path.

## Non-goals

- Creating or wiring the Never-lab Supabase project (follow-up after merge).
- Restoring the Streamlit keep-alive GitHub Action (tracked on the issue checklist only).
- Multi-user auth on SQLite; full RLS parity; migrating production data.
- Broad refactors of UI or CRUD.

## Approach (chosen)

**Explicit `LOCAL_SQLITE` bootstrap** (not silent fallback on any missing secret).

| Mode | Trigger | Database | Auth UI |
|------|---------|----------|---------|
| Local bootstrap | `LOCAL_SQLITE=True` (env) | `sqlite:///data/local.db` (or override URL) | `DEMO_MODE=True` injects `DEMO_USER` (default UUID/email in `.env.example`) |
| Production / Cloud | `LOCAL_SQLITE` unset/false | Postgres from `st.secrets["database"]["url"]` | Supabase Auth as today |

Rationale: fail-closed for misconfigured deploys; opt-in for local/CI.

## Behavior

### Env / config

- `.env.example` adds:
  - `LOCAL_SQLITE=False`
  - Stable demo defaults: `DEMO_USER_ID=00000000-0000-4000-8000-000000000001`, `DEMO_USER_EMAIL=demo@local.fuelpytracker`
- `.streamlit/secrets.toml.example` documents optional `[demo]` block and notes that with `LOCAL_SQLITE=True` the `[database]` URL may be omitted or set to `sqlite:///data/local.db`.
- `data/*.db` already gitignored — keep that.

### `src/database/core.py`

Resolution order for `DATABASE_URL`:

1. If `LOCAL_SQLITE` env is truthy → `sqlite:///data/local.db` (ensure `data/` exists); use `check_same_thread=False` connect args for Streamlit re-entrancy.
2. Else try `st.secrets["database"]["url"]`.
3. Else show clear error (current message, updated to mention `LOCAL_SQLITE`).

`init_db()` / `get_db()` unchanged in responsibility: create tables, session scope. SQLite uses the same SQLAlchemy models.

### Demo + auth

- Recommended local combo: `LOCAL_SQLITE=True` + `DEMO_MODE=True`.
- Existing DEMO_MODE path in `main.py` (inject `DEMO_USER`, disable writes in UI, OCR mock) stays.
- Do not invent a second auth stack for SQLite in this PR.

### Tests

- `test_auth.py`: if secrets missing → `pytest.skip` (or mock minimal secrets) — **never** `sys.exit`.
- Existing unit tests already use in-memory SQLite via `conftest.py`; leave that path.
- Add a small unit test for URL resolution: `LOCAL_SQLITE=True` → sqlite URL without requiring secrets.

### Docs (minimal)

- Short subsection in `docs/SETUP_GUIDE.md` (or README Quick Start): copy `.env.example` → `.env`, set `LOCAL_SQLITE=True` and `DEMO_MODE=True`, `streamlit run main.py`, open `http://localhost:8501`.
- No new architecture essay.

## Issue + PR packaging

- **Issue** (English, no-ai-slop): demo 303/auth gate; keep-alive action deleted; clone blocked on secrets; `test_auth` hard-exit; proposal = local SQLite bootstrap.
- **PR** branch `feat/local-sqlite-bootstrap`: implements this design; `Fixes #N`; DoD below.

## Success criteria (DoD)

1. With only `.env` (`LOCAL_SQLITE=True`, `DEMO_MODE=True`, demo user defaults) and **no** real `secrets.toml`, `streamlit run main.py` serves the demo UI.
2. `pytest` exits 0 without a real Supabase `secrets.toml`.
3. With `LOCAL_SQLITE` unset and valid Postgres secrets, behavior matches current main (no regression path).
4. Diff stays surgical: core URL resolution, example files, test_auth fix, one resolution unit test, short setup note.

## Risks

- SQLite type quirks vs Postgres (JSON, UUID strings) — models already use String user_id; validate with existing unit tests + one smoke run.
- Accidental `LOCAL_SQLITE=True` on Cloud — document as local-only; Cloud should set secrets, not this flag.
