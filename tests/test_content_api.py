from fastapi.testclient import TestClient

from app.main import app


def test_content_api_valid_id() -> None:
    client = TestClient(app)
    resp = client.get("/api/content/interactive-learning")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["id"] == "interactive-learning"
    assert payload["type"] == "text"
    assert "title" in payload
    assert "description" in payload


def test_content_api_invalid_id_404() -> None:
    client = TestClient(app)
    resp = client.get("/api/content/does-not-exist")
    assert resp.status_code == 404
