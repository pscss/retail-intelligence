from fastapi.testclient import TestClient

import gateway_service.main as gateway_main


def test_gateway_health() -> None:
    """Gateway health endpoint responds successfully."""
    with TestClient(gateway_main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "gateway-service"
    assert payload["status"] == "healthy"


def test_graphql_health_query_with_overrides() -> None:
    """Gateway GraphQL health query works with valid API key."""
    with TestClient(gateway_main.app) as client:
        response = client.post(
            "/graphql",
            json={"query": "query { health }"},
            headers={"X-Api-Key": "dev-api-key-change-in-prod"},
        )
    assert response.status_code == 200
    assert response.json()["data"]["health"] == "healthy"
