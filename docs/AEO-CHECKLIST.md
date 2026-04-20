# AEO Checklist for ai-readable-government

`ai-readable-government`를 사람용 reader이면서 agent-friendly public document surface로 키우기 위한 실행 체크리스트다.

기준 문맥:
- Agentic Engine Optimization (AEO)
- 현재 저장소 구조: `robots.txt`, `sitemap.xml`, `llms.txt`, `agent-catalog.json`, sample indexes, static reader

---

## 1. Access / Crawl

### Already
- [x] `/robots.txt` 제공
- [x] `/sitemap.xml` 제공
- [x] GitHub Pages 공개 접근 가능

### Next
- [ ] `robots.txt`가 주요 agent/crawler 접근을 과하게 막고 있지 않은지 문구 재점검
- [ ] `robots.txt`에 reader / catalog / sitemap 경로가 의도대로 노출되는지 확인
- [ ] `agent-catalog.json`, `llms.txt`, `sitemap.xml`이 모두 200 응답인지 정기 검증 루틴 추가

---

## 2. Discovery

### Already
- [x] `/llms.txt` 제공
- [x] `/agent-catalog.json` 제공
- [x] press / gazette sitemap index 제공

### Next
- [ ] `llms.txt`를 task-oriented section 기준으로 더 재구성
- [ ] `llms.txt`에 sample reader와 full corpus의 차이를 명시
- [ ] `llms.txt`에서 핵심 entrypoint를 우선순위 순으로 정렬
  - reader
  - catalog
  - sitemap
  - source repos

---

## 3. Parsability

### Already
- [x] 정적 HTML 기반이라 JS 의존 없이 기본 콘텐츠 접근 가능
- [x] 구조화된 JSON 인덱스(`docs/index-data.json`) 제공
- [x] source repo는 Markdown corpus 기반

### Next
- [ ] 홈/소개 문구에서 sample count와 full corpus count를 항상 분리 표기
- [ ] 주요 페이지에 machine-readable metadata를 더 노출
- [ ] 사람이 보는 카피와 agent가 읽는 설명이 충돌하지 않게 용어 통일
  - sample
  - full corpus
  - reader
  - source repo

---

## 4. Token efficiency

### Already
- [x] `llms.txt`와 catalog가 원문 전체 대신 entrypoint 역할을 함
- [x] sample index로 사람이 한 번에 읽는 범위를 줄여둠

### Next
- [ ] `llms.txt`에 주요 문서/리소스별 대략적 token size 또는 size hint 추가
- [ ] 너무 큰 JSON/문서에는 chunking 전략 문서화
- [ ] `docs/index-data.json`와 agent-facing artifacts의 크기 증가 추세 점검

### Practical target
- `llms.txt`: 가능한 한 짧고 선명하게
- landing copy: sample/full distinction first
- large corpus access: catalog → sitemap → raw markdown 순 유도

---

## 5. Capability signaling

### Already
- [x] `agent-catalog.json`으로 dataset capability를 기계적으로 설명
- [x] source repo, date range, raw path pattern, variant 정보 제공

### Next
- [ ] 홈/README에서 "이 저장소가 할 수 있는 것"과 "하지 않는 것"을 더 명확히 분리
- [ ] agent-catalog에 reader layer purpose를 한 줄 더 강화
- [ ] sample reader와 full corpus discovery 역할의 경계를 더 명시

### Should be explicit
- 사람용 reader다
- 동시에 agent discovery layer다
- 전체 문서를 직접 호스팅하는 repo가 아니라 source repos를 가리킨다
- sample browse와 full corpus는 동일한 숫자 체계를 쓰지 않는다

---

## 6. Observability

### Already
- [x] GitHub Pages/Actions 기반 배포 이력 확인 가능

### Next
- [ ] AI referral / crawler 트래픽을 따로 볼지 결정
- [ ] 최소한 서버 로그 또는 대체 지표에서 AI fetch 흔적 분리 가능성 검토
- [ ] Pages 정적 환경에서 불가능한 관측은 repo-level monitoring note로 문서화

---

## 7. Copy for AI / Agent UX

### Already
- [x] source markdown repos를 직접 가리키는 구조가 있음

### Next
- [ ] 핵심 페이지에 "agent entrypoints" 짧은 안내 추가 검토
- [ ] 사람이 복사해 agent에 넣기 쉬운 요약 블록 또는 Markdown export 경로 검토
- [ ] README에 AEO 관점의 짧은 운영 원칙 추가 검토

---

## 8. Repo-level agent file

### Already
- [x] OpenClaw 워크스페이스에는 `AGENTS.md` 운영 규칙이 존재

### Next
- [ ] 이 repo 자체에도 public-facing `AGENTS.md`를 둘지 검토
- [ ] 둔다면 아래를 포함
  - repo purpose
  - key files
  - build commands
  - source-of-truth artifacts
  - sample/full count policy
  - Pages deployment notes

---

## 9. Immediate priority for this repo

### P1
- [ ] `llms.txt`를 sample/full distinction 중심으로 한 번 더 다듬기
- [ ] README에 이 체크리스트 링크 추가
- [ ] `agent-catalog.json` 설명 문구가 reader layer 목적과 맞는지 점검

### P2
- [ ] public `AGENTS.md` 도입 여부 결정
- [ ] token/size hints를 어느 표면에 둘지 결정
- [ ] AI-friendly copy block 또는 agent entrypoint block 검토

### P3
- [ ] AEO 상태를 정기 점검하는 간단한 validate 스크립트 추가 검토

---

## One-line principle

**인간용 IA와 agent용 IA를 분리하되, 숫자·용어·entrypoint는 서로 모순되지 않게 유지한다.**
