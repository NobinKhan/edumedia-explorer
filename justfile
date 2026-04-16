set shell := ["bash", "-cu"]

dev-setup:
    @if [ ! -f .env ]; then cp .env.example .env && echo "Created .env from .env.example"; else echo ".env already exists; skipping copy"; fi
    docker compose up -d db

install:
    uv sync

dev:
    -@port="${PORT:-8000}"; \
    while ! uv run python -c 'import socket,sys; s=socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(("127.0.0.1", int(sys.argv[1]))); s.close()' "$port" >/dev/null 2>&1; do \
        port="$((port+1))"; \
    done; \
    echo "Using port ${port}"; \
    uv run fastapi dev app/main.py --port "$port"

run:
    -@port="${PORT:-8000}"; \
    while ! uv run python -c 'import socket,sys; s=socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(("127.0.0.1", int(sys.argv[1]))); s.close()' "$port" >/dev/null 2>&1; do \
        port="$((port+1))"; \
    done; \
    echo "Using port ${port}"; \
    uv run fastapi run app/main.py --port "$port"

test:
    -@uv run pytest

seed:
    -@uv run python -m app.seed_cli

lint:
    -@uv run ruff check .

format:
    -@uv run ruff format .

check:
    -@uv run ruff format --check .
    -@uv run ruff check .
    -@uv run pytest

clean:
    -@rm -rf .pytest_cache .ruff_cache .mypy_cache dist build
