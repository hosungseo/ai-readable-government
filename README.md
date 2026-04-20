# ai-readable-government

`ai-readable-government`는 기존 정부 API와 공개 문서 코퍼스를 **AEO(Agentic Engine Optimization) 기준으로 다시 정렬해**, 사람과 AI 에이전트가 더 잘 찾고, 읽고, 활용할 수 있게 만드는 **public reader and discovery layer**입니다.

이 저장소는 정부 보도자료, 관보, 국무회의 회의록 같은 원천 문서를 readable corpus로 묶고, 동시에 `robots.txt`, `sitemap.xml`, `llms.txt`, `agent-catalog.json` 같은 agent-facing surface를 제공합니다. 즉, 단순 프록시가 아니라 **reader layer + agent discovery layer + transition-request / transition-intelligence layer**를 함께 설계하는 프로젝트입니다.

## Live
- GitHub Pages: <https://hosungseo.github.io/ai-readable-government/>
- Press source repo: <https://github.com/hosungseo/gov-press-md>
- Gazette source repo (공개본): <https://github.com/hosungseo/ai-readable-gazette-kr>
- Cabinet minutes + candidate links repo: <https://github.com/hosungseo/gungmuhoeui-briefing-links>
- File-to-API transition repo: <https://github.com/hosungseo/public-data-portal-intelligence>

## English summary
`ai-readable-government` is a public reader and discovery layer for Korean government data. Rather than trying to become the authoritative API for every dataset, it reorganizes existing public APIs and document corpora around AEO so both humans and AI agents can discover, read, and use them more effectively.

## 프로젝트 정의
- `gov-press-md` = 정부의 설명, 보도, 브리핑 레이어
- `ai-readable-gazette-kr` = 정부의 공식 기록, 고시, 공고 레이어
- `gungmuhoeui-briefing-links` = 국무회의 회의록과 발언 단위를 중심으로 관보·보도자료 후보 링크까지 묶는 회의록/링크 레이어
- `public-data-portal-intelligence` = 파일데이터→API 전환 후보를 구조화하는 transition-request / transition-intelligence 레이어
- `ai-readable-government` = 이 축들을 함께 읽게 하는 public reader and discovery layer

## 3가지 방향

### 1. API 집합 레이어
이미 존재하는 정부 API를 한곳에서 발견하고 읽을 수 있게 정리하는 층입니다. 이 저장소가 모든 데이터를 직접 제공하기보다, 어디에 무엇이 있고 어떻게 접근해야 하는지 보여 주는 catalog 성격을 가집니다.

### 2. Readable corpus 레이어
관보, 보도자료, 국무회의 회의록 같은 공개 문서를 사람이 읽기 쉽고 AI가 처리하기 쉬운 corpus로 다시 묶는 층입니다. sample reader, metadata, source link, full corpus discovery가 이 축에 속합니다.

현재 이 그룹에는 `gov-press-md`, `ai-readable-gazette-kr`, `gungmuhoeui-briefing-links`가 함께 들어갑니다. 특히 `gungmuhoeui-briefing-links`는 국무회의록 Markdown 자체가 1차 가치이고, 여기에 관보·보도자료 후보 링크를 붙여 추가 부가가치를 만드는 2차 레이어라는 점에서 중요합니다.

### 3. File-to-API transition request 레이어
파일데이터를 이 저장소가 직접 authoritative API로 바꾸는 것이 아니라, 어떤 데이터가 API 전환 대상으로 구조화되어야 하는지 드러내는 층입니다. 즉, 전환 실행기라기보다 전환 필요성과 우선순위를 드러내는 요청 레이어입니다.

현재 이 축의 연결 저장소는 [`public-data-portal-intelligence`](https://github.com/hosungseo/public-data-portal-intelligence)입니다. 이 저장소는 파일데이터를 바로 공식 API로 대체하는 제품이 아니라, 전환 후보를 검토하고 구조화하는 transition-intelligence queue / reader 성격을 가집니다.

## 현재 프로토타입 상태
사람용 리더 프로토타입은 샘플 인덱스 기준, 에이전트용 카탈로그는 전체 코퍼스 기준입니다.

**사람 리더 샘플 (`docs/index-data.json`)**
- 반영 범위: **2024-01-01 ~ 2026-04-08**
- press sample total: **34,134**
- gazette sample total: **48,614**
- date groups: **710**
- institution groups: **130**

**에이전트 카탈로그 (`agent-catalog.json`, 주 1회 재빌드)**
- **press 전체**: **165,938** 문서 (`2020-01-01 ~ 2026-04-11`, 소스 `gov-press-md` 실제 문서 기준)
- **gazette 전체**: **128,403** 문서 (`2020-01-02 ~ 2026-04-07`, 소스 `ai-readable-gazette-kr` `derived/readable-corrected/`)

> 참고: press 전체 수치는 날짜 디렉터리용 `README.md`를 제외한 실제 문서 수입니다. 사람용 샘플 인덱스와 전체 코퍼스 수치를 섞지 않도록 분리해 표기합니다.

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
- `ai-readable-gazette-kr` = 관보 DB (OCR 보정 corrected 코퍼스 포함, public)
- `gungmuhoeui-briefing-links` = 국무회의록 Markdown + 관보·보도자료 후보 링크 레이어
- `public-data-portal-intelligence` = 파일데이터→API 전환 후보 검토/구조화 레이어 (transition-request / transition-intelligence)
- `ai-readable-government` = 위 4축을 함께 읽게 하는 public reader 프로토타입 + 에이전트 발견 레이어 허브

## 이 저장소에 포함된 것
- 정적 HTML 기반 reader prototype
- 통합 샘플 인덱스(`docs/index-data.json`)
- 날짜별 / 기관별 browse 데이터
- 디자인 및 정보구조 문서

## 주요 문서
- `DESIGN.md` — 디자인 시스템과 제품 톤
- `docs/IA.md` — 정보구조와 화면 설계 초안
- `docs/INDEXES.md` — 샘플 인덱스 계층과 공통 스키마 메모
- `docs/AEO-CHECKLIST.md` — agent-friendly 공개 표면 점검 체크리스트
- `docs/index-data.json` — 프론트엔드가 읽는 통합 샘플 인덱스

## 데이터 생성 방식
메인 프로토타입은 HTML 내부 하드코딩 데이터 대신 `docs/index-data.json`을 읽습니다.

생성 스크립트:
```bash
python3 scripts/build_sample_indexes.py
```

기본 동작:
- `gov-press-md`에서 보도자료 샘플 추출
- `ai-readable-gazette-kr`에서 관보 샘플 추출
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
