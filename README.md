# azure-superpowers

> **Azure deployment layer for [Superpowers](https://github.com/obra/superpowers).**
> 가장 인기 있는 GHCP 하네스에 Azure를 입힌다 — 코드에서 멈추지 않고 **살아있는 Azure URL**까지.

가장 인기 있는 하네스를 이기려는 게 아니다. **Superpowers가 spec→TDD→리뷰로 코드를 완성**하면,
이 레이어가 그 뒤를 이어 **키리스·단일 RG**로 Azure에 띄운다. (obra/superpowers, MIT — 위에 얹는 애드온)

## 한 줄
Superpowers의 깊이 + Azure 배포 = 아이디어를 **GHCP만으로** Azure URL까지.

## 차별점
- **Superpowers엔 없는 Azure 배포**: App Service + DB까지. Superpowers가 쪼갠 스키마 → **Azure DB로**.
- **키리스(관리 ID)**: 유출될 키를 안 만든다.
- **단일 RG + 자원 대장**: `az group delete` 한 방으로 정리.
- 🪿 Azure 전용(AWS/GCP는 정중히 거절).

## 구조
```
install.sh                 # Superpowers 설치 + 이 레이어 안내
.github/
  copilot-instructions.md  # Superpowers 뒤 Azure 단계 잇기 + DB 선택 게이트
  agents/azure-deploy.md   # 배포자 (키리스, 단일 RG, URL)
  skills/azure-login/      # ⛔ 0순위: az 로그인·권한 체크부터
  skills/azure-provision/  # 리소스→Azure 매핑 (DB→Azure DB)
  instructions/keyless...  # 키리스·정리 가드레일
```

## 흐름 — Superpowers의 실행력 × Azure 배포
Superpowers가 아이디어를 검증된 코드로 만들고, 이 레이어가 그 코드를 살아있는 URL로 잇는다.

| 단계 | 주체 | 하는 일 |
|---|---|---|
| **0. 로그인 게이트** | 🪿 우리 | `azure-login`이 az 로그인·권한 확인 → `.azure-deploy/login-status.md` 기록. 실패 시 작업 중단 |
| **0.5 DB 선택** | 🪿 우리 | 간단(파일/SQLite) vs 정식(PostgreSQL). 정식이면 처음부터 PostgreSQL 전제로 코딩 |
| **1. 브레인스토밍** | 💪 SP | `brainstorming`으로 의도·요구·설계 탐색 |
| **2. 계획** | 💪 SP | `writing-plans`로 spec→단계별 구현 계획 |
| **3. TDD 구현** | 💪 SP | `test-driven-development` 빨강→초록→리팩터, 서브에이전트 병렬 |
| **4. 리뷰·검증** | 💪 SP | `requesting-code-review`+`verification-before-completion`으로 완성 보증 |
| **5. 매핑** | 🪿 우리 | `azure-provision`: 코드가 요구하는 리소스 → App Service·Azure DB로 |
| **6. 배포** | 🪿 우리 | `azure-deploy`: 키리스·단일 RG로 올려 🌐 URL, `resources.md` 기록 |

💪 SP = Superpowers(전역) · 🪿 = azure-superpowers(이 레이어)

## Superpowers보다 Azure에 특화된 점
- **코드에서 안 멈춘다**: SP는 코드 완성이 끝. 우리는 App Service + Azure DB로 **실제 URL**까지.
- **키리스 강제(관리 ID + RBAC)**: 연결문자열·API 키를 코드/커밋에 절대 안 만든다. SP엔 없는 Azure 보안 기본기.
- **0순위 로그인 게이트 + 진단·가이드**: 시작부터 az 로그인·권한 확인. 실패하면 반환 에러로 원인을 짚어 **할 일까지 안내**(Contributor 역할 요청·테넌트 전환·리전·프로바이더 등록). "만들고 나서 배포 안 됨"을 원천 차단.
- **DB도 Azure로**: SP가 쪼갠 스키마를 Azure DB for PostgreSQL에 키리스로 연결.
- **단일 RG + 자원 대장**: 모든 자원을 `rg-<앱>`에. `az group delete` 한 방 정리, 비용 사고 방지.
- **한국·퍼블릭·최소 SKU 기본**, MVP 경계 분명. 🪿 AWS/GCP는 정중히 거절.

## 사용
```bash
# 1) 한 번만: Superpowers(전역) + Azure 레이어(이 폴더) 준비
bash install.sh

# 2) 이 폴더에서 Copilot 실행 (Azure 레이어가 로드됨)
cd azure-superpowers && copilot
```
그다음 평소처럼 Superpowers에게 말한다:
```text
"방명록 웹앱 만들어줘"        # → 0순위 로그인 게이트 → DB 선택 → Superpowers가 spec·TDD로 완성
"Azure에 배포해줘"           # → azure-provision/deploy가 키리스·단일 RG로 → 🌐 URL
```
정리: `az group delete -n rg-<앱> --yes` 한 방.

전제: Azure 구독·권한. 범위 밖: 비용·스케일·모니터링.
