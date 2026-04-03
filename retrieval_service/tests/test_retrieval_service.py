"""Unit tests for retrieval service."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_health() -> None:
    """Health endpoint returns healthy status."""
    with (
        patch("retrieval_service.main.load_corpus", new_callable=AsyncMock),
        patch("retrieval_service.semantic_index.SemanticIndex.load_model"),
    ):
        from retrieval_service.main import app

        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == "retrieval-service"
