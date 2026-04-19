# Agent-Ready Discovery Layer — Design Spec

**Date**: 2026-04-19
**Repo**: `hosungseo/ai-readable-government`
**Status**: Design approved, implementation plan pending
**Related**: [`기획안_에이전트_정부정보_프록시.md`](../../../../../Users/seohoseong/Downloads/기획안_에이전트_정부정보_프록시.md) (origin planning doc, private)

---

## 1. 목표·범위·성공 기준

### 1.1 목표

`ai-readable-government`(정부 공공 문서 리더)에 **에이전트 발견 레이어(agent-ready layer)** 를 얹는다.
사람용 UI는 그대로 두고, 외부 에이전트(Claude / GPT / Perplexity 등)가 이 사이트를 "정부 공공 문서 읽기 허브"로 자동 인식해 관보·보도자료 markdown을 곧장 소비할 수 있게 한다.

### 1.2 이번 사이클 범위 (MVP)

| 항목 | 내용 |
|---|---|
| `robots.txt` | AI 크롤러 전부 allow + `crawl-delay: 1` + `Sitemap:` 라인 |
| `llms.txt` | 사이트 개요·데이터셋 목록·URL 패턴 (llmstxt.org 규격) |
| `sitemap.xml` | 사이트맵 인덱스 (연도·데이터셋별 서브맵 포함) |
| `sitemaps/sitemap-{dataset}-{YYYY}.xml` | 연도별 URL 목록 (50k 한도 내) |
| `agent-catalog.json` | 기계 판독 데이터셋 카탈로그 (스키마 아래 §3) |
| `scripts/build_agent_artifacts.py` | 위 아티팩트 일괄 생성기 |
| `scripts/validate_agent_artifacts.py` | 스키마·샘플 URL 검증기 |
| `.github/workflows/rebuild-agent-artifacts.yml` | 주 1회 cron + 수동 디스패치 |
| `README.md` | "Agent-ready layer" 섹션 1문단 추가 |

### 1.3 범위 밖 (별도 사이클)

- 입법예고(법제처 API) 신규 수집 파이프라인
- `.well-known/mcp.json` · `agent-skills.json` (실제 MCP 서버 구축 사이클에서 추가)
- 읽기 패턴 로깅·인기 문서 집계 (동적 서버 필요)
- 커뮤니티·댓글 엔드포인트
- `Accept: text/markdown` 헤더 분기 및 `x-markdown-tokens` 헤더 (정적 호스팅으로는 불가)

### 1.4 성공 기준 (verifiable)

1. 다음 네 URL이 모두 200으로 응답
   - `https://hosungseo.github.io/ai-readable-government/robots.txt`
   - `https://hosungseo.github.io/ai-readable-government/llms.txt`
   - `https://hosungseo.github.io/ai-readable-government/sitemap.xml`
   - `https://hosungseo.github.io/ai-readable-government/agent-catalog.json`
2. `isitagentready.com` 스캔 결과: Discoverability 100% · Bot Control 100% · Accessibility 부분 · Protocol 부분 (정직하게 수용)
3. 외부 에이전트에 "이 사이트에서 최근 관보 3건을 가져와 요약" 프롬프트 → 카탈로그·sitemap 참조해 `raw.githubusercontent.com` MD 3건 fetch + 요약 성공
4. 기존 사람용 리더에 회귀 없음 (Pages 빌드 녹색, 인덱스·라우트 무변동)

---

## 2. 파일 배치

**전제.** `ai-readable-government` 리포의 `index.html`·`styles.css`가 리포 root에 있고, GitHub Pages가 main branch의 root를 서빙한다 (실측 확인됨). 따라서 에이전트 대상 artifact는 **전부 root level**에 배치. `docs/`는 기존 데이터 JSON 전용으로 둔다.

```
ai-readable-government/
├── index.html                      (existing, no change)
├── styles.css                      (existing, no change)
├── README.md                       EDIT (append "Agent-ready layer" section)
├── DESIGN.md                       (existing, no change)
│
├── robots.txt                      NEW (root — protocol requires /robots.txt)
├── llms.txt                        NEW (root)
├── sitemap.xml                     NEW (root, site-wide sitemap index, 2 entries)
├── agent-catalog.json              NEW (root)
├── sitemaps/                       NEW (root)
│   ├── sitemap-gazette-index.xml      (dataset index → year files)
│   ├── sitemap-gazette-2020.xml
│   ├── sitemap-gazette-2021.xml
│   ├── sitemap-gazette-2022.xml
│   ├── sitemap-gazette-2023.xml
│   ├── sitemap-gazette-2024.xml
│   ├── sitemap-gazette-2025.xml
│   ├── sitemap-gazette-2026.xml
│   ├── sitemap-press-index.xml        (dataset index → year files)
│   ├── sitemap-press-2020.xml
│   ├── sitemap-press-2021.xml
│   ├── sitemap-press-2022.xml
│   ├── sitemap-press-2023.xml
│   ├── sitemap-press-2024.xml
│   ├── sitemap-press-2025.xml
│   └── sitemap-press-2026.xml
│
├── docs/                           (existing data — no change)
│   ├── index-data.json
│   ├── press-sample.json
│   └── gazette-sample.json
│
├── scripts/
│   ├── build_sample_indexes.py     (existing, no change)
│   ├── build_agent_artifacts.py    NEW
│   └── validate_agent_artifacts.py NEW
│
└── .github/workflows/              NEW directory (not yet exist)
    └── rebuild-agent-artifacts.yml NEW
```

**Notes.**
- 보도자료 연도별 파일 수가 50k를 넘는 해가 있으면 빌더가 자동으로 월별 분할(`sitemap-press-2024-01.xml` 등)로 fallback.
- 아티팩트 파일만 커밋됨. 30만 MD 원본은 소스 리포(`gov-gazette-md`, `gov-press-md`)에 그대로 둠 (복제 금지).

---

## 3. `agent-catalog.json` 스키마

### 3.1 전체 구조

```json
{
  "name": "ai-readable-government",
  "description": "Korean government public documents — agent-readable index. Points to source markdown corpora hosted on GitHub.",
  "site_url": "https://hosungseo.github.io/ai-readable-government/",
  "generated_at": "2026-04-19T22:30:00+09:00",
  "generator": "scripts/build_agent_artifacts.py",
  "license_note": "Index/catalog under MIT. Document license varies per dataset — see `license` per dataset.",
  "contact": "https://github.com/hosungseo/ai-readable-government/issues",

  "datasets": [
    {
      "id": "gazette",
      "name": "대한민국 관보 (Government Gazette of Korea)",
      "description": "Official government record layer — 2020-01-02 onward, dictionary-corrected markdown corpus.",
      "format": "text/markdown",
      "total_documents": 128471,
      "date_range": { "start": "2020-01-02", "end": "2026-04-07" },
      "update_cadence": "near-daily (source repo)",
      "license": "Korean Copyright Act Art. 7 — not protected; derived corpus CC0 1.0",
      "source_repo": "hosungseo/gov-gazette-md",
      "variants": [
        {
          "id": "readable-corrected",
          "description": "OCR-corrected, dictionary-based fixup (recommended for LLM consumption).",
          "raw_base": "https://raw.githubusercontent.com/hosungseo/gov-gazette-md/main/derived/readable-corrected/",
          "path_pattern": "{YYYY-MM-DD}/{NNN}_{institution}_{title}.md"
        },
        {
          "id": "readable-final",
          "description": "Pre-correction baseline (for diff / research).",
          "raw_base": "https://raw.githubusercontent.com/hosungseo/gov-gazette-md/main/readable-final/",
          "path_pattern": "{YYYY-MM-DD}/{NNN}_{institution}_{title}.md"
        }
      ],
      "frontmatter_fields": ["title", "publisher", "date", "source_raw_md"],
      "sitemap_url": "https://hosungseo.github.io/ai-readable-government/sitemaps/sitemap-gazette-index.xml",
      "sample_documents": ["..."]
    },
    {
      "id": "press",
      "name": "정부 보도자료 (Government Press Releases)",
      "description": "Government explanatory layer — ministry press releases as markdown.",
      "format": "text/markdown",
      "total_documents": 169801,
      "date_range": { "start": "2020-01-01", "end": "2026-04-18" },
      "update_cadence": "daily (source repo)",
      "license": "See individual ministry terms (public information, generally open).",
      "source_repo": "hosungseo/gov-press-md",
      "variants": [
        {
          "id": "data",
          "description": "Press releases under per-year folders.",
          "raw_base": "https://raw.githubusercontent.com/hosungseo/gov-press-md/main/data/",
          "path_pattern": "{YYYY}/{YYYY-MM-DD}/{...}.md"
        }
      ],
      "frontmatter_fields": ["title", "agency", "date", "source_url"],
      "sitemap_url": "https://hosungseo.github.io/ai-readable-government/sitemaps/sitemap-press-index.xml",
      "sample_documents": ["..."]
    }
  ],

  "how_to_use": [
    "1. GET /agent-catalog.json for machine-readable index.",
    "2. For structure, fetch each dataset's sitemap_url (XML sitemap index).",
    "3. For documents, fetch raw_base + date/path — plain markdown with YAML frontmatter.",
    "4. For a human-browsable reader, see site_url."
  ]
}
```

### 3.2 설계 결정

- **`variants[]`** — 관보의 보정본 / 비보정본처럼 한 데이터셋에 여러 버전이 공존할 때 에이전트가 고를 수 있게 함.
- **`sample_documents`** — 스키마 학습 비용 최소화. 3건만 가져가도 frontmatter·본문 구조 파악 가능.
- **`how_to_use`** — 사람/에이전트 공통 안내. `llms.txt`와 정보 중복이지만 이 파일만 봐도 이해 가능해야 함.
- **`frontmatter_fields`** — YAML 파싱 시 기대 키 선언.
- **`generated_at` + `generator`** — 신선도·재현성 표식.
- **`$schema` 필드 생략** — JSON Schema 파일을 실제로 제공하지 않는 상태에서 선언만 하면 404로 에이전트 신뢰 훼손. 스키마 공개가 필요해지면 그때 `agent-catalog.schema.json`과 함께 도입.

### 3.3 의도적으로 뺀 것

- `x-markdown-tokens` / 파일별 토큰 수 — 30만 파일 계산 비용 대비 효용 낮음.
- `total_size_bytes` — 소스 리포 변화 잦아 stale 위험.

### 3.4 `llms.txt`와의 관계

`llms.txt`는 `agent-catalog.json`의 **사람·에이전트 양쪽이 읽기 편한 prose 축약판**. 동일 스크립트가 두 파일 동시 생성. H1(사이트명) + blockquote(한 줄 설명) + H2(데이터셋별 섹션)로 llmstxt.org 관례를 따른다.

---

## 4. 업데이트 자동화

### 4.1 워크플로우

`.github/workflows/rebuild-agent-artifacts.yml`

```yaml
on:
  schedule:
    - cron: "0 0 * * 1"    # Monday 00:00 UTC (09:00 KST)
  workflow_dispatch: {}

jobs:
  rebuild:
    steps:
      - checkout (this repo)
      - setup Python 3.11
      - pip install jsonschema lxml requests
      - python3 scripts/build_agent_artifacts.py
          # internally does: partial clone of source repos to /tmp, git ls-tree, cleanup
      - python3 scripts/validate_agent_artifacts.py
      - commit + push if diff (message: "Rebuild agent artifacts (YYYY-MM-DD)")
```

### 4.2 빌더 동작

1. **소스 리포 트리 확보 (blob 없는 부분 clone)**:
   ```bash
   for repo in gov-gazette-md gov-press-md; do
     git clone --no-checkout --filter=tree:0 --depth 1 \
       https://github.com/hosungseo/$repo.git /tmp/$repo
     git -C /tmp/$repo ls-tree -r --name-only HEAD > /tmp/$repo.paths
   done
   ```
   - `--filter=tree:0`: tree 객체만, blob(파일 내용) 다운로드 안 함
   - `--no-checkout`: 작업 디렉토리에 파일 펼치지 않음
   - `--depth 1`: 최신 커밋만
   - 전체 경로 획득 비용: 네트워크·디스크 모두 수 초~십수 초
   - **왜 API 아니고 clone**: GitHub `trees?recursive=true`는 `truncated: true` 이슈 있음 (실측 결과 두 소스 리포 모두 트리 반환이 실제 파일 수보다 훨씬 적게 잘림). 부분 clone은 잘림 없음.
   - **소스 리포 접근성 전제**: 두 리포 모두 public. private로 바뀌면 워크플로우에 PAT secret 추가.
2. `*.md` 경로만 필터, 데이터셋별 group.
3. 연도별 bucket → 각 bucket 50k 초과 시 월별 재분할.
4. 카탈로그 메타 재계산:
   - `total_documents` = 실제 카운트
   - `date_range.start` / `date_range.end` = 최소·최대 날짜 폴더
   - `sample_documents` = 각 variant에서 최근 3건 균등 샘플
5. 파일 생성 (3-tier sitemap):
   - `agent-catalog.json` (root)
   - `llms.txt` (root)
   - `sitemap.xml` (root) — 사이트 최상위 인덱스 (entry 2: gazette 데이터셋 인덱스 + press 데이터셋 인덱스)
   - `sitemaps/sitemap-{dataset}-index.xml` — 데이터셋별 인덱스 (entry ~7: 연도별 서브맵)
   - `sitemaps/sitemap-{dataset}-{YYYY}[-{MM}].xml` — 실제 URL 목록
6. `/tmp/gov-*-md` 정리.

### 4.3 검증 단계

`validate_agent_artifacts.py`:
- `agent-catalog.json` → 필수 필드 presence 검증 (빌더 내부에 Python dict로 하드코딩한 스키마에 `jsonschema.validate` 적용). 외부 스키마 파일 의존 없음
- 각 dataset의 `sample_documents[0]` → HEAD 200 확인
- `sitemap.xml` → `lxml`로 파싱, `sitemapindex` 유효성
- 각 dataset-level 인덱스(`sitemap-{dataset}-index.xml`) → `sitemapindex` 유효성
- 각 연/월 서브 sitemap → `urlset` 유효성, URL 수 ≤ 50,000
- `llms.txt` → 최소 H1 · 한 개 이상의 H2 섹션 존재
- `robots.txt` → `Sitemap:` 라인 존재
- 실패 시 non-zero exit → 워크플로우 fail → 본인 이메일 자동 알림

### 4.4 하지 않는 것

- 소스 리포 webhook 수신 — 운영 복잡도만 증가. 주 1회로 충분.
- 실시간 재빌드 — 에이전트 유즈케이스에서 요구하지 않음.
- 증분 빌드 — GitHub API 트리 조회 2회가 분 단위라 전량 재생성이 더 단순.

---

## 5. 엣지 케이스·테스트·리스크

### 5.1 파일명·경로

- 한글·공백·특수문자 → `urllib.parse.quote(path, safe='/')` 로 URL 인코딩.
- 비표준 날짜 폴더(발행 N회차 suffix 등) → 정규식 `^\d{4}-\d{2}-\d{2}$` 만 인덱싱. skip 건은 빌드 로그에 경고.
- 소스 리포에서 삭제된 문서 → 다음 재빌드에서 자동 drop. 중간 기간(<1주) stale 감수.

### 5.2 사이트맵 준수

- `sitemaps.org` 프로토콜: 50,000 URL / 50MB(압축 전) 한도.
- 연도별 분할이 부족하면 월별 재분할(`sitemap-press-2024-01.xml`).
- URL XML escape: `&` → `&amp;`, 기타.
- `<lastmod>` 는 파일 시스템 mtime 아닌 **발행 날짜(폴더명)** 사용 — 재빌드마다 mtime 같아지는 오류 방지.

### 5.3 `llms.txt` 규격

- Jeremy Howard / Anthropic 초안(H1 + blockquote + H2 섹션) 준수.
- 스펙 확정 전이라 포맷 변동 시 이 파일만 재생성.

### 5.4 `robots.txt` 정책

- 전 AI 크롤러 allow: GPTBot, ClaudeBot, CCBot, PerplexityBot, Google-Extended, anthropic-ai, Applebot-Extended, Meta-ExternalAgent, Bytespider 등.
- `crawl-delay: 1`.
- `Sitemap: https://hosungseo.github.io/ai-readable-government/sitemap.xml` 라인 필수.

### 5.5 유닛 테스트

없음. 빌더·검증 스크립트는 한 번 쓰고 주기 실행되는 도구. `validate_agent_artifacts.py` 가 end-to-end 테스트 역할. 과잉 설계 금지.

### 5.6 인지된 리스크

| 리스크 | 완화 |
|---|---|
| 소스 리포 rename / delete → 전체 링크 깨짐 | `README.md` · `llms.txt` 에 의존 리포 명시. 본인이 판단해 이동 시 본 스크립트 경로 교체 |
| 부분 clone 네트워크 실패 | 워크플로우 자동 재시도 1회 + 수동 재실행으로 복구. clone 실패는 빌드 실패로 처리(부분 결과 커밋 금지) |
| 소스 리포가 private로 전환될 경우 | `SOURCE_REPOS_TOKEN` repo secret 추가 후 clone URL에 토큰 주입 |
| Pages CDN 캐시 ~10분 stale | 수용. MVP 신선도 요구 없음 |
| isitagentready.com 표준 자체가 초기 단계 → 스펙 변동 | 분기 1회 표준 재확인, 아티팩트 포맷만 조정 |
| 행안부 조직국 공무원 개인 프로젝트 + 정부 데이터 미러링 이해충돌 | 본인이 사전 정리(기존 `ai-readable-government`·`ai-readable-gazette-kr` 운영 근거와 동일). 이 사이클은 공식성 주장하지 않는 개인 아카이브 포지셔닝 유지 |
| 에이전트 수요 실재성 미검증 | MVP 출시 후 3개월간 `isitagentready.com` 점수 + 외부 에이전트 fetch 로그(Pages 로그 불가라 정황 증거)로 관찰. 신호 없으면 입법예고 사이클 진행 여부 재검토 |

---

## 6. 결정 로그

| ID | 결정 | 근거 |
|---|---|---|
| D1 | `a2a_government_kr`(신규 폴더)는 폐기, 작업은 전부 `ai-readable-government/`에 레이어 추가 | 기존 인프라·도메인·브랜드 통일, 중복 회피 |
| D2 | 첫 사이클 = B-3 (정적 agent-ready + MD 서빙 강화) | 입법예고 수집은 신규 파이프라인 필요 → 분리, 수요 검증과 동시에 가능 |
| D3 | GitHub Pages 유지, Cloudflare Worker·Pages 이사 없음 | `Accept` 헤더 체크박스 하나 때문에 인프라 늘리는 비용 과함. URL 규칙으로 대체 |
| D4 | 데이터는 `raw.githubusercontent.com` 직접 포인팅, Pages 리포에 MD 복제 없음 | 중복 0 · `ai-readable-gazette-kr` 검증 패턴 재사용 |
| D5 | `.well-known/mcp.json` · `agent-skills.json` 생략, 실제 MCP 서버 생기는 다음 사이클에서 도입 | 지금 선언하면 tool call 시 깨짐 → 에이전트 신뢰 훼손 |
| D6 | 업데이트 주기 = 주 1회 cron + 수동 디스패치 | 에이전트 유즈케이스상 일 단위 정확도 불필요, 운영 단순 |
| D7 | ~~GitHub API `git/trees?recursive=true` 사용~~ → **tree-filter 부분 clone(`--filter=tree:0`) + `git ls-tree`** 로 변경 | 실측 결과 두 소스 리포 모두 API 응답이 `truncated: true` 로 잘림. blob 없는 부분 clone은 잘림 없고 수 초 내 완료 |
| D8 | Agent-ready artifact는 **리포 root level**에 배치 (docs/가 아님) | `robots.txt`는 프로토콜상 `/robots.txt`여야 함. 그리고 현 리포의 `index.html`이 root에 있어 Pages가 root 서빙 중임이 실측 확인됨 |
| D9 | `agent-catalog.json`에 `$schema` 필드 선언 안 함 | JSON Schema 파일을 공급하지 않는 상태에서 참조만 걸면 404 → 에이전트 신뢰 훼손. 스키마 공개 필요 시 별도 사이클에서 도입 |

---

## 7. 다음 단계

1. 본 spec을 git 커밋 (이 파일).
2. 본인 리뷰 — 수정 요청이 있으면 이 spec 편집.
3. 통과 시 `writing-plans` 스킬로 구현 플랜 작성 진행.
