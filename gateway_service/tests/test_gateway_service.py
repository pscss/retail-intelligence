"""Unit tests for gateway service."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_health() -> None:
    """Health endpoint returns healthy status."""
    with (
        patch(
            "gateway_service.clients.inference_client.InferenceClient.start",
            new_callable=AsyncMock,
        ),
        patch(
            "gateway_service.clients.retrieval_client.RetrievalClient.start",
            new_callable=AsyncMock,
        ),
        patch(
            "gateway_service.clients.data_client.DataClient.start",
            new_callable=AsyncMock,
        ),
    ):
        from gateway_service.main import app

        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == "gateway-service"


def test_graphql_health(api_key_header: dict[str, str]) -> None:
    """GraphQL health query returns healthy."""
    with (
        patch(
            "gateway_service.clients.inference_client.InferenceClient.start",
            new_callable=AsyncMock,
        ),
        patch(
            "gateway_service.clients.retrieval_client.RetrievalClient.start",
            new_callable=AsyncMock,
        ),
        patch(
            "gateway_service.clients.data_client.DataClient.start",
            new_callable=AsyncMock,
        ),
    ):
        from gateway_service.main import app

        with TestClient(app) as client:
            response = client.post(
                "/graphql",
                json={"query": "{ health }"},
                headers=api_key_header,
            )

    assert response.status_code == 200
    assert response.json()["data"]["health"] == "healthy"
