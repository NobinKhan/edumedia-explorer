# Interactive Teaching Platform (FastAPI)

This repo implements the **Interactive Teaching Platform** hiring-task demo using **FastAPI + Jinja2 + static assets**.

## Features
- Two-column responsive page (stacks on mobile)
- Media example controls (Text, Image, Audio, MyVid, YouTube)
- Interactive article terms that open the same modal
- Accordion sidebar with inline interactive triggers
- Central content registry backing `/api/content/{content_id}`
- Accessible modal: Escape/overlay/close button, focus trap and focus restore

## Requirements
- `uv` installed
- `just` installed

## Quickstart

```bash
just install
just dev
```

Then open the URL printed by the server.

## Routes
- `GET /`: homepage (server-rendered HTML)
- `GET /healthz`: health check JSON
- `GET /api/content/{content_id}`: content registry lookup JSON

## Commands
- `just install`: sync dependencies
- `just dev`: run dev server (reload)
- `just run`: run production-style server
- `just format`: format code
- `just lint`: lint code
- `just test`: run tests
- `just check`: format-check + lint + tests
- `just clean`: remove caches
