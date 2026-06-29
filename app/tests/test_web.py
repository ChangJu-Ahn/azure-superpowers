import sqlite3
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import main
import store


def make_conn():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    store.init_db(conn)
    return conn


def client_with_conn(conn):
    main.app.dependency_overrides[main.get_conn] = lambda: conn
    return TestClient(main.app)


def test_index_returns_200_and_lists_videos():
    conn = make_conn()
    store.upsert_video(
        conn,
        {"id": "v1", "channel": "Microsoft", "title": "Azure intro",
         "published_at": "2026-06-01T00:00:00Z", "url": "u1"},
    )
    store.save_summary(conn, "v1", "ko", "한국어 요약", "gpt-4o")
    client = client_with_conn(conn)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Azure intro" in resp.text
    assert "한국어 요약" in resp.text
    main.app.dependency_overrides.clear()


def test_refresh_saves_summary(monkeypatch):
    conn = make_conn()
    monkeypatch.setattr(main, "fetch_recent", lambda *a, **k: [
        {"id": "vX", "channel": "Microsoft", "title": "Title", "published_at": "2026-06-02T00:00:00Z", "url": "uX"}
    ])
    monkeypatch.setattr(main, "fetch_transcript", lambda vid: None)
    monkeypatch.setattr(main, "summarize_ko", lambda text: "요약결과")
    client = client_with_conn(conn)
    resp = client.post("/refresh", follow_redirects=False)
    assert resp.status_code in (302, 303, 307)
    rows = store.list_videos(conn)
    assert any(r["id"] == "vX" for r in rows)
    cur = conn.execute("SELECT text FROM summaries WHERE video_id='vX'")
    assert cur.fetchone()[0] == "요약결과"
    main.app.dependency_overrides.clear()


def test_channels_crud_via_web():
    conn = make_conn()
    client = client_with_conn(conn)
    client.post("/channels", data={"url": "https://www.youtube.com/@Microsoft"}, follow_redirects=False)
    assert [c["handle"] for c in store.list_channels(conn)] == ["@Microsoft"]
    client.post("/channels/delete", data={"handle": "@Microsoft"}, follow_redirects=False)
    assert store.list_channels(conn) == []
    main.app.dependency_overrides.clear()


def test_refresh_uses_saved_channels(monkeypatch):
    conn = make_conn()
    store.add_channel(conn, "@onlythis")
    used = {}
    def fake_fetch(handles, key, since_days=None):
        used["handles"] = handles
        return []
    monkeypatch.setattr(main, "fetch_recent", fake_fetch)
    client = client_with_conn(conn)
    client.post("/refresh", follow_redirects=False)
    assert used["handles"] == ["@onlythis"]
    main.app.dependency_overrides.clear()
