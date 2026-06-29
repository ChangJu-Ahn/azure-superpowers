#!/bin/bash
# App Service 시작 스크립트: uvicorn으로 FastAPI 앱 구동.
set -e
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
