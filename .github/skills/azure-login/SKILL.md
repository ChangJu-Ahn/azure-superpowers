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
6. 실패면 `로그인: 실패`로 적고, **반환된 에러로 원인을 짚어 다음 행동을 안내**한 뒤 작업 중단.

## 실패 시 가이드 (반환값 → 할 일)
에러 메시지를 그대로 두지 말고 진단해서 한 줄 처방을 준다.
- **미로그인**(`Please run 'az login'`): 로그인 창 다시 열기. 안 뜨면 `az login --use-device-code`.
- **구독 없음/비활성**(`No subscriptions found`): 구독 활성화 또는 다른 계정/테넌트 — `az login --tenant <id>`.
- **RG 생성 권한 없음**(`AuthorizationFailed`): 구독에 **Contributor** 필요. 관리자에게 역할 요청, 안내문 제공.
- **리전 정책 차단**(`RequestDisallowedByPolicy`): 정책 허용 리전 확인 → 한국 외면 사용자에게 대안 리전 제안.
- **프로바이더 미등록**(`MissingSubscriptionRegistration`): `az provider register --namespace <ns>` 자동 실행 후 재시도.
- **CLI 없음/구버전**: `az version` 확인, 설치/업그레이드 안내.
판단 불가하면 에러 원문을 사용자에게 보여주고 멈춘다(추측 금지).

## 규칙
- 사용자에게 `az` 명령은 숨긴다(클릭만). 키 안 만든다(키리스).
- 로그인 성공 전에는 ideation/코딩으로 넘어가지 않는다.
