# IA.md — Ai readable government

## 1. Product framing

Ai readable government is a reader, not a dashboard.

The job of the interface is to help a person:
1. discover a government document,
2. understand what type of document it is,
3. read a cleaned version,
4. compare it to the source,
5. move across dates and institutions.

---

## 2. Primary navigation

- Home
- Press
- Gazette
- By Date
- By Institution
- About

Optional later:
- Compare
- Topics
- Parsing status

---

## 3. Home

### Job
Explain the product clearly and route the user into the two main document layers.

### Sections
1. **Hero**
   - product name
   - one-sentence thesis
   - two main actions:
     - Browse Press
     - Browse Gazette

2. **What this site does**
   - 정부 문서를 읽기 쉬운 markdown 레이어로 제공
   - source / readable / raw 관계 설명

3. **Coverage snapshot**
   - press coverage dates
   - gazette coverage dates
   - last updated

4. **Latest documents**
   - latest readable items from both layers

5. **Browse by structure**
   - by date
   - by institution
   - by source type

---

## 4. Press index

### Job
Browse policy briefings and ministry press releases.

### Controls
- date range
- ministry filter
- keyword search
- view mode: latest / by date / by ministry

### List row fields
- title
- ministry
- date
- available layers badge (`readable`, `source`)
- short excerpt

---

## 5. Gazette index

### Job
Browse official gazette entries and move into readable/source/raw views.

### Controls
- date
- issuing institution
- form type
- basis law keyword
- has readable final? yes/no

### List row fields
- title
- issuing institution
- date
- form type
- basis law
- badges:
  - metadata
  - source pdf
  - raw
  - readable

### Reader orientation note
Every row should answer:
- what is it?
- who issued it?
- when?
- can I read a cleaned version?
- can I verify the source?

---

## 6. By Date page

### Job
Let users browse document flow chronologically.

### Layout
- left: date list or timeline rail
- right: documents for selected date

### Useful groupings
- press on that date
- gazette on that date
- counts by source type

This page should feel like an archive calendar, not analytics.

---

## 7. By Institution page

### Job
Help users follow one ministry/agency across both explanation and official-record layers.

### Layout
- institution header
- tabs:
  - press
  - gazette
  - all
- latest documents list
- source mix indicators

### Why this matters
This is likely the most important page for real government monitoring.

---

## 8. Document detail page

### Shared structure
1. title
2. source metadata strip
3. mode switch
4. content area
5. related navigation

### Metadata strip fields
- issuing institution / ministry
- date
- form type or category
- basis law if available
- original source link
- parsing quality label

### Mode switch
- Readable
- Raw Markdown
- Source PDF
- Metadata

### Content behavior
- default to `Readable` when available
- otherwise fall back to metadata + source link
- never hide the source PDF
- always show whether a cleaned layer is partial or good

---

## 9. Parsing quality language

Keep it honest.

Allowed labels:
- Good
- Needs cleanup
- Appendix-heavy
- Metadata only
- Source only

Do not pretend every PDF became perfect markdown.

---

## 10. Visual rules for implementation

- first viewport must explain the product without scrolling
- lists should look archival, not like kanban cards
- detail pages should prioritize reading comfort
- source trust markers must be visually obvious
- use restrained color and thin separators
- avoid decorative widgets that do not improve reading

---

## 11. Implementation priority

### Phase 1
- Home
- Gazette index
- Gazette detail
- Press link-outs or basic press index

### Phase 2
- By Date
- By Institution
- shared search/filter model

### Phase 3
- compare views
- parsing quality dashboards
- topic landing pages
