from fastapi.testclient import TestClient

from app.main import app


def test_homepage_loads() -> None:
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Interactive Teaching Platform" in resp.text
