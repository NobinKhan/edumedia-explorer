from __future__ import annotations


def test_categories_crud(api_client) -> None:
    r = api_client.post("/api/v1/categories/", json={"name": "Science", "slug": "science"})
    assert r.status_code == 201
    cid = r.json()["id"]

    r = api_client.get("/api/v1/categories/")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = api_client.patch(f"/api/v1/categories/{cid}", json={"description": "STEM"})
    assert r.status_code == 200
    assert r.json()["description"] == "STEM"

    r = api_client.delete(f"/api/v1/categories/{cid}")
    assert r.status_code == 204

    r = api_client.get("/api/v1/categories/")
    assert r.json() == []
