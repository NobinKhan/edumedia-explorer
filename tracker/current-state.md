# Current state

- **Branch:** (local default; not pinned by agent)
- **Completed tasks:** T001–T025 (toolchain, tracker, SQLite models, `/api/v1` CRUD, editor dashboard + page editor, formatting toolbar, annotation flow, preview/publish, seed, tests, README, Docker/Render config).
- **Current task:** T027 — final polish + handoff readiness.
- **Blockers:** T026 (deployment) blocked pending hosting access/credentials.
- **Test status:** Last run `just check` — all green (8 pytest tests).
- **Deployment status:** Not deployed; `Dockerfile` + `render.yaml` present.
- **Repo cleanliness:** `NewWorkPlan.md` may remain untracked as reference; otherwise working tree dirty until commit.
- **Exact next command:** `just seed && just dev` (then open `/editor` and `/pages/photosynthesis`)
- **Exact next file to edit:** `tracker/handoff.md`
