# Ai readable government

정부 문서를 사람이 읽고 AI가 처리하기 쉬운 형태로 다시 제공하는 리더 프로젝트.

## 제품 한 줄 정의
- `gov-press-md`는 정부의 **설명/보도 레이어**
- `gov-gazette-md`는 정부의 **공식 기록 레이어**
- `Ai readable government`는 이 둘을 한 인터페이스에서 읽게 하는 **공공 문서 리더**

## 핵심 원칙
- source first
- readable second
- hype never
- trust over dashboard
- archive over campaign

## 현재 연결 대상
- Press: https://github.com/hosungseo/gov-press-md
- Gazette: https://github.com/hosungseo/gov-gazette-md

## 문서
- `DESIGN.md` — 디자인 시스템과 제품 톤
- `docs/IA.md` — 정보구조 및 화면 설계 초안
- `docs/INDEXES.md` — 샘플 인덱스 계층과 공통 스키마 메모
- `docs/index-data.json` — 프론트엔드가 읽는 통합 샘플 인덱스

## 샘플 데이터 일반화
이제 메인 프로토타입은 HTML 내부 하드코딩 데이터 대신 `docs/index-data.json`을 읽습니다.

생성 스크립트:
```bash
python3 scripts/build_sample_indexes.py
```

기본 동작:
- `gov-press-md/data/2026/2026-04/2026-04-01/`에서 보도자료 샘플 추출
- `gov-gazette-md/data/...`, `readable-final/...`, `opendataloader-output/...`에서 관보 샘플 추출
- 아래 파일 생성/갱신
  - `docs/press-sample.json`
  - `docs/gazette-sample.json`
  - `docs/by-date.json`
  - `docs/by-institution.json`
  - `docs/index-data.json`

옵션:
```bash
python3 scripts/build_sample_indexes.py --day 2026-04-06 --press-limit 10 --gazette-limit 10
python3 scripts/build_sample_indexes.py --start-day 2026-04-01 --end-day 2026-04-08 --press-limit-per-day 8 --gazette-limit-per-day 8
```

현재는 범위 생성도 지원합니다. 범위 모드에서는 여러 날짜의 샘플을 합쳐:
- `press`
- `gazette`
- `byDate`
- `byInstitution`
를 다시 계산합니다.

## 다음 단계
- 날짜별/기관별 인덱스를 공통 스키마로 확장
- 정적 HTML을 앱 구조로 승격
- 샘플 인덱스에서 실제 browseable reader 데이터 계층으로 전환
