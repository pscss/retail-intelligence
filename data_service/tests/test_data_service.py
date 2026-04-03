"""Unit tests for data service."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_health() -> None:
    """Health endpoint returns healthy status."""
    with (
        patch(
            "data_service.seed.seed_products.SeedProducts.run", new_callable=AsyncMock
        ),
        patch("data_service.seed.seed_faqs.SeedFaqs.run", new_callable=AsyncMock),
    ):
        from data_service.main import app

        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == "data-service"
    assert response.json()["status"] == "healthy"
