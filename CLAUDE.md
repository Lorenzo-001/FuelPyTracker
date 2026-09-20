# FuelPyTracker — agent brief (CLAUDE.md)

Concise rules for agents working in this repo. [`AGENTS.md`](./AGENTS.md) is a stub pointer (Cursor loads it); edit this file only.

## Product

- Hub **data-driven** per gestione veicolo: rifornimenti, consumi (km/L), manutenzioni/scadenze, import/export, OCR scontrini (opzionale).
- Stack: **Streamlit** + **Supabase** (Auth + Postgres RLS) + **SQLAlchemy**; OCR opzionale via OpenAI GPT-4o Vision.
- UI copy: Italian (README e stringhe utente). Demo pubblica: `DEMO_MODE=True` (read-only, utente fittizio, OpenAI mock).

## Orientation

1. Entry: [`main.py`](./main.py) → `src/ui`, `src/auth`, `src/database`, `src/services`.
2. Secrets: `.streamlit/secrets.toml` (from `.streamlit/secrets.toml.example`); env: `.env` from `.env.example`. Never commit secrets.
3. Tests: `tests/unit/` with **pytest**.
4. Skill logo/IP: `.cursor/skills/ip-as-logo`.

## Creative / multi-step work (Superpowers)

For new features or non-trivial UX (not typo fixes):

1. **Brainstorm** — clarify scope; get approval before coding.
2. **Design** — store the approved design in **claude-mem** (project `FuelPyTracker`, type `decision`). Formal spec/plan MD only if the user explicitly asks.
3. **Implement** task-by-task (TDD where logic exists); verify; PR.

Do not skip to implementation on ambiguous “build X” requests.

## Git & PRs

1. Branch from updated `main`: `feat/…`, `fix/…`, or `docs/…`. One concern per PR.
2. Before opening/asking to merge: `pytest` (and any lint the repo already uses).
3. **Open PRs only on** https://github.com/Lorenzo-001/FuelPyTracker/pulls  
   (`gh pr create --repo Lorenzo-001/FuelPyTracker --head Never-lab:<branch> --base main`).  
   Push branches to `origin` (`Never-lab/FuelPyTracker`). Never target `Never-lab/.../pulls` as the review host.
4. Wait for CI green; do not merge while red/pending.
5. Never push straight to `main`. No force-push to `main`.
6. Commit only when the user asks (or explicitly says “vai / fai commit / apri PR”).
7. **Do not commit:** `.superpowers/sdd/*`, local session diffs/reports, secrets, `.env`, `.streamlit/secrets.toml`.
8. Never `Co-authored-by: Cursor`.

## Code & tests

- Prefer pure helpers in `src/services` / logic modules — cover with pytest; Streamlit UI wiring verified by running the app when needed.
- Keep diffs surgical; no drive-by refactors.
- Match existing patterns (SQLAlchemy session usage, Supabase auth, demo-mode guards).
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
- Prefer `ponytail` + Karpathy; Superpowers only when the slice is new/ambiguous. No default `docs/superpowers/specs|plans` MD — decisions in chat/claude-mem (liquidazi style).
- PRs: only https://github.com/Lorenzo-001/FuelPyTracker/pulls (`--repo Lorenzo-001/FuelPyTracker`, head `Never-lab:<branch>`).