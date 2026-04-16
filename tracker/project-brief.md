# EduMedia Author — project brief

## Goal

Deliver a FastAPI backend and light Jinja/vanilla-JS frontend for authoring **hierarchical subject details pages** with Word-like formatting and **annotations** (text, image, audio, video, YouTube, link) on selected text, plus **public interactive rendering** (modals).

## Scope

- Category → sub-category → sub-sub-category → subject page hierarchy (CRUD).
- Subject pages: title, summary, rich HTML body, draft/publish, preview, rendered output.
- Annotations CRUD tied to pages; media assets API with local file storage.
- REST API under `/api/v1`, health and meta endpoints.
- Editor and public page web routes (incremental UI delivery per backlog).
- SQLite + SQLAlchemy, services + repositories, tests, deployment notes, tracker handoff.

## Non-goals

- Authentication and authorization (explicitly out of scope for MVP).
- Cloud object storage, collaborative editing, revision history.
- Heavy SPA frameworks.

## Locked stack

- FastAPI, uv, just, Jinja2, vanilla JS, SQLite, SQLAlchemy, pytest, ruff.
- Python: **>=3.12,<3.16** on current dev hosts (see `decisions.md` for 3.14.4 note).

## Acceptance criteria

See `NewWorkPlan.md` Definition of done; tracker `qa-checklist.md` mirrors executable checks.
