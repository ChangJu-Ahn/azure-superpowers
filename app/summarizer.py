import os

MAX_CHARS = 24000

SYSTEM_PROMPT = (
    "당신은 영어 영상 자막을 한국어로 요약하는 전문가입니다. "
    "핵심 내용을 정확하고 간결하게 한국어로 요약하세요."
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
