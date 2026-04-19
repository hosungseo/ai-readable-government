# ai-readable-government

정부 문서를 **사람이 읽기 쉽고 AI가 처리하기 쉬운 형태**로 다시 보여 주는 공공 문서 리더 프로젝트입니다.

이 저장소는 단순 링크 모음이 아니라, `gov-press-md`와 `gov-gazette-md` 같은 공개 문서 DB를 하나의 읽기 경험으로 묶는 **reader layer**를 목표로 합니다.

## Live
- GitHub Pages: <https://hosungseo.github.io/ai-readable-government/>
- Press source repo: <https://github.com/hosungseo/gov-press-md>
- Gazette source repo (공개본): <https://github.com/hosungseo/ai-readable-gazette-kr>

## 한 줄 정의
- `gov-press-md` = 정부의 설명, 보도, 브리핑 레이어
- `gov-gazette-md` = 정부의 공식 기록, 고시, 공고 레이어
- `ai-readable-government` = 이 둘을 함께 읽게 하는 공공 문서 리더

## 현재 프로토타입 상태
사람용 리더 프로토타입은 샘플 인덱스 기준, 에이전트용 카탈로그는 전체 코퍼스 기준입니다.

**사람 리더 샘플 (`docs/index-data.json`)**
- 반영 범위: **2024-01-01 ~ 2026-04-08**
- press sample total: **34,134**
- gazette sample total: **48,614**
- date groups: **710**
- institution groups: **130**

**에이전트 카탈로그 (`agent-catalog.json`, 주 1회 재빌드)**
- **press 전체**: 168,225 문서 (`2020-01-01 ~ 2026-04-11`, 소스 `gov-press-md`)
- **gazette 전체**: 128,403 문서 (`2020-01-02 ~ 2026-04-07`, 소스 `ai-readable-gazette-kr` `derived/readable-corrected/`)

## 핵심 원칙
- source first
- readable second
- hype never
- trust over dashboard
- archive over campaign

## 이 프로젝트가 하는 일
이 프로젝트는 정부 문서를 단순히 링크하는 대신, **source + metadata + readable layer**를 한 화면 안에서 함께 보여 주려 합니다.

사용자는 한 인터페이스에서:
- press / gazette 두 레이어를 구분해 보고
- 날짜별 흐름을 훑고
- 기관별 문서 흐름을 탐색하고
- 원문 링크와 readable representation의 관계를 함께 볼 수 있습니다.

## 저장소 관계
- `gov-press-md` = 보도자료 DB (public)
- `ai-readable-gazette-kr` = 관보 DB 공개본 (OCR 보정 corrected 코퍼스 포함, public)
- `gov-gazette-md` = 관보 원본 + derived 작업 저장소 (private)
- `ai-readable-government` = public reader 프로토타입 + 에이전트 발견 레이어 허브

## 이 저장소에 포함된 것
- 정적 HTML 기반 reader prototype
- 통합 샘플 인덱스(`docs/index-data.json`)
- 날짜별 / 기관별 browse 데이터
- 디자인 및 정보구조 문서

## 주요 문서
- `DESIGN.md` — 디자인 시스템과 제품 톤
- `docs/IA.md` — 정보구조와 화면 설계 초안
- `docs/INDEXES.md` — 샘플 인덱스 계층과 공통 스키마 메모
- `docs/index-data.json` — 프론트엔드가 읽는 통합 샘플 인덱스

## 데이터 생성 방식
메인 프로토타입은 HTML 내부 하드코딩 데이터 대신 `docs/index-data.json`을 읽습니다.

생성 스크립트:
```bash
python3 scripts/build_sample_indexes.py
```

기본 동작:
- `gov-press-md`에서 보도자료 샘플 추출
- `gov-gazette-md`에서 관보 샘플 추출
- 아래 파일 생성 또는 갱신
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

## 현재 한계
- 아직은 **정적 HTML 프로토타입** 중심입니다.
- 현재 노출 범위는 전체 원천 DB가 아니라 **샘플 인덱스 계층**입니다.
- 브라우저 스냅샷 계열 도구는 데이터가 커지면 payload limit에 걸릴 수 있습니다.
- 관보 원천 API에는 upstream 장애 구간이 존재합니다.
  - 예: `2025-09-22 ~ 2025-09-25` → `302 APPLICATION_ERROR`

## 다음 단계
- browse 정렬과 필터 강화
- 정적 HTML에서 앱 구조로 승격
- 샘플 인덱스를 실제 browseable reader 데이터 계층으로 확장
- press와 gazette를 넘나드는 cross-link UX 보강

## Agent-ready layer

In addition to the human-browsable reader, the site serves a machine-readable
discovery layer so external AI agents can enumerate and consume the underlying
markdown corpora directly.

- Machine catalog: [`/agent-catalog.json`](https://hosungseo.github.io/ai-readable-government/agent-catalog.json)
- Sitemap index: [`/sitemap.xml`](https://hosungseo.github.io/ai-readable-government/sitemap.xml)
- LLM summary: [`/llms.txt`](https://hosungseo.github.io/ai-readable-government/llms.txt)
- Crawler policy: [`/robots.txt`](https://hosungseo.github.io/ai-readable-government/robots.txt)

The catalog points agents at `raw.githubusercontent.com` URLs in the source
markdown repos (`gov-press-md`, `ai-readable-gazette-kr`); this repo itself
stores only the catalog and sitemap artifacts, rebuilt weekly via GitHub
Actions (`.github/workflows/rebuild-agent-artifacts.yml`).
