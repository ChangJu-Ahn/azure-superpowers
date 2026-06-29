"""Data store layer. Works with PostgreSQL (psycopg) and SQLite (tests).

SQL is kept compatible with both backends. The connection's parameter style is
detected so callers can pass either a psycopg or sqlite3 connection.
"""

from datetime import datetime, timezone

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        channel TEXT,
        title TEXT,
        published_at TEXT,
        url TEXT,
        fetched_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS transcripts (
        video_id TEXT,
        lang TEXT,
        text TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS summaries (
        video_id TEXT,
        lang TEXT,
        text TEXT,
        model TEXT,
        created_at TEXT
    )
    """,
]


def _ph(conn):
    return "%s" if conn.__class__.__module__.startswith("psycopg") else "?"


def init_db(conn):
    cur = conn.cursor()
    for stmt in SCHEMA:
        cur.execute(stmt)
    conn.commit()


def upsert_video(conn, video):
    p = _ph(conn)
    sql = (
        f"INSERT INTO videos (id, channel, title, published_at, url, fetched_at) "
        f"VALUES ({p}, {p}, {p}, {p}, {p}, {p}) ON CONFLICT (id) DO NOTHING"
    )
    conn.cursor().execute(
        sql,
        (
            video["id"],
            video.get("channel"),
            video.get("title"),
            video.get("published_at"),
            video.get("url"),
            video.get("fetched_at"),
        ),
    )
    conn.commit()


def save_summary(conn, video_id, lang, text, model):
    p = _ph(conn)
    cur = conn.cursor()
    cur.execute(
        f"DELETE FROM summaries WHERE video_id = {p} AND lang = {p}",
        (video_id, lang),
    )
    created_at = datetime.now(timezone.utc).isoformat()
    cur.execute(
        f"INSERT INTO summaries (video_id, lang, text, model, created_at) "
        f"VALUES ({p}, {p}, {p}, {p}, {p})",
        (video_id, lang, text, model, created_at),
    )
    conn.commit()


def save_transcript(conn, video_id, lang, text):
    p = _ph(conn)
    cur = conn.cursor()
    cur.execute(
        f"DELETE FROM transcripts WHERE video_id = {p} AND lang = {p}",
        (video_id, lang),
    )
    cur.execute(
        f"INSERT INTO transcripts (video_id, lang, text) VALUES ({p}, {p}, {p})",
        (video_id, lang, text),
    )
    conn.commit()


def has_summary(conn, video_id, lang):
    p = _ph(conn)
    cur = conn.cursor()
    cur.execute(
        f"SELECT 1 FROM summaries WHERE video_id = {p} AND lang = {p} LIMIT 1",
        (video_id, lang),
    )
    return cur.fetchone() is not None


def list_videos(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, channel, title, published_at, url, fetched_at "
        "FROM videos ORDER BY channel, published_at DESC"
    )
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
