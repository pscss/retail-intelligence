"""Inference service — transformer model inference for retail tasks."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from inference_service.model_loader import model_loader
from inference_service.routers import intent_router, sentiment_router, triage_router
from shared.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all models at startup, clean up on shutdown."""
    print(f"Starting {settings.project_name} inference-service...")
    model_loader.load_all()
    yield
    print("Shutting down inference-service...")


app = FastAPI(
    title="Retail Intelligence — Inference Service",
    description="Transformer model inference for sentiment, intent and triage.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(sentiment_router)
app.include_router(intent_router)
app.include_router(triage_router)


@app.get("/health")
async def health() -> dict:
    """Liveness check — includes model load status."""
    return {
        "service": "inference-service",
        "status": "healthy" if model_loader.is_loaded else "loading",
        "models_loaded": model_loader.is_loaded,
    }
