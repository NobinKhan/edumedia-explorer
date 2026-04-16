# Handoff

## What is done

- Tracker folder and protocol files; `PROJECT_SPEC.md`.
- SQLite + SQLAlchemy models for hierarchy, pages, annotations, media.
- `/api/v1` routers: categories through media-assets; publish/preview/rendered; `GET /api/v1/meta`; `GET /healthz` on the web router.
- `render_service` (BeautifulSoup span wrap + nh3 sanitize); validation for hierarchy, slugs, annotation offsets (single text node), YouTube hosts, type-specific fields.
- Placeholder editor routes (`/editor`, `/editor/pages/new`, `/editor/pages/{id}`) and public `GET /pages/{slug}` with modal JSON + `app.js` annotation triggers.
- Tests: health, home, categories CRUD, subject page publish + rendered (in-memory SQLite via dependency override).

## What remains

- Backlog T014–T027: full editor UX, more tests (`test_render_api`, annotations edge cases), seed data, QA pass, README/deployment polish, live deploy.

## Risks

- Plain-text offsets vs rich HTML: edge cases when annotations span complex markup; covered partially in `render_service` and validation.
- No authentication: public write APIs are appropriate only for demos; lock down before any real deployment.

## What not to casually change

- `tracker/session-log.md` is append-only.
- Slug and hierarchy validation rules (breaking them loses data integrity).

## Resume command

```bash
cd /media/nobinkhan/files/projects/backends/edumedia-explorer && just install && just check && just seed && just dev
```

## Resume file

`app/main.py` (application wiring and router inclusion)

## Deployment notes

- Docker: `Dockerfile` runs `uvicorn app.main:app` on port 8000.
- Render: `render.yaml` included as a starting point; adjust plan/env as needed.
