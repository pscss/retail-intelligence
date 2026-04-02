"""HTTP client for inference-service."""

import httpx

from shared.config import settings


class InferenceClient:
    """Client wrapper for inference service operations."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient()

    async def stop(self) -> None:
        if self._client:
            await self._client.aclose()

    async def sentiment(self, text: str) -> dict:
        response = await self._client.post(
            f"{settings.inference_service_url}/sentiment",
            json={"text": text},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    async def intent(self, text: str) -> dict:
        response = await self._client.post(
            f"{settings.inference_service_url}/intent",
            json={"text": text},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    async def triage(self, text: str) -> dict:
        response = await self._client.post(
            f"{settings.inference_service_url}/triage",
            json={"text": text},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


inference_client = InferenceClient()
