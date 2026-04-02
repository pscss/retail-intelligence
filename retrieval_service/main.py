"""Retrieval service — semantic search and FAQ RAG."""

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from retrieval_service.routers import rag_router, search_router
from retrieval_service.semantic_index import faq_index, product_index
from shared.config import settings


async def load_corpus() -> None:
    """Load products and FAQs from data service and build indexes."""
    async with httpx.AsyncClient() as client:
        print("Loading products from data service...")
        response = await client.get(
            f"{settings.data_service_url}/products",
            params={"limit": 1000},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        products = data["items"]
        print(f"Loaded {len(products)} products")
        product_index.build(products, text_field="commodity_desc")

        print("Loading FAQs from data service...")
        response = await client.get(
            f"{settings.data_service_url}/faqs",
            params={"limit": 1000},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        faqs = data["items"]
        print(f"Loaded {len(faqs)} FAQs")
        faq_index.build(faqs, text_field="question")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load embedding model and build indexes at startup."""
    print(f"Starting {settings.project_name} retrieval-service...")
    product_index.load_model()
    faq_index._model = product_index._model
    try:
        await load_corpus()
    except Exception as e:
        print(f"Warning: Could not load corpus at startup: {e}")
        print("Service will start without indexes. Seed data and rebuild.")
    yield
    print("Shutting down retrieval-service...")


app = FastAPI(
    title="Retail Intelligence — Retrieval Service",
    description="Semantic search and FAQ RAG over retail corpus.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(search_router)
app.include_router(rag_router)


@app.get("/health")
async def health() -> dict:
    """Liveness check."""
    return {
        "service": "retrieval-service",
        "status": "healthy" if product_index.is_built else "loading",
        "product_index_size": product_index.size,
        "faq_index_size": faq_index.size,
    }
