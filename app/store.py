"""Data store layer. Works with PostgreSQL (psycopg) and SQLite (tests).

SQL is kept compatible with both backends. The connection's parameter style is
detected so callers can pass either a psycopg or sqlite3 connection.
"""

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
    sql = (
        f"INSERT INTO summaries (video_id, lang, text, model, created_at) "
        f"VALUES ({p}, {p}, {p}, {p}, {p})"
    )
    conn.cursor().execute(sql, (video_id, lang, text, model, None))
    conn.commit()


def list_videos(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, channel, title, published_at, url, fetched_at "
        "FROM videos ORDER BY published_at DESC"
    )
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
