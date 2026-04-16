# syntax=docker/dockerfile:1.7
#
# Multistage image: Wolfi (Chainguard) build + minimal Wolfi runtime, uv for deps.
# Pattern aligned with basmalahub-commerce Saleor backend Dockerfile (wolfi-base + uv binary).
#
# Python: install Wolfi’s newest stable line (bump `python-3.x*` package names when Wolfi
# promotes a newer series; there is no unversioned “latest” APK).

## ---------------------------------------------------------------------------------- ##
## -------------------------------- Build ------------------------------------------- ##
## ---------------------------------------------------------------------------------- ##

FROM cgr.dev/chainguard/wolfi-base:latest AS build

ENV UV_COMPILE_BYTECODE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add --no-cache \
    build-base \
    ca-certificates \
    python-3.14 \
    python-3.14-dev \
    linux-headers \
    zlib-dev

COPY pyproject.toml uv.lock README.md ./
COPY app ./app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

## ---------------------------------------------------------------------------------- ##
## -------------------------------- Runtime ----------------------------------------- ##
## ---------------------------------------------------------------------------------- ##

FROM cgr.dev/chainguard/wolfi-base:latest AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH=/app/.venv/bin:$PATH

RUN set -eux \
    && apk update \
    && apk upgrade \
    && apk add --no-cache ca-certificates python-3.14 \
    && apk cache clean \
    && addgroup -S app \
    && adduser -S -D -H -G app -s /sbin/nologin app \
    && mkdir -p /app/data/uploads \
    && chown -R app:app /app

USER app
WORKDIR /app

COPY --from=build --chown=app:app /app/.venv /app/.venv
COPY --from=build --chown=app:app /app/app /app/app

EXPOSE 8000

LABEL org.opencontainers.image.title="edumedia-explorer" \
    org.opencontainers.image.description="EduMedia Author — FastAPI; SQLite by default, PostgreSQL via DATABASE_URL" \
    org.opencontainers.image.source="https://github.com/NobinKhan/edumedia-explorer"

# Same entrypoint style as `just run` (production: no reload, listens on 0.0.0.0 by default).
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
