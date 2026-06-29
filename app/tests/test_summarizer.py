from unittest.mock import MagicMock

import summarizer


def make_mock_client(reply="한국어 요약입니다."):
    client = MagicMock()
    message = MagicMock()
    message.content = reply
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]
    client.chat.completions.create.return_value = completion
    return client


def test_summarize_ko_returns_mock_text():
    client = make_mock_client("이 영상은 Azure를 소개합니다.")
    result = summarizer.summarize_ko("This video introduces Azure.", client=client)
    assert result == "이 영상은 Azure를 소개합니다."


def test_summarize_ko_uses_korean_prompt():
    client = make_mock_client()
    summarizer.summarize_ko("Some English transcript.", client=client)
    args, kwargs = client.chat.completions.create.call_args
    messages = kwargs["messages"]
    joined = " ".join(m["content"] for m in messages)
    assert "한국어" in joined
    assert "Some English transcript." in joined


def test_summarize_ko_truncates_long_text():
    client = make_mock_client()
    long_text = "word " * 20000
    summarizer.summarize_ko(long_text, client=client)
    args, kwargs = client.chat.completions.create.call_args
    sent = " ".join(m["content"] for m in kwargs["messages"])
    assert len(sent) < len(long_text)
