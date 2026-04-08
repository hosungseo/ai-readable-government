# INDEXES.md

`Ai readable government`는 두 개의 **git-backed public document DB**를 읽는 리더입니다.

- `gov-press-md` = press DB
- `gov-gazette-md` = gazette DB
- `ai-readable-government` = DB browse / reader layer

즉 이 문서는 단순 샘플 메모가 아니라,
리더가 어떤 **파일 기반 DB 스키마와 인덱스 계층**을 읽는지 설명하는 문서입니다.

## 인덱스 계층
### 1) source DB layer
- `gov-press-md/data/...`
- `gov-gazette-md/data/...`
- `gov-gazette-md/readable-final/...`
- `gov-gazette-md/opendataloader-output/...`

### 2) reader index layer
- `docs/press-sample.json`
- `docs/gazette-sample.json`
- `docs/by-date.json`
- `docs/by-institution.json`
- `docs/index-data.json`

### 3) UI layer
- `index.html`
- `styles.css`

## 생성 파일
- `docs/index-data.json`
  - 메인 프로토타입이 읽는 통합 엔트리
  - `press`, `gazette`, `byDate`, `byInstitution` 포함
- `docs/press-sample.json`
  - 보도자료 샘플 목록
- `docs/gazette-sample.json`
  - 관보 샘플 목록
- `docs/by-date.json`
  - 날짜 기준 그룹 인덱스
- `docs/by-institution.json`
  - 기관 기준 그룹 인덱스

## 공통 document schema
이 리더는 레이어가 달라도 공통 필드로 먼저 읽습니다.

| 필드 | 의미 |
|---|---|
| `layer` | `press` 또는 `gazette` |
| `title` | 문서 제목 |
| `institution` | 기관/부처 이름 |
| `date` | 정규화된 날짜 |
| `docType` | 문서 유형 |
| `path` | source repo 안의 대표 경로 |

## 레이어별 확장 필드
### Press
| 필드 | 의미 |
|---|---|
| `newsItemId` | 정책브리핑 문서 식별자 |
| `originalUrl` | 원문 URL |
| `source` | 데이터 출처 식별 |
| `groupingCode` | 보도자료 유형/그룹 |

### Gazette
| 필드 | 의미 |
|---|---|
| `basisLaw` | 근거법령 |
| `pdfUrl` | 원문 PDF 링크 |
| `hasRaw` | raw 추출 존재 여부 |
| `hasReadable` | readable-final 존재 여부 |
| `metaPath` | metadata md 경로 |
| `rawPath` | raw md/json 경로 |
| `readablePath` | readable-final 경로 |

## 인덱스 = materialized browse views
리더 인덱스는 원본 문서를 대체하지 않습니다.
원본 레코드를 빠르게 탐색하기 위한 **materialized browse views**로 취급합니다.

- `press` / `gazette` = 샘플 레코드 목록
- `byDate` = 날짜 그룹 뷰
- `byInstitution` = 기관 그룹 뷰
- `index-data.json` = UI가 읽는 통합 엔트리

## 생성 명령
```bash
python3 scripts/build_sample_indexes.py
```

옵션 예시:
```bash
python3 scripts/build_sample_indexes.py --day 2026-04-06 --press-limit 10 --gazette-limit 10
python3 scripts/build_sample_indexes.py --start-day 2025-01-01 --end-day 2026-04-08 --press-limit-per-day 24 --gazette-limit-per-day 24
```

## 현재 누적 반영 상태
현재 누적 기준:
- range: `2025-01-01 ~ 2026-04-08`
- press: `9391`
- gazette: `7175`
- by-date groups: `462`
- by-institution groups: `94`

## known gaps / policy notes
- 관보 원천 API에는 확인된 장애 구간이 있음
  - `2025-09-22 ~ 2025-09-25`
  - `302 APPLICATION_ERROR`
- 이 구간은 로컬 파이프라인 오류가 아니라 **upstream outage hole**로 취급
- 리더 레이어는 이런 공백을 숨기기보다, source DB 정책과 함께 설명 가능한 상태를 유지하는 방향을 지향

## 다음 확장
- quick filter (`press-heavy`, `gazette-heavy`, `recent`)
- 정렬 모드 선택
- period slice별 browse 강화
- 정적 HTML에서 앱 구조로 승격
