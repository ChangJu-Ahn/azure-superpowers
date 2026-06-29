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


def fetch_recent(handles, api_key, max_n=5, youtube=None):
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
            videos.append(
                {
                    "id": vid,
                    "channel": title,
                    "title": snip.get("title", ""),
                    "published_at": snip.get("publishedAt", ""),
                    "url": f"https://www.youtube.com/watch?v={vid}",
                }
            )
    return videos


def fetch_transcript(video_id, transcript_api=None):
    try:
        if transcript_api is None:
            from youtube_transcript_api import YouTubeTranscriptApi

            transcript_api = YouTubeTranscriptApi()
        fetched = transcript_api.fetch(video_id)
        return " ".join(snippet.text for snippet in fetched).strip()
    except Exception:
        return None
