"""Data service — owns PostgreSQL, corpus management, query logging."""

import asyncio
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from data_service.routers import (
    faqs_router,
    products_router,
    query_logs_router,
    tasks_router,
)
from data_service.seed import SeedFaqs, SeedProducts
from data_service.session import AsyncSessionLocal, engine
from shared.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print(f"Starting {settings.project_name} data-service...")

    # Run migrations in thread pool to avoid blocking event loop
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, lambda: command.upgrade(Config("alembic.ini"), "head")
    )

    async with AsyncSessionLocal() as db:
        await SeedProducts().run(db)
        await SeedFaqs().run(db)
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
