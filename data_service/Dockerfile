FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY shared/ ./shared/
COPY constants.py ./
COPY data_service/ ./data_service/

# Install dependencies
RUN uv sync --frozen --no-dev

# Run the service
CMD ["uv", "run", "uvicorn", "data_service.main:app", "--host", "0.0.0.0", "--port", "8003"]
