# QA checklist

## Automated

- [ ] `just check` (format check, ruff, pytest)
- [ ] `uv sync` succeeds on pinned Python

## Manual — UI

- [ ] `/` loads landing
- [ ] `/editor` loads dashboard and lists pages
- [ ] `/editor/pages/new` can create a draft
- [ ] `/editor/pages/{id}` can edit, preview, publish
- [ ] `/pages/{slug}` shows published page with modal accessibility (Escape, overlay, focus, Enter/Space activation)

## Manual — API

- [ ] `GET /healthz` → 200
- [ ] `GET /api/v1/meta` → JSON meta
- [ ] Category → subject page CRUD happy paths via HTTP client or OpenAPI `/docs`
- [ ] Annotation create fails when selection crosses element boundaries
- [ ] Media upload works via `POST /api/v1/media-assets/upload`

## Deployment

- [ ] Production settings documented (env vars, database path)
- [ ] Live URL recorded in README when `T026` done
