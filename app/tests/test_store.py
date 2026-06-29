import sqlite3

import store


def make_conn():
    conn = sqlite3.connect(":memory:")
    store.init_db(conn)
    return conn


def test_upsert_and_list_one_video():
    conn = make_conn()
    video = {
        "id": "abc123",
        "channel": "Microsoft",
        "title": "Azure intro",
        "published_at": "2026-01-01T00:00:00Z",
        "url": "https://youtu.be/abc123",
    }
    store.upsert_video(conn, video)
    rows = store.list_videos(conn)
    assert len(rows) == 1
    assert rows[0]["id"] == "abc123"
    assert rows[0]["title"] == "Azure intro"


def test_upsert_ignores_duplicate_id():
    conn = make_conn()
    video = {"id": "dup", "channel": "c", "title": "t", "published_at": "2026-01-01T00:00:00Z", "url": "u"}
    store.upsert_video(conn, video)
    video["title"] = "changed"
    store.upsert_video(conn, video)
    rows = store.list_videos(conn)
    assert len(rows) == 1
    assert rows[0]["title"] == "t"


def test_list_videos_ordered_by_published_desc():
    conn = make_conn()
    store.upsert_video(conn, {"id": "1", "channel": "c", "title": "old", "published_at": "2026-01-01T00:00:00Z", "url": "u1"})
    store.upsert_video(conn, {"id": "2", "channel": "c", "title": "new", "published_at": "2026-06-01T00:00:00Z", "url": "u2"})
    rows = store.list_videos(conn)
    assert [r["id"] for r in rows] == ["2", "1"]


def test_save_summary():
    conn = make_conn()
    store.upsert_video(conn, {"id": "v", "channel": "c", "title": "t", "published_at": "2026-01-01T00:00:00Z", "url": "u"})
    store.save_summary(conn, "v", "ko", "요약", "gpt-4o")
    cur = conn.execute("SELECT video_id, lang, text, model FROM summaries")
    row = cur.fetchone()
    assert row == ("v", "ko", "요약", "gpt-4o")


def test_save_summary_dedup_one_row():
    conn = make_conn()
    store.save_summary(conn, "v", "ko", "처음", "gpt-4o")
    store.save_summary(conn, "v", "ko", "다시", "gpt-4o")
    cur = conn.execute("SELECT text, created_at FROM summaries WHERE video_id='v' AND lang='ko'")
    rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "다시"
    assert rows[0][1] is not None


def test_save_transcript_stored():
    conn = make_conn()
    store.save_transcript(conn, "v", "ko", "대본")
    store.save_transcript(conn, "v", "ko", "갱신")
    cur = conn.execute("SELECT text FROM transcripts WHERE video_id='v' AND lang='ko'")
    rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "갱신"


def test_channels_add_list_delete():
    conn = make_conn()
    store.add_channel(conn, "@microsoft")
    store.add_channel(conn, "@MicrosoftKorea")
    handles = [c["handle"] for c in store.list_channels(conn)]
    assert handles == ["@microsoft", "@MicrosoftKorea"]
    store.delete_channel(conn, "@microsoft")
    assert [c["handle"] for c in store.list_channels(conn)] == ["@MicrosoftKorea"]


def test_add_channel_dedup():
    conn = make_conn()
    store.add_channel(conn, "@microsoft")
    store.add_channel(conn, "@microsoft")
    assert len(store.list_channels(conn)) == 1


def test_seed_channels_only_when_empty():
    conn = make_conn()
    store.seed_channels(conn, ["@a", "@b"])
    store.seed_channels(conn, ["@c"])
    assert [c["handle"] for c in store.list_channels(conn)] == ["@a", "@b"]
