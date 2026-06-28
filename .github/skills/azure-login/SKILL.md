---
name: azure-login
description: "어떤 작업이든 시작 전에 가장 먼저 Azure 로그인·권한을 확인할 때 발동. az login을 대신 실행해 사용자는 클릭만, 구독·기본 권한을 점검하고 .azure-deploy/login-status.md에 기록한다. 미로그인이면 여기부터 시작."
---

# azure-login — 0순위 게이트

배포가 목적인 하네스다. **로그인이 안 되면 아무리 잘 만들어도 배포 불가** → 가장 먼저 확인한다.

## 절차
1. `.azure-deploy/login-status.md` 확인. `로그인: 성공`이면 통과.
2. 아니면: "Azure에 연결할게요. 로그인 창이 열립니다…" → `az login` 실행, 사용자는 계정 클릭만.
3. `az account show`로 구독 확인. 여러 개면 기본 제안.
4. 권한 간단 점검: `az group create -n rg-precheck-tmp -l koreacentral` → 성공 시 즉시 `az group delete -n rg-precheck-tmp --yes --no-wait` (생성권한 확인용, 흔적 제거).
5. 결과 기록:
```
# Azure 로그인 상태
- 로그인: 성공
- 계정: <email>
- 구독: <id>
- RG 생성권한: OK
- 확인시각: <ts>
```
6. 실패면 `로그인: 실패`로 적고 사용자에게 알린 뒤 작업 중단.

## 규칙
- 사용자에게 `az` 명령은 숨긴다(클릭만). 키 안 만든다(키리스).
- 로그인 성공 전에는 ideation/코딩으로 넘어가지 않는다.
