from fastapi.testclient import TestClient

import retrieval_service.main as retrieval_main


async def _noop_load_corpus() -> None:
    return None


def test_retrieval_service_health(monkeypatch) -> None:
    """Retrieval service health endpoint responds without startup corpus load."""
    monkeypatch.setattr(retrieval_main, "load_corpus", _noop_load_corpus)
    monkeypatch.setattr(retrieval_main.product_index, "load_model", lambda: None)

    with TestClient(retrieval_main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "retrieval-service"
    assert "product_index_size" in payload
    assert "faq_index_size" in payload
