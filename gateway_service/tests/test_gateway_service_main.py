from fastapi.testclient import TestClient

import gateway_service.main as gateway_main
from gateway_service.controller.auth import require_api_key
from gateway_service.controller.rate_limit import enforce_rate_limit


def test_gateway_health() -> None:
    """Gateway health endpoint responds successfully."""
    with TestClient(gateway_main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "gateway-service"
    assert payload["status"] == "healthy"


def test_graphql_health_query_with_overrides() -> None:
    """Gateway GraphQL health query works with auth/rate-limit overrides."""
    gateway_main.app.dependency_overrides[require_api_key] = lambda: None
    gateway_main.app.dependency_overrides[enforce_rate_limit] = lambda: None

    try:
        with TestClient(gateway_main.app) as client:
            response = client.post("/graphql", json={"query": "query { health }"})
    finally:
        gateway_main.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["health"] == "healthy"
