# Architecture and toolchain decisions

## 2026-04-15 — Python runtime version

- **Decision:** Target `requires-python = ">=3.12,<3.16"` and local `.python-version` `3.12.3` instead of Python 3.14.4 from the brief.
- **Reason:** The development host provides Python 3.12.3; Python 3.14.4 is not installed, so `uv sync` and `just check` would fail.
- **Alternatives considered:** Install Python 3.14.4 via pyenv/uv python pin (deferred; can align later when available).
- **Consequences:** Ruff `target-version` is `py312`. Code avoids 3.14-only syntax.

## 2026-04-15 — just version

- **Decision:** Document host `just` 1.21.0; keep `justfile` compatible with 1.21+.
- **Reason:** NewWorkPlan specified 1.49.0; environment reports 1.21.0.
- **Alternatives considered:** Upgrading just on the host (user-managed).
- **Consequences:** No just 1.49-only features used.

## 2026-04-15 — uv version

- **Decision:** Accept uv 0.11.6 (host) vs brief 0.11.5; no feature delta required.
- **Reason:** Patch-level drift; lockfile remains authoritative.

## 2026-04-15 — HTML rendering stack

- **Decision:** Use `beautifulsoup4` for `render_service` (plain-text offsets → wrapped spans) and `nh3` for HTML sanitization on public output.
- **Reason:** Reliable tree manipulation without a full browser; nh3 is a maintained HTML5 sanitizer (Rust-backed).
- **Alternatives considered:** bleach (older API); manual `html.parser` (too error-prone for wrapping).
- **Consequences:** Two small dependencies focused on safety and correctness.

## 2026-04-15 — `app/api/v1/annotations` module name

- **Decision:** Name the standalone annotation router module `annotation_routes.py` instead of `annotations.py`.
- **Reason:** `from __future__ import annotations` in `app/api/v1/__init__.py` binds the name `annotations`, which breaks `from app.api.v1 import annotations` (import resolves to the future feature, not the submodule).
- **Alternatives considered:** Dropping `from __future__ import annotations` from `__init__.py` only; aliasing imports.
- **Consequences:** API paths remain `/api/v1/annotations/...`.

## 2026-04-15 — Legacy demo API

- **Decision:** Remove `/api/content/{content_id}` in favor of `/api/v1` and database-backed resources.
- **Reason:** NewWorkPlan requires dynamic APIs and SQLite-backed models; the in-memory registry conflicts with that direction.
- **Consequences:** Tests and README point at v1 APIs and new web routes.
