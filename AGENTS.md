# Agent notes — FuelPyTracker

Canonical brief: [`CLAUDE.md`](./CLAUDE.md). Prefer editing that file for long-lived rules. This file is loaded by Cursor — keep **hard constraints** here too.

## GitHub PRs (hard)

- **Canonical PR host:** https://github.com/Lorenzo-001/FuelPyTracker/pulls  
  Open every PR with `--repo Lorenzo-001/FuelPyTracker` (base usually `main`).
- Head branch lives on the working fork `Never-lab/FuelPyTracker` (`origin`). Example:  
  `gh pr create --repo Lorenzo-001/FuelPyTracker --head Never-lab:<branch> --base main`
- **Do not** open or leave review PRs on `Never-lab/FuelPyTracker/pulls` (that repo is the push remote only).
- Do not `git push` to `Lorenzo-001/FuelPyTracker` unless you have write access; use cross-repo PRs from `Never-lab:` heads.
- One concern per PR. Stacked work: separate branches/PRs on Lorenzo-001; note dependency on the parent PR in the body.
- **Lingua PR (titolo + body + commenti di review pubblici):** italiano. Codice, identificatori e commit message restano in inglese.

## Language (chat vs repo)

- Chat con l’utente: italiano (se scrive in italiano).
- UI prodotto: italiano.
- Commit message: inglese (stile repo).
- Issue/PR su Lorenzo-001: italiano.
