import os

MAX_CHARS = 24000

SYSTEM_PROMPT = (
    "당신은 영어 영상 자막을 한국어로 요약하는 전문가입니다. "
    "핵심 내용을 정확하고 간결하게 한국어로 요약하세요."
)

INSIGHTS_PROMPT = (
    "당신은 영상 자막을 분석해 실무 인사이트를 카테고리별로 정리하는 전문가입니다. "
    "반드시 아래 5개 섹션을 한국어 마크다운으로 작성하세요. 각 섹션은 '## ' 제목으로 시작하고 "
    "내용은 글머리표(•) 2~4개로 정리합니다.\n"
    "## 기술\n## 비용\n## 관리\n## 기업\n## 트렌드\n"
    "근거가 부족한 섹션은 '• 자막에서 관련 내용 없음'으로 표기하세요."
)


def _build_client():
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    from openai import AzureOpenAI

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return AzureOpenAI(
        azure_endpoint=os.environ["AOAI_ENDPOINT"],
        azure_ad_token_provider=token_provider,
        api_version="2024-10-21",
    )


def summarize_ko(text, client=None):
    if client is None:
        client = _build_client()

    transcript = text[:MAX_CHARS]
    completion = client.chat.completions.create(
        model=os.environ.get("AOAI_DEPLOYMENT", ""),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"다음 영어 자막을 한국어로 요약해 주세요:\n\n{transcript}"},
        ],
    )
    return completion.choices[0].message.content


def insights_ko(text, client=None):
    """자막에서 한국어 핵심 인사이트(글머리표)를 추출한다."""
    if client is None:
        client = _build_client()

    transcript = text[:MAX_CHARS]
    completion = client.chat.completions.create(
        model=os.environ.get("AOAI_DEPLOYMENT", ""),
        messages=[
            {"role": "system", "content": INSIGHTS_PROMPT},
            {"role": "user", "content": f"다음 자막에서 핵심 인사이트를 한국어로 뽑아 주세요:\n\n{transcript}"},
        ],
    )
    return completion.choices[0].message.content
