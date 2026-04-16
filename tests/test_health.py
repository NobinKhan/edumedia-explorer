def test_healthz(api_client) -> None:
    resp = api_client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["database"] in ("sqlite", "postgresql", "unknown")
    assert data["database_status"] == "connected"
