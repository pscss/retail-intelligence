"""Unit tests for inference service."""

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_health() -> None:
    """Health endpoint returns healthy status."""
    with patch("inference_service.model_loader.ModelLoader.load_all"):
        from inference_service.main import app

        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == "inference-service"
