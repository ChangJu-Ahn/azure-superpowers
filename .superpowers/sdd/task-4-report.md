# Task 4 보고서: web (FastAPI 목록·갱신)

## 상태
완료 (PASS). app/.venv pytest 12 passed.

## 생성 파일
- `app/main.py`: FastAPI. `GET /` 목록(채널·시간 내림차순, store.list_videos 활용)+한국어 요약, `POST /refresh` → fetch_recent → fetch_transcript(없으면 title 폴백) → summarize_ko → upsert_video+save_summary → 303 redirect `/`.
- `app/templates/index.html`: Jinja, 한국어 UI(새로 고침/요약 없음).
- `app/tests/test_web.py`: TestClient. `/` 200·요약 노출, `/refresh` save 호출.

## 테스트
`app/.venv/bin/pytest app/tests/` → 12 passed (web 2건 포함).

## 우려/메모
- DB: PGHOST 있으면 psycopg(키리스), 없으면 SQLite(APP_DB_PATH). FastAPI Depends(get_conn)로 테스트 오버라이드.
- requirements에 fastapi/jinja2/httpx 필요(설치됨). 배포는 후속 단계.
