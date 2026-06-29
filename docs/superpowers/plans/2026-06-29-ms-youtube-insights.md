# MS YouTube 인사이트 앱 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Microsoft·Microsoft Developer·Microsoft Korea 채널 신규 영상 자막을 수집해 한국어 요약을 PostgreSQL에 저장하고 웹에서 채널·시간순 조회.

**Architecture:** FastAPI 웹앱이 PostgreSQL의 누적 요약을 조회/표시. fetcher가 YouTube Data API로 영상 목록·자막을 수집, summarizer가 Azure OpenAI로 영어→한국어 요약, store가 PG에 upsert. 배치+수동 갱신.

**Tech Stack:** Python 3.14, FastAPI, Jinja2, psycopg, youtube-transcript-api, google-api-python-client, openai(Azure), DefaultAzureCredential, pytest.

## Global Constraints
- 키리스: Azure OpenAI·PostgreSQL은 DefaultAzureCredential + 관리 ID + RBAC. 코드/커밋에 키 금지.
- YouTube Data API 키만 환경변수 `YOUTUBE_API_KEY` 허용.
- 요약 언어 한국어, 원본 영어 가정. 요약 모델 환경변수 `AOAI_DEPLOYMENT`.
- 앱 코드는 `app/` 하위, 테스트는 `app/tests/`. 의존성은 `.venv` 로컬.
- 채널: Microsoft, Microsoft Developer, Microsoft Korea. 핸들→채널ID는 fetcher가 해석.

---

### Task 1: 프로젝트 스캐폴드 + 데이터 모델
**Files:** Create: `app/requirements.txt`, `app/store.py`, `app/tests/test_store.py`, `app/.env.example`
**Interfaces:** Produces: `init_db(conn)`, `upsert_video(conn, video)`, `save_summary(conn, video_id, lang, text, model)`, `list_videos(conn)`. video keys: id,channel,title,published_at,url.
- [ ] Step1 실패 테스트: sqlite 메모리로 init_db→upsert_video→list_videos 1건.
- [ ] Step2 실패 확인: `pytest app/tests/test_store.py -v` FAIL.
- [ ] Step3 구현: store.py 스키마(videos/transcripts/summaries), upsert(중복 무시), list_videos 정렬.
- [ ] Step4 통과 확인 PASS.
- [ ] Step5 커밋 `feat: store + schema`.

### Task 2: summarizer (Azure OpenAI, 키리스)
**Files:** Create: `app/summarizer.py`, `app/tests/test_summarizer.py`
**Interfaces:** env `AOAI_ENDPOINT`,`AOAI_DEPLOYMENT`. Produces: `summarize_ko(text, client=None) -> str`.
- [ ] Step1 실패 테스트: mock client로 한국어 요약 반환.
- [ ] Step2 FAIL.
- [ ] Step3 구현: DefaultAzureCredential token provider, AzureOpenAI, 한국어 프롬프트, client 주입.
- [ ] Step4 PASS.
- [ ] Step5 커밋 `feat: ko summarizer`.

### Task 3: fetcher (영상 목록 + 자막)
**Files:** Create: `app/fetcher.py`, `app/tests/test_fetcher.py`
**Interfaces:** `fetch_recent(handles, api_key, max_n=5) -> list[dict]`, `fetch_transcript(video_id) -> str|None`.
- [ ] Step1 실패 테스트: mock fetch_recent 리스트, 자막없음 None.
- [ ] Step2 FAIL.
- [ ] Step3 구현: google-api-python-client 핸들→영상, youtube-transcript-api 자막.
- [ ] Step4 PASS.
- [ ] Step5 커밋 `feat: fetcher`.

### Task 4: web (FastAPI 목록·갱신)
**Files:** Create: `app/main.py`, `app/templates/index.html`, `app/tests/test_web.py`
**Interfaces:** Routes `GET /`, `POST /refresh`. Consumes store/fetcher/summarizer.
- [ ] Step1 실패 테스트: TestClient `/` 200, `/refresh` 저장 호출.
- [ ] Step2 FAIL.
- [ ] Step3 구현: FastAPI+Jinja 목록, refresh: fetch→폴백→summarize→save.
- [ ] Step4 PASS.
- [ ] Step5 커밋 `feat: web ui + refresh`.

### Task 5: 배치 + 배포 준비
**Files:** Create: `app/refresh_job.py`, `app/startup.sh`; Modify: `app/.env.example`
- [ ] Step1 refresh_job 진입점.
- [ ] Step2 키리스 env + startup.sh.
- [ ] Step3 커밋 `feat: batch job + deploy prep`.

## Self-Review
- fetcher/summarizer/store/web+배치+키리스 모두 매핑. 플레이스홀더 없음. 시그니처 일관.
