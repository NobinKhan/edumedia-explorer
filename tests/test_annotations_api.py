from __future__ import annotations


def _hierarchy(api_client):
    c = api_client.post("/api/v1/categories/", json={"name": "Cat", "slug": "cat"}).json()
    sc = api_client.post(
        "/api/v1/sub-categories/",
        json={"category_id": c["id"], "name": "Sub", "slug": "sub"},
    ).json()
    ssc = api_client.post(
        "/api/v1/sub-sub-categories/",
        json={"sub_category_id": sc["id"], "name": "Leaf", "slug": "leaf"},
    ).json()
    return c, sc, ssc


def test_annotation_validation_rejects_cross_node_selection(api_client) -> None:
    c, sc, ssc = _hierarchy(api_client)
    # Two separate text nodes: <b> splits nodes.
    raw = "<p>Hello <b>world</b></p>"
    pr = api_client.post(
        "/api/v1/subject-pages/",
        json={
            "category_id": c["id"],
            "sub_category_id": sc["id"],
            "sub_sub_category_id": ssc["id"],
            "title": "T",
            "slug": "t2-page",
            "summary": "",
            "raw_content": raw,
            "status": "draft",
        },
    )
    assert pr.status_code == 201
    pid = pr.json()["id"]

    # Plain text is "Hello world" but selection crosses nodes ("o " + "w").
    ar = api_client.post(
        f"/api/v1/subject-pages/{pid}/annotations",
        json={
            "annotation_type": "text",
            "trigger_text": "o w",
            "start_offset": 4,
            "end_offset": 7,
            "title": "bad",
            "body_text": "nope",
        },
    )
    assert ar.status_code == 400


def test_youtube_annotation_requires_plausible_url(api_client) -> None:
    c, sc, ssc = _hierarchy(api_client)
    pr = api_client.post(
        "/api/v1/subject-pages/",
        json={
            "category_id": c["id"],
            "sub_category_id": sc["id"],
            "sub_sub_category_id": ssc["id"],
            "title": "T",
            "slug": "t3-page",
            "summary": "",
            "raw_content": "<p>Hello world</p>",
            "status": "draft",
        },
    )
    pid = pr.json()["id"]
    ar = api_client.post(
        f"/api/v1/subject-pages/{pid}/annotations",
        json={
            "annotation_type": "youtube",
            "trigger_text": "world",
            "start_offset": 6,
            "end_offset": 11,
            "title": "vid",
            "youtube_url": "https://example.com/watch?v=x",
        },
    )
    assert ar.status_code == 400
