from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
client = TestClient(app)


def test_app_created():
    """Verify the FastAPI app initialises correctly."""
    assert app is not None


def test_unknown_route_returns_404():
    """Placeholder test — replace with real route tests."""
    response = client.get("/")
    assert response.status_code == 404
