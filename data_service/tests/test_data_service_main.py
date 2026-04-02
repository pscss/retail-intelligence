from contextlib import asynccontextmanager

from fastapi.testclient import TestClient

from data_service.main import app


def test_data_service_health() -> None:
    """Data service health endpoint responds successfully."""

    @asynccontextmanager
    async def _noop_lifespan(_app):
        yield

    app.router.lifespan_context = _noop_lifespan

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "data-service"
    assert payload["status"] == "healthy"
