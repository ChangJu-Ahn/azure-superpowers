"""FastAPI web app: 누적된 한국어 요약 목록과 갱신 트리거."""

import os

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import store
from fetcher import fetch_recent, fetch_transcript, fetch_video, parse_channel_input, parse_video_id
from summarizer import summarize_ko

HANDLES = ["@microsoft", "@MicrosoftDeveloper", "@MicrosoftKorea"]

BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(title="MS YouTube 인사이트")


def get_conn():
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
            os.environ.get("APP_DB_PATH", os.path.join(BASE_DIR, "insights.db")),
            check_same_thread=False,
        )
    store.init_db(conn)
    try:
        yield conn
    finally:
        conn.close()


def list_videos_with_summaries(conn):
    videos = store.list_videos(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT video_id, text FROM summaries WHERE lang = 'ko' "
        "ORDER BY created_at"
    )
    summaries = {row[0]: row[1] for row in cur.fetchall()}
    for v in videos:
        v["summary"] = summaries.get(v["id"])
    return videos


@app.get("/")
def index(request: Request, conn=Depends(get_conn)):
    videos = list_videos_with_summaries(conn)
    return templates.TemplateResponse(
        request, "index.html", {"videos": videos}
    )


def _summarize_and_store(conn, video):
    store.upsert_video(conn, video)
    if store.has_summary(conn, video["id"], "ko"):
        return
    text = fetch_transcript(video["id"])
    if text:
        store.save_transcript(conn, video["id"], "ko", text)
    try:
        summary = summarize_ko(text or video["title"])
    except Exception:
        summary = "요약 대기 중 (Azure OpenAI 미연결)"
    store.save_summary(conn, video["id"], "ko", summary, os.environ.get("AOAI_DEPLOYMENT", ""))


@app.post("/refresh")
def refresh(urls: str = Form(""), days: int = Form(20), conn=Depends(get_conn)):
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    handles = list(HANDLES)
    video_ids = []
    for raw in urls.replace(",", "\n").split("\n"):
        raw = raw.strip()
        if not raw:
            continue
        vid = parse_video_id(raw)
        if vid:
            video_ids.append(vid)
            continue
        handle = parse_channel_input(raw)
        if handle:
            handles.append(handle)

    for video in fetch_recent(handles, api_key, since_days=days):
        _summarize_and_store(conn, video)
    for vid in video_ids:
        video = fetch_video(vid, api_key)
        if video:
            _summarize_and_store(conn, video)
    return RedirectResponse(url="/", status_code=303)
