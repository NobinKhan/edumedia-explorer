from __future__ import annotations


def test_sub_category_and_sub_sub_category_filters(api_client) -> None:
    c1 = api_client.post("/api/v1/categories/", json={"name": "C1", "slug": "c1"}).json()
    c2 = api_client.post("/api/v1/categories/", json={"name": "C2", "slug": "c2"}).json()

    sc1 = api_client.post(
        "/api/v1/sub-categories/",
        json={"category_id": c1["id"], "name": "SC1", "slug": "sc1"},
    ).json()
    api_client.post(
        "/api/v1/sub-categories/",
        json={"category_id": c2["id"], "name": "SC2", "slug": "sc2"},
    ).json()

    r = api_client.get(f"/api/v1/sub-categories/?category_id={c1['id']}")
    assert r.status_code == 200
    assert [x["id"] for x in r.json()] == [sc1["id"]]

    api_client.post(
        "/api/v1/sub-sub-categories/",
        json={"sub_category_id": sc1["id"], "name": "SSC1", "slug": "ssc1"},
    ).json()
    api_client.post(
        "/api/v1/sub-sub-categories/",
        json={"sub_category_id": sc1["id"], "name": "SSC2", "slug": "ssc2"},
    ).json()

    r = api_client.get(f"/api/v1/sub-sub-categories/?sub_category_id={sc1['id']}")
    assert r.status_code == 200
    payload = r.json()
    assert len(payload) == 2
    assert all(x["sub_category_id"] == sc1["id"] for x in payload)
