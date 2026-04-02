"""Data service — owns PostgreSQL, corpus management, query logging."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from data_service.routers import (
    faqs_router,
    products_router,
    query_logs_router,
    tasks_router,
)
from data_service.session import engine
from shared.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print(f"Starting {settings.project_name} data-service...")
    yield
    await engine.dispose()
    print("Shutting down data-service...")


app = FastAPI(
    title="Retail Intelligence — Data Service",
    description="Manages product corpus, FAQs, and query logs.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(products_router)
app.include_router(faqs_router)
app.include_router(query_logs_router)
app.include_router(tasks_router)


@app.get("/health")
async def health() -> dict:
    """Liveness check."""
    return {"service": "data-service", "status": "healthy"}
