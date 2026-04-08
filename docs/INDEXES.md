# INDEXES.md

`Ai readable government`의 현재 샘플 인덱스 계층입니다.

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

## 현재 스키마 방향
공통 필드:
- `layer` — `press` | `gazette`
- `title`
- `institution`
- `date`
- `docType`
- `path`

레이어별 추가 필드:
- Press: `newsItemId`, `originalUrl`, `source`, `groupingCode`
- Gazette: `basisLaw`, `pdfUrl`, `hasRaw`, `hasReadable`, `metaPath`, `rawPath`, `readablePath`

## 생성 명령
```bash
python3 scripts/build_sample_indexes.py
```

옵션 예시:
```bash
python3 scripts/build_sample_indexes.py --day 2026-04-06 --press-limit 10 --gazette-limit 10
python3 scripts/build_sample_indexes.py --start-day 2026-04-01 --end-day 2026-04-08 --press-limit-per-day 8 --gazette-limit-per-day 8
```

## 현재 범위 샘플 상태
`2026-04-01 ~ 2026-04-08` 샘플 생성 기준:
- press: 61건
- gazette: 40건
- by-date groups: 8개
- by-institution groups: 23개

## 다음 확장
- 하루 샘플이 아니라 기간 단위 인덱스 생성
- 기관 alias 정규화
- by-date / by-institution 전용 화면 연결
- 공통 document schema를 고정한 뒤 앱 레이어로 승격
