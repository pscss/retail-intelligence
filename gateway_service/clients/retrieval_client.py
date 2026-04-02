"""HTTP client for retrieval-service."""

import httpx

from shared.config import settings


class RetrievalClient:
    """Client wrapper for retrieval service operations."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient()

    async def stop(self) -> None:
        if self._client:
            await self._client.aclose()

    async def search_products(self, query: str, top_k: int) -> dict:
        response = await self._client.post(
            f"{settings.retrieval_service_url}/search",
            json={"query": query, "top_k": top_k},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    async def query_faq(self, question: str, top_k: int) -> dict:
        response = await self._client.post(
            f"{settings.retrieval_service_url}/rag",
            json={"question": question, "top_k": top_k},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


retrieval_client = RetrievalClient()
