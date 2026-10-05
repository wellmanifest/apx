# AGENTS.md

This repository follows the `wellmanifest/new-project` policy-as-code standard.

- Repository: `wellmanifest/apx`
- Purpose: Standard for Autonomous Application Packs (APX) composition and lifecycle
- Standard ID: `urn:wellmanifest:spec:apx:v1`

## Autonomous Agent Instructions

1. **Ticket Allocation**: All changes must be allocated through `./project/new-ticket.sh`.
2. **Worktree Isolation**: Work exclusively within isolated worktrees (`.worktrees/ticket-*`). Never commit directly to `main`.
3. **Zero Duplication Principle**: Do not duplicate standards. APX is a composition pack that delegates to:
   - `wellmanifest/docs` for documentation documents
   - `wellmanifest/usermanual` for CQRS API surfaces
   - `wellmanifest/logs` for JSONL event logging
   - `wellmanifest/ssot` for single source of truth configurations
   - `wellmanifest/wellman` for cryptographic execution receipts
4. **Verification**: Run `pytest -v` to ensure all conformance checks and tests pass.
