# Local SQLite bootstrap — Implementation Plan

> **For agentic workers:** execute task-by-task. Checkboxes track progress.

**Goal:** Opt-in `LOCAL_SQLITE` so clone → `.env` → `streamlit run` / `pytest` work without Supabase secrets.

**Architecture:** Resolve DB URL from env before `st.secrets`; soft-fail OpenAI secrets at import; skip live auth tests without secrets.

**Tech Stack:** SQLAlchemy SQLite, python-dotenv, pytest, Streamlit.

## Global Constraints

- Explicit `LOCAL_SQLITE=True` only (no silent fallback).
- Surgical diffs; no auth rewrite; DEMO_MODE path unchanged.
- DoD: UI boots with LOCAL_SQLITE+DEMO_MODE; pytest green without real secrets.toml.

---

### Task 1: URL resolution + core engine
### Task 2: Soft OpenAI secrets + dotenv in main
### Task 3: Fix test_auth skip + URL unit test
### Task 4: Examples + SETUP/README note
### Task 5: Issue + PR
