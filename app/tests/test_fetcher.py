from unittest.mock import MagicMock

import fetcher


def make_youtube_mock():
    youtube = MagicMock()

    def channels_list(part, forHandle):
        ch = MagicMock()
        ch.execute.return_value = {
            "items": [
                {
                    "snippet": {"title": "Microsoft"},
                    "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
                }
            ]
        }
        return ch

    def items_list(part, playlistId, maxResults):
        pl = MagicMock()
        pl.execute.return_value = {
            "items": [
                {
                    "snippet": {
                        "title": "Intro to Azure",
                        "publishedAt": "2026-06-01T00:00:00Z",
                        "resourceId": {"videoId": "vid001"},
                    }
                }
            ]
        }
        return pl

    youtube.channels.return_value.list.side_effect = channels_list
    youtube.playlistItems.return_value.list.side_effect = items_list
    return youtube


def test_fetch_recent_returns_dicts():
    youtube = make_youtube_mock()
    videos = fetcher.fetch_recent(["Microsoft"], api_key="k", max_n=5, youtube=youtube)
    assert len(videos) == 1
    v = videos[0]
    assert v["id"] == "vid001"
    assert v["channel"] == "Microsoft"
    assert v["title"] == "Intro to Azure"
    assert v["published_at"] == "2026-06-01T00:00:00Z"
    assert v["url"] == "https://www.youtube.com/watch?v=vid001"


def test_fetch_transcript_joins_text():
    snip = MagicMock()
    snip.text = "Hello world"
    api = MagicMock()
    api.fetch.return_value = [snip]
    assert fetcher.fetch_transcript("vid001", transcript_api=api) == "Hello world"


def test_fetch_transcript_none_on_exception():
    api = MagicMock()
    api.fetch.side_effect = Exception("no captions")
    assert fetcher.fetch_transcript("vid001", transcript_api=api) is None
