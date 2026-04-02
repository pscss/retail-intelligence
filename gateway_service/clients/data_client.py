"""HTTP client for data-service."""

import httpx

from shared.config import settings


class DataClient:
    """Client wrapper for data-service operations."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient()

    async def stop(self) -> None:
        if self._client:
            await self._client.aclose()

    async def create_query_log(self, payload: dict) -> None:
        await self._client.post(
            f"{settings.data_service_url}/query-logs",
            json=payload,
            timeout=10.0,
        )


data_client = DataClient()
