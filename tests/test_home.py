def test_homepage_loads(api_client) -> None:
    resp = api_client.get("/")
    assert resp.status_code == 200
    assert "EduMedia Author" in resp.text
