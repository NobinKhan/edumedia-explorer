from __future__ import annotations

import pytest
from sqlalchemy import delete, func, select

import app.config as app_config
from app.db import SessionLocal
from app.models.category import Category
from app.models.request_log import RequestLog
from app.tracker.middleware import request_path_for_log


@pytest.fixture
def tracker_secret_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        app_config,
        "settings",
        app_config.settings.model_copy(update={"tracker_secret": "test-tracker-secret-key"}),
    )


def test_tracker_disabled_returns_404(api_client) -> None:
    resp = api_client.get("/tracker")
    assert resp.status_code == 404


def test_openapi_excludes_tracker_paths(api_client) -> None:
    resp = api_client.get("/openapi.json")
    assert resp.status_code == 200
    paths = resp.json().get("paths") or {}
    assert not any(str(p).startswith("/tracker") for p in paths)


def test_tracker_login_and_dashboard(api_client, tracker_secret_on: None) -> None:
    r = api_client.get("/tracker", follow_redirects=False)
    assert r.status_code == 200
    assert "Usage tracker" in r.text

    bad = api_client.post("/tracker/login", data={"secret": "wrong"})
    assert bad.status_code == 401

    ok = api_client.post(
        "/tracker/login",
        data={"secret": "test-tracker-secret-key"},
        follow_redirects=False,
    )
    assert ok.status_code == 302
    assert ok.headers.get("location", "").endswith("/tracker/dashboard")
    assert "tracker_session" in ok.headers.get("set-cookie", "").lower()

    dash = api_client.get("/tracker/dashboard")
    assert dash.status_code == 200
    assert "Request analytics" in dash.text

    out = api_client.post("/tracker/logout", follow_redirects=False)
    assert out.status_code == 302
    set_cookie = out.headers.get("set-cookie") or ""
    assert "tracker_session" in set_cookie.lower()


def test_tracker_header_grants_dashboard(api_client, tracker_secret_on: None) -> None:
    r = api_client.get(
        "/tracker/dashboard",
        headers={"X-Tracker-Secret": "test-tracker-secret-key"},
    )
    assert r.status_code == 200


def test_request_path_for_log_uses_actual_path_and_query() -> None:
    assert request_path_for_log("/pages/photosynthesis", "") == "/pages/photosynthesis"
    assert request_path_for_log("/api/v1/meta", "verbose=1") == "/api/v1/meta?verbose=1"
    long_q = "x=" + ("a" * 3000)
    out = request_path_for_log("/p", long_q)
    assert len(out) == 2048


def test_middleware_inserts_request_log(api_client, tracker_secret_on: None) -> None:
    with SessionLocal() as session:
        session.execute(delete(RequestLog))
        session.commit()
        before = session.scalar(select(func.count()).select_from(RequestLog)) or 0

    api_client.get("/api/v1/meta")

    with SessionLocal() as session:
        after = session.scalar(select(func.count()).select_from(RequestLog)) or 0

    assert after == before + 1
    with SessionLocal() as session:
        row = session.scalar(select(RequestLog).order_by(RequestLog.id.desc()).limit(1))
    assert row is not None
    assert row.method == "GET"
    assert "/api/v1/meta" in row.path
    assert row.status_code == 200


def test_tracker_reset_requires_secret_confirmation(api_client, tracker_secret_on: None) -> None:
    api_client.post(
        "/tracker/login",
        data={"secret": "test-tracker-secret-key"},
        follow_redirects=False,
    )
    r = api_client.get("/tracker/reset-data")
    assert r.status_code == 200
    assert "Reset app data" in r.text

    bad = api_client.post("/tracker/reset-data", data={"secret": "wrong"})
    assert bad.status_code == 401
    assert "Invalid secret" in bad.text

    with SessionLocal() as session:
        session.add(
            Category(name="Tmp", slug="tmp-tracker-reset-test", description="will vanish"),
        )
        session.commit()
        before_cats = session.scalar(select(func.count()).select_from(Category)) or 0
        before_logs = session.scalar(select(func.count()).select_from(RequestLog)) or 0

    ok = api_client.post(
        "/tracker/reset-data",
        data={"secret": "test-tracker-secret-key"},
        follow_redirects=False,
    )
    assert ok.status_code == 302
    assert "reset=ok" in (ok.headers.get("location") or "")

    with SessionLocal() as session:
        after_cats = session.scalar(select(func.count()).select_from(Category)) or 0
        tmp = session.scalar(select(Category).where(Category.slug == "tmp-tracker-reset-test"))
        science = session.scalar(select(Category).where(Category.slug == "science"))
        after_logs = session.scalar(select(func.count()).select_from(RequestLog)) or 0

    assert tmp is None
    assert science is not None
    assert before_cats >= 2
    assert after_cats == 1
    assert after_logs >= before_logs
