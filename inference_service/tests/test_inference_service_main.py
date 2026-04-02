from fastapi.testclient import TestClient

import inference_service.main as inference_main


def test_inference_service_health(monkeypatch) -> None:
    """Inference service health endpoint responds without loading models."""
    monkeypatch.setattr(inference_main.model_loader, "load_all", lambda: None)

    with TestClient(inference_main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "inference-service"
    assert "models_loaded" in payload
