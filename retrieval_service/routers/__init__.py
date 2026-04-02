"""Retrieval service routers."""

from retrieval_service.routers.rag import router as rag_router
from retrieval_service.routers.search import router as search_router

__all__ = [
    "rag_router",
    "search_router",
]
