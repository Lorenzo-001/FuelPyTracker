# FuelPyTracker — agent brief (CLAUDE.md)

Concise rules for agents working in this repo. [`AGENTS.md`](./AGENTS.md) is a stub pointer (Cursor loads it); edit this file only.

## Product (V2.0)

- Hub **data-driven** per gestione veicolo: rifornimenti, consumi (km/L), manutenzioni/scadenze, promemoria, import/export, libretto PDF, Smart OCR scontrini.
- Stack: **FastAPI (Python 3.12)** backend + **React 19 / TypeScript / Vite / Tailwind** frontend + **SQLAlchemy** (Dual DB: SQLite locale o Supabase Postgres RLS) + Vision OCR.
- UI copy: Italian (README e stringhe utente). Demo pubblica: `DEMO_MODE=True` (read-only, utente fittizio, AI mock).

## Orientation

1. Backend: `backend/` → `src/api` (router modulari), `src/services`, `src/models`, `src/database`. Entry: `backend/src/main.py`.
2. Frontend: `frontend/` → `src/components`, `src/hooks`, `src/context`, `src/pages`. Entry: `frontend/src/main.tsx`.
3. Docs: `docs/functional/`, `docs/architecture/`, `docs/technical/`, `docs/archive/`.
4. Env: `.env` da `.env.example`. Mai committare credenziali o file `.env`.
5. Tests: `backend/tests/` con **pytest** (unit ed e2e); frontend con `npm run lint` (`oxlint`) e `npm run build` (`tsc`).

## Creative / multi-step work (Superpowers)

For new features or non-trivial UX (not typo fixes):

1. **Brainstorm** — clarify scope; get approval before coding.
2. **Design** — store the approved design in **claude-mem** (project `FuelPyTracker`, type `decision`). Formal spec/plan MD only if the user explicitly asks.
3. **Implement** task-by-task (TDD where logic exists); verify; PR.

Do not skip to implementation on ambiguous “build X” requests.

## Git & PRs (Hard Rules)

1. Branch from updated `main`: `feat/…`, `fix/…`, or `docs/…`. One concern per PR.
2. Before opening/asking to merge: `pytest` and frontend typecheck (`tsc -b`).
3. **Open PRs only on** https://github.com/Lorenzo-001/FuelPyTracker/pulls  
   (`gh pr create --repo Lorenzo-001/FuelPyTracker --head Never-lab:<branch> --base main`).  
   Push branches to `origin` (`Never-lab/FuelPyTracker`). Never target `Never-lab/.../pulls` as the review host.
4. Wait for CI green; do not merge while red/pending.
5. Never push straight to `main`. No force-push to `main`.
6. Commit only when the user asks (or explicitly says “vai / fai commit / apri PR”).
7. **Do not commit:** `.superpowers/sdd/*`, local session diffs/reports, secrets, `.env`, `_cantiere/`.
8. Never `Co-authored-by: Cursor`.

## Code & tests

- Backend: Prefer pure helpers and modular services in `backend/src/services` — cover with pytest.
- Frontend: Ensure state synchronization via TanStack Query and clean component separation; 0 linter warnings.
- Keep diffs surgical; no drive-by refactors.
- Match existing patterns (SQLAlchemy session usage, Supabase auth / SQLite local, demo-mode guards).
- Do not weaken RLS or demo write-locks.

## Language

- If the user writes in Italian, respond in Italian (unless they ask otherwise).
- Code identifiers stay English; user-visible strings Italian.
- **PR / issue text on Lorenzo-001:** Italian (title, body, public review comments). Commit messages stay English.

## Execution preferences

- Default: work on a feature branch in this checkout.
- Prefer one clear clarifying question over speculative multi-path implementation when scope is huge.
- If the design is already approved in this chat (or the user says «ok / procedi / implementa come approvato»): skip Superpowers brainstorm and implement from this thread.

## Shared agent block (Never-lab)

- Chat: Italian. Code: English. **FuelPyTracker:** UI strings Italian; **PR/issue su Lorenzo-001 in italiano**; commit messages English.
- Before posting PR bodies or issue comments: skill **`no-ai-slop`**.
- Never `Co-authored-by: Cursor`.
- PRs: only https://github.com/Lorenzo-001/FuelPyTracker/pulls (`--repo Lorenzo-001/FuelPyTracker`, head `Never-lab:<branch>`).