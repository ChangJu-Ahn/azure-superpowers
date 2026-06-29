import sqlite3

import refresh_job
import store


def test_run_refresh_saves_summary(monkeypatch):
    conn = sqlite3.connect(":memory:")
    store.init_db(conn)

    monkeypatch.setattr(refresh_job, "fetch_recent", lambda *a, **k: [
        {"id": "vX", "channel": "Microsoft", "title": "Title",
         "published_at": "2026-06-02T00:00:00Z", "url": "uX"}
    ])
    monkeypatch.setattr(refresh_job, "fetch_transcript", lambda vid: None)
    monkeypatch.setattr(refresh_job, "summarize_ko", lambda text: "요약결과")

    count = refresh_job.run_refresh(conn)

    assert count == 1
    rows = store.list_videos(conn)
    assert any(r["id"] == "vX" for r in rows)
    cur = conn.execute("SELECT text FROM summaries WHERE video_id='vX'")
    assert cur.fetchone()[0] == "요약결과"
