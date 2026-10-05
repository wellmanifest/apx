# GEMINI.md

This repository follows the `wellmanifest/new-project` policy-as-code standard.
This file is the Gemini / Antigravity entry; the same rules are in `AGENTS.md` and `CLAUDE.md`.

Fail-closed. Do not write code until this contract is followed:

1. Read `AGENTS.md` and `README.md`.
2. Allocate tickets only through `./project/new-ticket.sh`. Never copy `project/ticket-*`.
3. Work on a branch or worktree whose name contains `ticket-NNN`. Never commit on `main` or a dirty primary checkout.
4. Stay inside that ticket's `intent.json` `allowedPaths`.
5. Maintain strict composition with companion standards: `wellmanifest/{docs,usermanual,logs,ssot,wellman,new-project,uriprocess}`.
