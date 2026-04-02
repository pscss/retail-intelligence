"""Inference service routers."""

from inference_service.routers.intent import router as intent_router
from inference_service.routers.sentiment import router as sentiment_router
from inference_service.routers.triage import router as triage_router

__all__ = [
    "intent_router",
    "sentiment_router",
    "triage_router",
]
