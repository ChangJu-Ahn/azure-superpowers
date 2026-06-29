# MS YouTube 인사이트 앱 — 설계

## 목표
Microsoft, Microsoft Developer, Microsoft Korea 세 YouTube 채널의 신규 영상 자막을 수집하여
**한국어 요약**을 생성·저장하고, 웹에서 채널·시간순으로 조회한다. 원본 자막은 대부분 영어,
요약은 한국어로 통일한다.

## 범위 (MVP)
- 3개 채널 신규 영상 메타데이터 수집
- 자막(transcript) 수집 (영어 위주)
- Azure OpenAI로 영어→한국어 요약 생성
- PostgreSQL에 영상/자막/요약 누적
- 웹 화면: 채널·시간순 목록 + 요약 보기 + "갱신" 버튼
- 갱신: 배치(스케줄) + 수동 버튼 둘 다

## 비범위
비용·스케일·트래픽·이중화·고급 모니터링·CI/CD·추천/검색 고도화. 한국·퍼블릭·최소 SKU.

## 아키텍처 (단일 RG, 키리스)
- **App Service (Python / FastAPI + Jinja)** — 조회 화면 + 수동 갱신 트리거
- **Azure DB for PostgreSQL (Flexible, 최소 SKU)** — 영상/자막/요약 저장, 관리 ID + RBAC
- **Azure OpenAI** — 한국어 요약, DefaultAzureCredential 키리스
- **수집 배치** — 하루 1회 스케줄(예: App Service cron/타이머) + 웹 버튼 수동 실행
- **YouTube Data API** — 채널 영상 목록 조회 (API 키 1개 환경변수, 불가피)
- 자막은 transcript 라이브러리로 수집

## 컴포넌트 경계
- `fetcher` — YouTube 영상 목록 + 자막 수집. 입력: 채널ID. 출력: 영상 메타+자막 텍스트.
- `summarizer` — 영어 자막 → 한국어 요약. Azure OpenAI 호출. 입력: 자막. 출력: 요약문.
- `store` — PostgreSQL CRUD. 영상/자막/요약 누적, 중복 방지.
- `web` — FastAPI 라우트(목록·상세·갱신) + Jinja 템플릿.
각 컴포넌트는 독립 테스트 가능.

## 데이터 모델
- `videos`: id(YouTube), channel, title, published_at, url, fetched_at
- `transcripts`: video_id(FK), lang, text
- `summaries`: video_id(FK), lang(ko), text, model, created_at

## 데이터 흐름
신규 영상 조회 → 자막 수집 → Azure OpenAI 한국어 요약 → PostgreSQL 저장 → 웹 조회.

## 오류 처리
- 자막 없는 영상: 제목+설명으로 요약 폴백
- API 한도/실패: 재시도 후 스킵, 다음 갱신 때 재시도
- 중복 영상: id 기준 upsert

## 테스트
fetcher/summarizer/store는 모킹으로 단위 테스트, web은 라우트 스모크 테스트.

## 비밀/키리스
YouTube API 키만 환경변수. Azure OpenAI·PostgreSQL은 DefaultAzureCredential + 관리 ID + RBAC.
