"""배치 진입점: 웹 서버 없이 전체 갱신을 1회 수행한다.

main.py와 동일한 env/DB 선택(키리스 PG 우선, 없으면 SQLite)을 사용해
init_db → fetch → transcript(없으면 title) → summarize → upsert+save 순으로 처리한다.
"""

import os

import store
from fetcher import fetch_recent, fetch_transcript
from summarizer import summarize_ko

HANDLES = ["@microsoft", "@MicrosoftDeveloper", "@MicrosoftKorea"]

BASE_DIR = os.path.dirname(__file__)


def open_conn():
    """DB 연결. PostgreSQL(키리스: Entra 토큰) 우선, 없으면 로컬 SQLite."""
    if os.environ.get("PGHOST"):
        import psycopg
        from azure.identity import DefaultAzureCredential

        token = DefaultAzureCredential().get_token(
            "https://ossrdbms-aad.database.windows.net/.default"
        )
        conn = psycopg.connect(password=token.token)
    else:
        import sqlite3

        conn = sqlite3.connect(
            os.environ.get("APP_DB_PATH", os.path.join(BASE_DIR, "insights.db"))
        )
    store.init_db(conn)
    return conn


def run_refresh(conn):
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    model = os.environ.get("AOAI_DEPLOYMENT", "")
    count = 0
    for video in fetch_recent(HANDLES, api_key):
        text = fetch_transcript(video["id"]) or video["title"]
        summary = summarize_ko(text)
        store.upsert_video(conn, video)
        store.save_summary(conn, video["id"], "ko", summary, model)
        count += 1
    return count


def main():
    conn = open_conn()
    try:
        count = run_refresh(conn)
        print(f"refresh complete: {count} videos")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
