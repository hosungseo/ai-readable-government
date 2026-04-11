# Ai readable government

정부 문서를 사람이 읽고 AI가 처리하기 쉬운 형태로 다시 제공하는 공공 문서 리더 프로젝트.

## Live
- GitHub Pages: <https://hosungseo.github.io/ai-readable-government/>
- Press source repo: <https://github.com/hosungseo/gov-press-md>
- Gazette source repo: <https://github.com/hosungseo/gov-gazette-md>

## 제품 한 줄 정의
- `gov-press-md`는 정부의 **설명/보도 레이어**
- `gov-gazette-md`는 정부의 **공식 기록 레이어**
- `Ai readable government`는 이 둘을 한 인터페이스에서 읽게 하는 **공공 문서 리더**

## 지금 반영된 범위
현재 프로토타입은 누적 기준으로 다음 범위를 반영합니다.
- `2024-01-01 ~ 2026-04-08`
- press sample total: `34134`
- gazette sample total: `48614`
- date groups: `710`
- institution groups: `130`
- press source corpus: `75842`
- gazette source corpus: `about 100k`

## 핵심 원칙
- source first
- readable second
- hype never
- trust over dashboard
- archive over campaign

## 이 프로젝트가 하는 일
이 프로젝트는 정부 문서를 단순히 링크하는 것이 아니라,
**git-backed public document DB를 읽는 리더**를 목표로 합니다.

구조는 다음과 같습니다.
- `gov-press-md` = 보도자료 DB
- `gov-gazette-md` = 관보 DB
- `ai-readable-government` = 그 DB를 읽는 public reader

사용자는 한 화면 안에서:
- press / gazette 두 레이어를 구분해 보고
- 날짜별로 흐름을 훑고
- 기관별로 문서 흐름을 보고
- 원문 source 링크와 metadata/readable 관계를 함께 볼 수 있습니다.

## 문서
- `DESIGN.md` — 디자인 시스템과 제품 톤
- `docs/IA.md` — 정보구조 및 화면 설계 초안
- `docs/INDEXES.md` — 샘플 인덱스 계층과 공통 스키마 메모
- `docs/index-data.json` — 프론트엔드가 읽는 통합 샘플 인덱스

## 샘플 데이터 일반화
메인 프로토타입은 HTML 내부 하드코딩 데이터 대신 `docs/index-data.json`을 읽습니다.

생성 스크립트:
```bash
python3 scripts/build_sample_indexes.py
```

기본 동작:
- `gov-press-md`에서 보도자료 샘플 추출
- `gov-gazette-md`에서 관보 샘플 추출
- 아래 파일 생성/갱신
  - `docs/press-sample.json`
  - `docs/gazette-sample.json`
  - `docs/by-date.json`
  - `docs/by-institution.json`
  - `docs/index-data.json`

예시:
```bash
python3 scripts/build_sample_indexes.py --day 2026-04-06 --press-limit 10 --gazette-limit 10
python3 scripts/build_sample_indexes.py --start-day 2025-01-01 --end-day 2026-04-08 --press-limit-per-day 24 --gazette-limit-per-day 24
```

범위 모드에서는 여러 날짜의 샘플을 합쳐:
- `press`
- `gazette`
- `byDate`
- `byInstitution`
를 다시 계산합니다.

## 알려진 한계
- 현재는 정적 HTML 프로토타입 기반입니다.
- 브라우저 툴 스냅샷은 데이터가 커지면 payload limit에 걸릴 수 있습니다.
- 관보 원천 API에는 확인된 장애 구간이 있습니다.
  - 예: `2025-09-22 ~ 2025-09-25` → `302 APPLICATION_ERROR`
  - 이 구간은 로컬 파이프라인 문제가 아니라 upstream outage hole로 취급합니다.

## 다음 단계
- browse 정렬/필터 강화
- 정적 HTML을 앱 구조로 승격
- sample index를 실제 browseable reader 데이터 계층으로 확장
