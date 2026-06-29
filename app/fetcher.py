"""YouTube fetcher: recent videos per channel handle + transcripts.

Networking is injected (``youtube`` service, ``transcript_api``) so tests can
mock without real network calls.
"""


def _build_youtube(api_key):
    from googleapiclient.discovery import build

    return build("youtube", "v3", developerKey=api_key)


def _resolve_uploads_playlist(youtube, handle):
    h = handle if handle.startswith("@") else f"@{handle}"
    resp = (
        youtube.channels()
        .list(part="snippet,contentDetails", forHandle=h)
        .execute()
    )
    items = resp.get("items") or []
    if not items:
        return None, None
    ch = items[0]
    title = ch.get("snippet", {}).get("title", h)
    playlist = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    return title, playlist


def parse_channel_input(text):
    """채널 URL/핸들에서 핸들(@name) 추출. 영상 URL이면 None."""
    t = (text or "").strip()
    if not t:
        return None
    if parse_video_id(t):
        return None
    if "youtube.com" in t:
        import re

        m = re.search(r"/(@[A-Za-z0-9._-]+)", t)
        if m:
            return m.group(1)
        m = re.search(r"/(?:c|user)/([A-Za-z0-9._-]+)", t)
        if m:
            return f"@{m.group(1)}"
        return None
    return t if t.startswith("@") else f"@{t}"


def parse_video_id(text):
    """영상 URL에서 video id 추출. 아니면 None."""
    t = (text or "").strip()
    import re

    m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", t)
    return m.group(1) if m else None


def _within_days(published_at, days):
    if not days or not published_at:
        return True
    from datetime import datetime, timezone, timedelta

    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    return dt >= datetime.now(timezone.utc) - timedelta(days=days)


def fetch_recent(handles, api_key, max_n=5, youtube=None, since_days=None):
    if youtube is None:
        youtube = _build_youtube(api_key)

    videos = []
    for handle in handles:
        title, playlist = _resolve_uploads_playlist(youtube, handle)
        if not playlist:
            continue
        resp = (
            youtube.playlistItems()
            .list(part="snippet", playlistId=playlist, maxResults=max_n)
            .execute()
        )
        for item in resp.get("items", [])[:max_n]:
            snip = item["snippet"]
            vid = snip["resourceId"]["videoId"]
            published = snip.get("publishedAt", "")
            if not _within_days(published, since_days):
                continue
            videos.append(
                {
                    "id": vid,
                    "channel": title,
                    "title": snip.get("title", ""),
                    "published_at": published,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                }
            )
    return videos


def fetch_video(video_id, api_key, youtube=None):
    """단일 영상 메타데이터. 없으면 None."""
    if youtube is None:
        youtube = _build_youtube(api_key)
    resp = youtube.videos().list(part="snippet", id=video_id).execute()
    items = resp.get("items") or []
    if not items:
        return None
    snip = items[0]["snippet"]
    return {
        "id": video_id,
        "channel": snip.get("channelTitle", ""),
        "title": snip.get("title", ""),
        "published_at": snip.get("publishedAt", ""),
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def fetch_transcript(video_id, transcript_api=None):
    try:
        if transcript_api is None:
            from youtube_transcript_api import YouTubeTranscriptApi

            transcript_api = YouTubeTranscriptApi()
        fetched = transcript_api.fetch(video_id)
        return " ".join(snippet.text for snippet in fetched).strip()
    except Exception:
        return None
