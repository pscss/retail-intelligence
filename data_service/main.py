"""Data service — owns PostgreSQL, corpus management, query logging."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print(f"Starting {settings.project_name} data-service...")
    yield
    print("Shutting down data-service...")


app = FastAPI(
    title="Retail Intelligence — Data Service",
    description="Manages product corpus, FAQs, and query logs.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict:
    """Liveness check."""
    return {"service": "data-service", "status": "healthy"}
