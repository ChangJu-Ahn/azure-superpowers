"""FastAPI web app: 누적된 한국어 요약 목록과 갱신 트리거."""

import os
import threading

from fastapi import BackgroundTasks, Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import store
from fetcher import fetch_recent, fetch_transcript, fetch_video, parse_channel_input, parse_video_id
from summarizer import insights_ko, summarize_ko

HANDLES = ["@microsoft", "@MicrosoftDeveloper", "@MicrosoftKorea"]

BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(title="MS YouTube 인사이트")


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
            os.environ.get("APP_DB_PATH", os.path.join(BASE_DIR, "insights.db")),
            check_same_thread=False,
        )
    store.init_db(conn)
    return conn


def get_conn():
    conn = open_conn()
    try:
        yield conn
    finally:
        conn.close()


_refresh_lock = threading.Lock()


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
    store.seed_channels(conn, HANDLES)
    videos = list_videos_with_summaries(conn)
    channels = store.list_channels(conn)
    return templates.TemplateResponse(
        request, "index.html", {"videos": videos, "channels": channels}
    )


@app.post("/channels")
def add_channel(url: str = Form(""), conn=Depends(get_conn)):
    handle = parse_channel_input(url)
    if handle:
        store.add_channel(conn, handle)
    return RedirectResponse(url="/", status_code=303)


@app.get("/video/{video_id}")
def video_detail(request: Request, video_id: str, conn=Depends(get_conn)):
    video = store.get_video(conn, video_id)
    if video is None:
        return RedirectResponse(url="/", status_code=303)
    deployment = os.environ.get("AOAI_DEPLOYMENT", "")
    transcript = store.get_transcript(conn, video_id, "ko")
    if transcript is None:
        transcript = fetch_transcript(video_id)
        if transcript:
            store.save_transcript(conn, video_id, "ko", transcript)
    summary = store.get_summary(conn, video_id, "ko")
    if not summary:
        try:
            summary = summarize_ko(transcript or video["title"])
            store.save_summary(conn, video_id, "ko", summary, deployment)
        except Exception:
            summary = "요약 대기 중 (Azure OpenAI 미연결)"
    insights = store.get_summary(conn, video_id, "insights")
    if not insights:
        try:
            insights = insights_ko(transcript or video["title"])
            store.save_summary(conn, video_id, "insights", insights, deployment)
        except Exception:
            insights = "인사이트 대기 중 (Azure OpenAI 미연결)"
    video["summary"] = summary
    video["insights"] = insights
    video["sections"] = _parse_sections(insights)
    video["transcript"] = transcript or "원문(자막) 없음"
    return templates.TemplateResponse(request, "detail.html", {"video": video})


def _parse_sections(insights):
    """'## 제목' 마크다운을 [{title, body}] 리스트로 분해. 실패 시 단일 섹션."""
    sections = []
    current = None
    for line in (insights or "").splitlines():
        if line.startswith("## "):
            current = {"title": line[3:].strip(), "body": ""}
            sections.append(current)
        elif current is not None:
            current["body"] += line + "\n"
    if not sections:
        sections = [{"title": "인사이트", "body": insights or ""}]
    return sections


@app.post("/channels/delete")
def remove_channel(handle: str = Form(""), conn=Depends(get_conn)):
    if handle:
        store.delete_channel(conn, handle)
    return RedirectResponse(url="/", status_code=303)


def _summarize_pending(video_ids, deployment):
    """백그라운드: 자체 DB 연결로 자막 추출+요약을 채운다(요청 블로킹 방지)."""
    if not _refresh_lock.acquire(blocking=False):
        return
    try:
        conn = open_conn()
        try:
            for vid in video_ids:
                if store.has_summary(conn, vid, "ko"):
                    continue
                text = fetch_transcript(vid)
                if text:
                    store.save_transcript(conn, vid, "ko", text)
                try:
                    summary = summarize_ko(text or vid)
                except Exception:
                    summary = "요약 대기 중 (Azure OpenAI 미연결)"
                store.save_summary(conn, vid, "ko", summary, deployment)
        finally:
            conn.close()
    finally:
        _refresh_lock.release()


@app.post("/refresh")
def refresh(background_tasks: BackgroundTasks, days: int = Form(20), conn=Depends(get_conn)):
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    handles = [c["handle"] for c in store.list_channels(conn)]
    video_ids = []
    for video in fetch_recent(handles, api_key, since_days=days):
        store.upsert_video(conn, video)
        video_ids.append(video["id"])
    background_tasks.add_task(
        _summarize_pending, video_ids, os.environ.get("AOAI_DEPLOYMENT", "")
    )
    return RedirectResponse(url="/", status_code=303)
