FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY shared/ ./shared/
COPY constants.py ./
COPY inference_service/ ./inference_service/

RUN uv sync --frozen --no-dev

CMD ["uv", "run", "uvicorn", "inference_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
