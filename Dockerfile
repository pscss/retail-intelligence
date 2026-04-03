FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY constants.py ./
COPY shared/ ./shared/
COPY data_service/ ./data_service/
COPY inference_service/ ./inference_service/
COPY retrieval_service/ ./retrieval_service/
COPY gateway_service/ ./gateway_service/

RUN uv sync --frozen --no-dev
RUN uv run pip install torch --index-url https://download.pytorch.org/whl/cpu --force-reinstall

ARG SERVICE
ARG PORT

ENV SERVICE=${SERVICE}
ENV PORT=${PORT}

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["uv run uvicorn ${SERVICE}.main:app --host 0.0.0.0 --port ${PORT}"]
