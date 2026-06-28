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
  copilot-instructions.md  # Superpowers 뒤 Azure 단계 잇기
  agents/azure-deploy.md   # 배포자 (키리스, 단일 RG, URL)
  skills/azure-provision/  # 리소스→Azure 매핑 (DB→Azure DB)
  instructions/keyless...  # 키리스·정리 가드레일
```

## 사용
```bash
bash install.sh && copilot
# Superpowers로 만들고 → "Azure에 배포해줘" → 🌐 URL
```

전제: Azure 구독·권한. 범위 밖: 비용·스케일·모니터링.
