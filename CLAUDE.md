# CLAUDE.md

This repository follows the `wellmanifest/new-project` policy-as-code standard.

- Repository: `wellmanifest/apx`
- Purpose: Standard for Autonomous Application Packs (APX) composition and lifecycle
- Standard ID: `urn:wellmanifest:spec:apx:v1`

## Agent Rules
1. Allocate tickets only through `./project/new-ticket.sh`.
2. Work in ticket worktrees. Never commit directly to `main`.
3. Preserve strict standards delegation and zero duplication.
4. Verify tests with `pytest -v`.
