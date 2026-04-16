from __future__ import annotations


def test_preview_overrides_raw_content(api_client) -> None:
    c = api_client.post("/api/v1/categories/", json={"name": "C", "slug": "c"}).json()
    sc = api_client.post(
        "/api/v1/sub-categories/",
        json={"category_id": c["id"], "name": "SC", "slug": "sc"},
    ).json()
    ssc = api_client.post(
        "/api/v1/sub-sub-categories/",
        json={"sub_category_id": sc["id"], "name": "SSC", "slug": "ssc"},
    ).json()

    pr = api_client.post(
        "/api/v1/subject-pages/",
        json={
            "category_id": c["id"],
            "sub_category_id": sc["id"],
            "sub_sub_category_id": ssc["id"],
            "title": "T",
            "slug": "prev-page",
            "summary": "",
            "raw_content": "<p>Hello world</p>",
            "status": "draft",
        },
    )
    pid = pr.json()["id"]

    r = api_client.post(
        f"/api/v1/subject-pages/{pid}/preview",
        json={"raw_content": "<p>Different</p>"},
    )
    assert r.status_code == 200
    assert "Different" in r.json()["rendered_content"]
