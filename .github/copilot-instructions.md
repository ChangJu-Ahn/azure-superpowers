# azure-superpowers (Azure 레이어 — 항상 적용)

이 repo는 **Superpowers를 이긴다**가 아니라, **가장 인기 있는 GHCP 하네스(Superpowers)에 Azure를 입힌다.**
Superpowers가 spec→설계→TDD 구현→리뷰로 **코드를 완성**하면, 여기부터 **Azure 배포 → 살아있는 URL**까지 잇는다.

## ⛔ 0순위 게이트 — Azure 로그인 먼저 (MUST, 무엇보다 먼저)
**아이디어·코드 작업을 시작하기 전에, 반드시 Azure 로그인/권한부터 확인한다.** 열심히 만들고 배포가 안 되면 취지가 무너진다.
1. 모든 작업 시작 시 `.azure-deploy/login-status.md`를 먼저 읽는다.
2. 파일이 없거나 `로그인: 성공`이 아니면 → **즉시 azure-login 스킬 실행**(인터뷰/코딩보다 먼저).
3. `az login` 실행 → `az account show`로 구독 확인 → **간단한 권한 체크**(리소스그룹 생성 권한 등) → 결과를 `.azure-deploy/login-status.md`에 기록.
4. 로그인/권한 실패면 작업을 진행하지 않고 사용자에게 알린다. 성공해야만 다음으로.

## 역할 분담
- **Superpowers**: 요구분석·계획·TDD·서브에이전트 리뷰까지(코드 완성). 그대로 신뢰하고 쓴다.
- **이 레이어(우리)**: 코드 완성 후 **Azure 배포**. 직접 만들지 말고 azure-deploy 에이전트 + azure-provision 스킬 + Microsoft 빌트인 스킬에 위임.

## 항상 지키는 원칙
- **키리스 우선(관리 ID)**: `DefaultAzureCredential` + 시스템 관리 ID + RBAC. 계정 키·연결문자열·API 키 금지.
- **단일 리소스 그룹**: 모든 자원을 `rg-<앱>` 하나에 묶고 `.azure-deploy/resources.md`에 기록 → `az group delete`로 한 번에 정리.
- **한국·퍼블릭·최소 SKU 기본.** 비용·스케일·트래픽·모니터링은 범위 밖(MVP).
- 사용자는 `az`를 몰라도 된다. 로그인은 창 띄우고 클릭만.
- 🪿 재미요소: 다른 클라우드(AWS/GCP) 배포 요청은 정중히 거절하고 Azure만 한다.

## 배포 흐름 (코드 완성 후)
1. **azure-provision**: 코드가 요구하는 리소스 판별(웹앱, DB 등) → Azure 매핑(App Service, Azure DB for PostgreSQL/SQL).
2. **azure-deploy**: 단일 RG에 키리스로 프로비저닝+배포 → URL. 빌트인 `python-appservice-deploy`/`azure-prepare` 위임.
3. resources.md 기록. 증분이면 기존 RG 재사용.
