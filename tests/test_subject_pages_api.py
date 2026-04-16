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


def test_subject_page_publish_and_rendered(api_client) -> None:
    c, sc, ssc = _hierarchy(api_client)
    raw = "<p>Hello world</p>"
    pr = api_client.post(
        "/api/v1/subject-pages/",
        json={
            "category_id": c["id"],
            "sub_category_id": sc["id"],
            "sub_sub_category_id": ssc["id"],
            "title": "T",
            "slug": "t-page",
            "summary": "S",
            "raw_content": raw,
            "status": "draft",
        },
    )
    assert pr.status_code == 201
    pid = pr.json()["id"]

    # "world" is a single text node slice; offsets 6-11 in plain "Hello world"
    ar = api_client.post(
        f"/api/v1/subject-pages/{pid}/annotations",
        json={
            "annotation_type": "text",
            "trigger_text": "world",
            "start_offset": 6,
            "end_offset": 11,
            "title": "Note",
            "body_text": "A note about world.",
        },
    )
    assert ar.status_code == 201

    pub = api_client.post(f"/api/v1/subject-pages/{pid}/publish")
    assert pub.status_code == 200
    rendered = pub.json()["rendered_content"]
    assert "anno-term" in rendered
    assert "data-annotation-id" in rendered

    rr = api_client.get(f"/api/v1/subject-pages/{pid}/rendered")
    assert rr.status_code == 200
    assert rr.json()["rendered_content"] == rendered
