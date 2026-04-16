# EduMedia Author

FastAPI service for authoring **hierarchical subject detail pages** (category → sub-category → sub-sub-category → page), **rich HTML bodies**, and **annotations** (text, image, audio, video, YouTube, link) anchored to a single DOM text node, with **published** interactive HTML and a lightweight **Jinja2 + vanilla JS** public view.

## Stack

- Python **3.12+** (local dev); container builds track Wolfi’s current Python line (see `Dockerfile`).
- FastAPI, uvicorn, SQLAlchemy, **SQLite** by default (`data/edumedia.db`), **PostgreSQL** via `DATABASE_URL` and **psycopg** (see [`.env.example`](.env.example) and [`docker-compose.yml`](docker-compose.yml)).
- nh3 + BeautifulSoup for sanitization/rendering
- uv, just, pytest, ruff

### Prerequisites (install tools)

- **uv** (Python package manager): [Installation](https://docs.astral.sh/uv/getting-started/installation/)
- **just** (command runner): [Installation](https://github.com/casey/just#installation)

## Quickstart

### Local (uv + just)

First-time setup (creates `.env` from [`.env.example`](.env.example) if missing and starts the Compose **Postgres** service only):

```bash
just dev-setup
```

For local development, set `ENVIRONMENT=development` in `.env` (see [Configuration](#configuration)); the default when unset is production-like behavior.

```bash
just install
just dev
```

On startup the app ensures tables exist with SQLAlchemy `create_all` (additive only—it never drops tables) and runs the idempotent demo `seed()` once per process start. You can still run `just seed` manually if you want the same bootstrap without restarting the server.

Open the URL printed by the dev server. API docs: `/docs`. Landing: `/`.

### Docker Compose (Chainguard PostgreSQL + app image)

Requires [Docker Compose](https://docs.docker.com/compose/) v2.

To bring the stack up manually:

```bash
docker compose up --build
```

To run **Ruff format, format check, lint, Pytest**, then **`docker compose build`** and start the stack in the background, use **`just test`** (needs Docker; first image build can take several minutes). For the same Python checks **without** Docker, use **`just check`** (see [Commands](#commands) and [Tests](#tests)).

- **Database**: [`cgr.dev/chainguard/postgres:latest`](https://images.chainguard.dev/directory/image/postgres/overview) with a named volume for data (optional `ports` mapping is commented in the compose file if you need host access).
- **App**: builds the [`Dockerfile`](Dockerfile); connects with `postgresql+psycopg://edumedia:edumedia@db:5432/edumedia`.
- **Port**: the app is published on **host `8001` → container `8000`** by default (`WEB_PORT` is configurable) so it does not collide with a local dev server on `8000`.

Examples (default compose port):

```bash
curl -sS http://127.0.0.1:8001/healthz
# Then open http://127.0.0.1:8001/docs in a browser
```

Use `WEB_PORT=8000 docker compose up --build` if you want the app on `8000` instead.

Stop and remove containers: `docker compose down`. To wipe the Postgres volume as well: `docker compose down -v`.

### Resetting env files and the Compose stack

**`just rm`** is a destructive local reset: it deletes `.env` and any other root-level `.env.*` files **except** [`.env.example`](.env.example), then runs `docker compose down -v --remove-orphans --rmi local` (stops the project, removes volumes and project networks, and removes **locally built** images for this Compose project). Use it when you want a clean slate before `just dev-setup` or a fresh `docker compose up --build`. It does not remove arbitrary Docker images from other projects.

## Useful routes

| Route | Purpose |
|-------|---------|
| `GET /` | Landing |
| `GET /healthz` | App status plus `database` kind and `database_status` (`connected` or error); HTTP **503** if the DB check fails |
| `GET /api/v1/meta` | API meta |
| `GET /docs` | OpenAPI UI |
| `GET /editor` | Editor dashboard |
| `GET /pages/{slug}` | Published subject page (404 if not `published`) |

## Dockerfile and container layout

This repository’s [`Dockerfile`](Dockerfile) is intentionally boring and security-oriented rather than clever:

- **Multistage Wolfi (Chainguard)**: the **build** stage installs compilers, `linux-headers`, and `python-*-dev` so native wheels (for example SQLAlchemy’s greenlet) can compile. The **runtime** stage installs only `ca-certificates` and the Python runtime—no C toolchain, no package manager in the final layer you ship.
- **Pinned, auditable dependencies**: the official [`ghcr.io/astral-sh/uv:latest`](https://github.com/astral-sh/uv/pkgs/container/uv) image supplies `uv`; `uv sync --frozen --no-dev` installs exactly what [`uv.lock`](uv.lock) records. `UV_COMPILE_BYTECODE=1` precompiles bytecode for faster cold starts.
- **Least privilege**: the app runs as a dedicated non-root **`app`** user; only `/app/data` (and the copied application tree) is required at runtime.
- **Small final artifact**: the runtime image copies **only** `.venv` and `app/`—no tests, git metadata, or dev dependency groups—so the deployed surface stays small and easy to scan.
- **Same entry style as production locally**: `CMD` uses `fastapi run app/main.py`, aligned with **`just run`** (no dev reload; suitable defaults for serving in a container).
- **Database-agnostic image**: the same image works with the default **SQLite** file URL or **PostgreSQL** when `DATABASE_URL` uses the **`postgresql+psycopg://`** scheme (see Compose and `.env.example`).

That combination—Wolfi base, frozen uv lock, split stages, non-root user—is a practical default when you want **reproducible builds** and a **reduced dependency footprint** without maintaining a bespoke distro image.

## Configuration

See [`.env.example`](.env.example). **`ENVIRONMENT`**: omit it for production-like defaults (`production`). Set **`ENVIRONMENT=development`** in `.env` for local work (for example the landing page dev hint). Optional: `DATABASE_URL`, `MEDIA_UPLOAD_DIR`, `SQLALCHEMY_ECHO`.

**Schema and demo data:** at startup the service calls `create_all` with `checkfirst=True` (creates missing tables only; no migrations and no `DROP`). It then runs the same idempotent demo seed as `just seed`. Destructive resets are limited to the optional SQLite demo interval described below.

For **PostgreSQL**, set `DATABASE_URL` to a SQLAlchemy URL using **psycopg v3**, for example:

`postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME`

Managed hosts (Fly Postgres, Lympg, and similar) often supply a bare `postgresql://` or legacy `postgres://` string without a `+driver` suffix. That form is accepted here and rewritten to **`postgresql+psycopg://`** automatically so SQLAlchemy uses the installed psycopg v3 driver instead of the default psycopg2 dialect.

The bundled [`docker-compose.yml`](docker-compose.yml) wires this for the `web` service against the `db` service hostname.

### SQLite auto-reset (demos only)

If `SQLITE_AUTO_RESET_SECONDS` is set to a positive value **and** you use SQLite, the app will **drop and recreate all tables** on that interval (e.g. `3600` for hourly). This prevents unbounded growth in throwaway environments. It is **destructive**—leave unset (`0`, the default) for normal use. After each reset, **`seed()` runs by default** (same as `just seed`); set `SQLITE_AUTO_RESET_SEED=false` to leave the database empty instead.

## Commands

| Command | Purpose |
|---------|---------|
| `just dev-setup` | Create `.env` from `.env.example` if missing; start Compose Postgres (`db`) |
| `just install` | `uv sync` dependencies |
| `just seed` | Same as startup: ensure tables + idempotent demo seed |
| `just dev` | Dev server with reload |
| `just run` | Production-style local server |
| `just test` | Format, format check, lint, pytest, then `docker compose build` and `docker compose up -d` |
| `just lint` | Ruff check |
| `just format` | Ruff format |
| `just check` | Format check + lint + tests (no Docker) |
| `just rm` | Remove `.env` and other `.env.*` except `.env.example`; Compose down with volumes, orphans, and local built images |
| `just clean` | Drop local caches |
| `docker compose up --build` | App container + Chainguard PostgreSQL (see [`docker-compose.yml`](docker-compose.yml)) |

## Tests

**Full pipeline (Python + Docker):**

```bash
just test
```

Runs, in order: `ruff format`, `ruff format --check`, `ruff check`, `pytest`, then `docker compose build` and `docker compose up -d`. Fail-fast: the first failing step stops the recipe. Ensure Docker is running; the first run may download base images and build the `web` image.

**Python only (CI-friendly, no Docker):**

```bash
just check
```

Runs format check, lint, and tests—same checks as the first half of `just test`, without Compose.

Integration tests use an isolated in-memory SQLite engine via `tests/conftest.py` (dependency override for `get_session`). The `/healthz` route still uses the process-wide engine from [`app/db.py`](app/db.py) (your configured `DATABASE_URL` or default SQLite file).

## API quick examples

Replace `localhost:8000` with `localhost:8001` if you are using **default** `docker compose` (the app is mapped to host port **8001** unless you set `WEB_PORT`).

Create a category:

```bash
curl -sS -X POST localhost:8000/api/v1/categories/ \
  -H 'content-type: application/json' \
  -d '{"name":"Science","slug":"science","description":"STEM"}'
```

Create nested levels, a draft page, then publish (adjust IDs from the JSON responses if you already have data):

```bash
curl -sS -X POST localhost:8000/api/v1/sub-categories/ \
  -H 'content-type: application/json' \
  -d '{"category_id":1,"name":"Physics","slug":"physics","description":""}'
curl -sS -X POST localhost:8000/api/v1/sub-sub-categories/ \
  -H 'content-type: application/json' \
  -d '{"sub_category_id":1,"name":"Mechanics","slug":"mechanics","description":""}'
curl -sS -X POST localhost:8000/api/v1/subject-pages/ \
  -H 'content-type: application/json' \
  -d '{"category_id":1,"sub_category_id":1,"sub_sub_category_id":1,"title":"Motion","slug":"motion","summary":"","raw_content":"<p>Hello</p>"}'
curl -sS -X POST localhost:8000/api/v1/subject-pages/1/publish
```

Preview with a body override (`POST`, not `GET`):

```bash
curl -sS -X POST localhost:8000/api/v1/subject-pages/1/preview \
  -H 'content-type: application/json' \
  -d '{"raw_content":"<p>Preview only</p>"}'
```
