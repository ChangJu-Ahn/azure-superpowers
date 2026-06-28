#!/usr/bin/env bash
# azure-superpowers — Superpowers 위에 Azure 배포 레이어를 얹는다.
# Superpowers는 의존성으로 "설치"만 하고, 이 repo는 .github/의 Azure 자산만 제공한다.
set -euo pipefail
cd "$(dirname "$0")"

echo ">> 1) Superpowers(GHCP) 설치"
copilot plugin marketplace add obra/superpowers-marketplace || true
copilot plugin install superpowers@superpowers-marketplace || true

echo ">> 2) Azure 레이어(.github/) 는 이 폴더에 이미 있음 — copilot을 이 폴더에서 실행하면 로드됨"
echo "   agents: azure-deploy / skills: azure-provision / instructions: keyless"

echo ">> 완료. 사용: cd $(pwd) && copilot"
