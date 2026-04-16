# EduMedia Author

FastAPI service for authoring **hierarchical subject detail pages** (category → sub-category → sub-sub-category → page), **rich HTML bodies**, and **annotations** (text, image, audio, video, YouTube, link) anchored to a single DOM text node, with **published** interactive HTML and a lightweight **Jinja2 + vanilla JS** public view.

Full product intent and acceptance criteria live in [`NewWorkPlan.md`](NewWorkPlan.md). Implementation status, backlog, and handoff live under [`tracker/`](tracker/).

## Stack

- Python **3.12+** (see `tracker/decisions.md` for the brief’s 3.14.4 note on this machine)
- FastAPI, uvicorn, SQLAlchemy, SQLite (default DB under `data/edumedia.db`), nh3 + BeautifulSoup for sanitization/rendering
- uv, just, pytest, ruff

## Quickstart

```bash
just install
just seed
just dev
```

Open the URL printed by the dev server. API docs: `/docs`. Landing: `/`.

## Useful routes

| Route | Purpose |
|-------|---------|
| `GET /` | Landing |
| `GET /healthz` | Liveness JSON |
| `GET /api/v1/meta` | API meta |
| `GET /docs` | OpenAPI UI |
| `GET /editor` | Editor shell (UI in progress) |
| `GET /pages/{slug}` | Published subject page (404 if not `published`) |

## Configuration

See [`.env.example`](.env.example). Optional: `DATABASE_URL`, `MEDIA_UPLOAD_DIR`, `SQLALCHEMY_ECHO`.

### SQLite auto-reset (demos only)

If `SQLITE_AUTO_RESET_SECONDS` is set to a positive value **and** you use SQLite, the app will **drop and recreate all tables** on that interval (e.g. `3600` for hourly). This prevents unbounded growth in throwaway environments. It is **destructive**—leave unset (`0`, the default) for normal use. After each reset, **`seed()` runs by default** (same as `just seed`); set `SQLITE_AUTO_RESET_SEED=false` to leave the database empty instead.

## Commands

| Command | Purpose |
|---------|---------|
| `just install` | `uv sync` dependencies |
| `just seed` | Seed sample hierarchy + one published page |
| `just dev` | Dev server with reload |
| `just run` | Production-style local server |
| `just test` | Pytest |
| `just lint` | Ruff check |
| `just format` | Ruff format |
| `just check` | Format check + lint + tests |
| `just clean` | Drop local caches |

## Tests

```bash
just test
```

Integration tests use an isolated in-memory SQLite engine via `tests/conftest.py` (dependency override for `get_session`).

## API quick examples

Create hierarchy + page (JSON):

```bash
curl -sS -X POST localhost:8000/api/v1/categories/ \
  -H 'content-type: application/json' \
  -d '{"name":"Science","slug":"science"}'
```

Publish a page (renders interactive HTML):

```bash
curl -sS -X POST localhost:8000/api/v1/subject-pages/1/publish
```
