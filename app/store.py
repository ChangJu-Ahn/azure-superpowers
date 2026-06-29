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
    """
    CREATE TABLE IF NOT EXISTS channels (
        handle TEXT PRIMARY KEY,
        label TEXT,
        added_at TEXT
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


def get_summary(conn, video_id, lang):
    p = _ph(conn)
    cur = conn.cursor()
    cur.execute(
        f"SELECT text FROM summaries WHERE video_id = {p} AND lang = {p} "
        f"ORDER BY created_at DESC LIMIT 1",
        (video_id, lang),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_video(conn, video_id):
    p = _ph(conn)
    cur = conn.cursor()
    cur.execute(
        f"SELECT id, channel, title, published_at, url, fetched_at "
        f"FROM videos WHERE id = {p}",
        (video_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
    return dict(zip(cols, row))


def get_transcript(conn, video_id, lang):
    p = _ph(conn)
    cur = conn.cursor()
    cur.execute(
        f"SELECT text FROM transcripts WHERE video_id = {p} AND lang = {p} LIMIT 1",
        (video_id, lang),
    )
    row = cur.fetchone()
    return row[0] if row else None


def add_channel(conn, handle, label=None):
    p = _ph(conn)
    added_at = datetime.now(timezone.utc).isoformat()
    conn.cursor().execute(
        f"INSERT INTO channels (handle, label, added_at) VALUES ({p}, {p}, {p}) "
        f"ON CONFLICT (handle) DO NOTHING",
        (handle, label, added_at),
    )
    conn.commit()


def list_channels(conn):
    cur = conn.cursor()
    cur.execute("SELECT handle, label, added_at FROM channels ORDER BY added_at")
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def delete_channel(conn, handle):
    p = _ph(conn)
    conn.cursor().execute(f"DELETE FROM channels WHERE handle = {p}", (handle,))
    conn.commit()


def seed_channels(conn, handles):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM channels LIMIT 1")
    if cur.fetchone() is not None:
        return
    for h in handles:
        add_channel(conn, h)


def list_videos(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, channel, title, published_at, url, fetched_at "
        "FROM videos ORDER BY channel, published_at DESC"
    )
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
