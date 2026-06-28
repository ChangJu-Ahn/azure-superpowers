---
name: azure-provision
description: "코드가 요구하는 리소스(웹앱, DB, 스토리지 등)를 Azure 서비스로 매핑·프로비저닝할 때 발동. Superpowers가 쪼갠 DB 스키마는 Azure DB(PostgreSQL/SQL)로 간다. 키리스·단일 RG·한국 기본."
---

# azure-provision — 리소스를 Azure로 매핑

Superpowers는 "DB가 필요하다"까지만 본다. 여기서 **그 DB를 Azure DB로** 잇는다.

## 매핑
| 코드 요구 | Azure 서비스 | 비고 |
| --- | --- | --- |
| 웹앱 | App Service (Linux, 최소 SKU) | |
| 관계형 DB/스키마 | **Azure DB for PostgreSQL Flexible** | 키리스: 관리 ID + Entra 인증 |
| 파일/blob | Azure Storage | 키리스 RBAC |
| LLM/비전 | Azure OpenAI | 키리스, Cognitive Services OpenAI User |

## 규칙
- 전부 단일 RG `rg-<앱>`, Korea Central, Public, 최소 SKU.
- 연결은 키리스(관리 ID). 연결문자열/키 금지.
- 만든 리소스는 `.azure-deploy/resources.md`에 기록 → azure-deploy가 배포·정리.
- 단순 앱(외부 리소스 불필요)이면 App Service만. 과한 프로비저닝 금지(MVP).
