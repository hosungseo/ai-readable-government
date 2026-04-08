# DESIGN.md

## 1. Visual Theme & Atmosphere

Ai readable government is not a startup landing page and not a flashy dashboard.
It should feel like a **calm public reader** built for trust, traceability, and daily use.

Mood:
- editorial
- institutional but modern
- restrained
- high-legibility
- source-aware

Design philosophy:
- document first
- metadata second
- controls third
- decoration last
- trust over spectacle

Avoid:
- SaaS hero cards
- gradient-heavy hype UI
- colorful KPI mosaics
- generic analytics dashboard patterns
- overly soft shadows and floating glass surfaces

Use:
- strong typography hierarchy
- calm whitespace
- thin dividers
- muted surfaces
- clear provenance badges
- obvious source/readable/raw distinctions

---

## 2. Color Palette & Roles

Base palette:
- `paper` — `#F7F5F1`
  - main page background
- `canvas` — `#FFFFFF`
  - content surface
- `ink` — `#111318`
  - primary text
- `muted-ink` — `#5A6270`
  - secondary text
- `line` — `#E3E0D8`
  - dividers and table rules
- `slate` — `#D7DDE5`
  - quiet UI surfaces

Accent palette:
- `civic-blue` — `#193A6B`
  - primary accent, links, active states
- `archive-green` — `#2E5E4E`
  - readable/final state, success-like archival confidence
- `source-amber` — `#8A5A18`
  - source/raw/original emphasis
- `alert-red` — `#8B2E2E`
  - errors, unavailable assets, parsing issues

Usage rules:
- default to monochrome + one accent
- blue is the main interaction color
- green is for readable/final layers only
- amber is for raw/source/PDF cues only
- never use more than two accents in the same viewport

---

## 3. Typography Rules

Typefaces:
- Headings: `Pretendard`, `Inter`, `system-ui`, sans-serif
- Body: `Pretendard`, `Noto Sans KR`, `system-ui`, sans-serif
- Monospace/meta IDs: `JetBrains Mono`, `SFMono-Regular`, monospace

Hierarchy:
- Product name / page title: 40–56px, 700–800
- Section title: 24–32px, 700
- Card/list title: 17–20px, 650–700
- Body: 15–18px, 400–500
- Metadata / labels: 12–13px, 600, slightly tighter tracking
- Dense document text: 15–16px with generous line-height

Rules:
- make the document title the loudest element on detail pages
- metadata must scan faster than body text
- IDs and dates can use mono selectively
- keep line length moderate on readable documents
- prefer bold through hierarchy, not through many font sizes

---

## 4. Component Stylings

### Navigation
- simple horizontal or left-rail navigation
- low chrome
- active route indicated by color + underline or weight, not pills everywhere

### Buttons
- primary: civic-blue fill, white text, sharp but not harsh radius
- secondary: white/canvas surface with border
- ghost: text-only with subtle hover tint

### Badges
Only for meaningful document state:
- `source pdf`
- `raw md`
- `readable`
- `api metadata`
- `parsing issue`

Badges should be:
- small
- uppercase or tight label style
- low count per screen

### Cards
- do not use cards by default
- only use card treatment when the block is truly interactive or grouped
- if a list can work as rows with dividers, use rows

### Tables
- minimal rules
- strong column labels
- zebra striping only if needed
- document lists should feel like archive records, not enterprise admin sludge

### Document viewer blocks
- headline block
- source metadata strip
- tab or segmented switch for `Readable / Raw / Source PDF / Metadata`
- readable text area on calm white surface with ample spacing

---

## 5. Layout Principles

Page model:
- top-level site frame
- route intro block
- control strip
- content list or content reader

Home page layout:
1. strong project header
2. two-layer explanation: press / gazette
3. current coverage
4. latest documents by date
5. entry points by source type

Reader page layout:
1. page title + scope note
2. filtering controls
3. content list
4. detail pane or dedicated detail page

Detail page layout:
1. title
2. metadata + provenance
3. mode switch
4. readable content
5. appendix/source/raw access

Spacing:
- airy outer spacing
- compact metadata spacing
- generous document body spacing
- keep controls close to results, not floating alone

---

## 6. Depth & Elevation

- mostly flat surfaces
- one subtle shadow tier for overlays only
- use borders and spacing before shadows
- sticky headers may use slight backdrop and bottom border
- avoid floating card stacks

---

## 7. Do's and Don'ts

Do:
- make provenance obvious
- keep the first screen instantly understandable
- show what is readable vs raw vs source
- make date and institution browsing effortless
- prefer lists, rows, and typographic structure over UI chrome

Don't:
- build a fake KPI dashboard for an archive product
- use 6 different badge colors
- make every block a card
- bury source PDF links
- let decorative motion compete with reading

---

## 8. Responsive Behavior

Mobile:
- filters collapse cleanly
- document title remains large but wraps well
- source/readable mode switch stays thumb-friendly
- wide metadata tables should stack into definition-list style blocks

Desktop:
- support split view where practical
- allow reading column to stay comfortably narrow even on wide screens
- use sticky metadata rail only if it improves orientation

---

## 9. Motion

Use only 2–3 meaningful motions:
- gentle section fade/slide on first reveal
- subtle state transition when switching `Readable / Raw / PDF`
- small hover emphasis on archive rows

No decorative parallax, bouncing cards, or flashy counters.

---

## 10. Product-Specific Rules

### Information architecture labels
Primary top-level concepts:
- Home
- Press
- Gazette
- By Date
- By Institution
- About

### Content labels
Use plain labels:
- Readable
- Raw Markdown
- Source PDF
- Metadata
- Parsing quality

### Quality status language
Prefer honest labels:
- Good
- Needs cleanup
- Appendix-heavy
- OCR may be needed

### Reader principle
If a block does not help a person:
- find a document
- trust a document
- understand a document
- compare a document to source
remove it.
