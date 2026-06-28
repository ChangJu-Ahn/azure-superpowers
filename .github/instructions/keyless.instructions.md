---
applyTo: "**"
---

# 키리스 + 정리 가드레일 (항상)

- **시작 전 로그인 게이트**: 모든 작업은 `.azure-deploy/login-status.md`가 `로그인: 성공`일 때만 진행. 아니면 azure-login 먼저.
- **키리스 강제**: `DefaultAzureCredential` + 관리 ID + RBAC. 계정 키·연결문자열·API 키를 코드/커밋에 절대 금지.
- **단일 RG + 대장**: 모든 Azure 자원은 `rg-<앱>` 하나에. `.azure-deploy/resources.md`에 기록, 삭제는 `az group delete -n rg-<앱> --yes`.
- **의존성 격리**: venv/node_modules 로컬. 전역 설치 금지.
- **MVP 경계**: 비용·스케일·트래픽·이중화·모니터링·CI/CD 안 함. 한국·퍼블릭·최소 SKU.
- 배포는 Superpowers가 코드 완성 후. 이 레이어는 그 뒤만 책임진다.
