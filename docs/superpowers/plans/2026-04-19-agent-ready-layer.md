# Agent-Ready Discovery Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add agent-discoverable static artifacts (robots.txt, llms.txt, sitemap index, agent-catalog.json) on top of the existing `ai-readable-government` reader so external agents can find and consume Korean government markdown corpora (관보 12.8만 + 보도자료 17만).

**Architecture:** Static files served from repo root via GitHub Pages (main branch, `/` folder). A weekly-scheduled Python script performs tree-filter partial clones of two source repos (`hosungseo/gov-gazette-md`, `hosungseo/gov-press-md`), enumerates all `*.md` paths via `git ls-tree`, groups by year, and emits a 3-tier XML sitemap, a JSON catalog, and a prose `llms.txt`. No backend, no database, no runtime services.

**Tech Stack:** Python 3.11 (standard lib + `lxml`, `jsonschema`), `git` (tree-filter partial clone), GitHub Actions (cron + workflow_dispatch).

**Spec:** `docs/superpowers/specs/2026-04-19-agent-ready-layer-design.md`

**Working directory throughout:** `/Users/seohoseong/.openclaw/workspace/ai-readable-government`

---

## Phase 0: Prerequisites (manual — user performs)

### Task 0: Public transition + Pages enable

**Files:** none (GitHub UI only)

- [ ] **Step 1: Make `hosungseo/ai-readable-government` public**

Browser → https://github.com/hosungseo/ai-readable-government → Settings → General → scroll to Danger Zone → Change visibility → Make public → confirm.

- [ ] **Step 2: Enable GitHub Pages for this repo**

Browser → same repo → Settings → Pages → "Build and deployment" → Source: *Deploy from a branch* → Branch: `main`, Folder: `/ (root)` → Save.

- [ ] **Step 3: Make `hosungseo/gov-gazette-md` public**

Browser → https://github.com/hosungseo/gov-gazette-md → Settings → General → Danger Zone → Change visibility → Make public → confirm.

- [ ] **Step 4: Make `hosungseo/gov-press-md` public**

Browser → https://github.com/hosungseo/gov-press-md → Settings → General → Danger Zone → Change visibility → Make public → confirm.

- [ ] **Step 5: Verify (wait ~1-2 min after enable)**

```bash
curl -sI https://hosungseo.github.io/ai-readable-government/ | head -1
# Expected: HTTP/2 200

curl -sI https://raw.githubusercontent.com/hosungseo/gov-gazette-md/main/README.md | head -1
# Expected: HTTP/2 200

curl -sI https://raw.githubusercontent.com/hosungseo/gov-press-md/main/README.md | head -1
# Expected: HTTP/2 200
```

If any returns 404 or 301 to a login page, re-check visibility / Pages settings before proceeding.

---

## Phase 1: Static robots.txt

### Task 1: Write robots.txt

**Files:**
- Create: `robots.txt` (repo root)

- [ ] **Step 1: Write the file**

Create `robots.txt` with exactly this content:

```txt
# robots.txt for ai-readable-government
# https://hosungseo.github.io/ai-readable-government/

User-agent: *
Allow: /
Crawl-delay: 1

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: CCBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Meta-ExternalAgent
Allow: /

User-agent: Bytespider
Allow: /

Sitemap: https://hosungseo.github.io/ai-readable-government/sitemap.xml
```

- [ ] **Step 2: Commit**

```bash
git add robots.txt
git commit -m "Add robots.txt allowing AI crawlers"
```

---

## Phase 2: Helpers package scaffold + source_repos module

### Task 2: Create helpers package init

**Files:**
- Create: `scripts/agent_artifacts/__init__.py`

- [ ] **Step 1: Write the package init**

```python
"""Helpers for building and validating agent-ready artifacts."""
```

- [ ] **Step 2: Commit**

```bash
git add scripts/agent_artifacts/__init__.py
git commit -m "Add agent_artifacts helpers package"
```

### Task 3: source_repos helper

**Files:**
- Create: `scripts/agent_artifacts/source_repos.py`

- [ ] **Step 1: Write the module**

```python
"""Tree-filter partial clone of source MD repos + path extraction.

Why partial clone instead of GitHub trees API: trees?recursive=true truncates
on large repos (verified empirically — both source repos return truncated=true
with ~40k of 128k+ / 170k+ entries). Partial clone with --filter=tree:0
downloads only tree objects, no blobs, and returns the complete path list.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class SourceRepo:
    owner: str
    name: str
    clone_dir: Path

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.name}.git"

    def ensure_cloned(self) -> None:
        if self.clone_dir.exists():
            shutil.rmtree(self.clone_dir)
        self.clone_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "git", "clone",
                "--no-checkout",
                "--filter=tree:0",
                "--depth", "1",
                self.clone_url,
                str(self.clone_dir),
            ],
            check=True,
            capture_output=True,
        )

    def list_md_paths(self) -> list[str]:
        result = subprocess.run(
            ["git", "-C", str(self.clone_dir),
             "ls-tree", "-r", "--name-only", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return [p for p in result.stdout.splitlines() if p.endswith(".md")]

    def cleanup(self) -> None:
        if self.clone_dir.exists():
            shutil.rmtree(self.clone_dir)


def group_by_date(paths: list[str]) -> dict[str, list[str]]:
    """Group MD paths by the first YYYY-MM-DD segment in the path.

    Paths without such a segment are skipped silently.
    Returns {"YYYY-MM-DD": [path, ...]} sorted by insertion order.
    """
    buckets: dict[str, list[str]] = defaultdict(list)
    for p in paths:
        date = next((s for s in p.split("/") if DATE_DIR_RE.match(s)), None)
        if date is None:
            continue
        buckets[date].append(p)
    return buckets


def group_by_year(
    date_buckets: dict[str, list[str]],
) -> dict[str, dict[str, list[str]]]:
    """Nest date buckets under year: {"YYYY": {"YYYY-MM-DD": [...]}}."""
    out: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for date, paths in date_buckets.items():
        year = date[:4]
        out[year][date] = paths
    return out
```

- [ ] **Step 2: Smoke test (small repo first)**

```bash
python3 -c "
from pathlib import Path
from scripts.agent_artifacts.source_repos import SourceRepo, group_by_date, group_by_year

r = SourceRepo('hosungseo', 'gov-press-md', Path('/tmp/_smoke_press'))
r.ensure_cloned()
paths = r.list_md_paths()
print(f'press_total_md={len(paths)}')
dates = group_by_date(paths)
print(f'press_dates={len(dates)}')
years = group_by_year(dates)
print(f'press_years={sorted(years.keys())}')
print(f'press_sample_path={paths[0] if paths else None}')
r.cleanup()
"
```

Expected (numbers approximate, should match reality):
- `press_total_md` around 169,000 — if <50k, clone filter likely failed
- `press_dates` in the thousands
- `press_years` includes ['2020', '2021', '2022', '2023', '2024', '2025', '2026']
- `press_sample_path` starts with `data/`

- [ ] **Step 3: Commit**

```bash
git add scripts/agent_artifacts/source_repos.py
git commit -m "Add source_repos helper (partial clone + path grouping)"
```

---

## Phase 3: Dataset config + sitemap module

### Task 4: Dataset config module

**Files:**
- Create: `scripts/agent_artifacts/config.py`

- [ ] **Step 1: Write the module**

```python
"""Dataset configuration — the single source of truth for source repos,
URL bases, path patterns, and licensing prose consumed by builder modules."""

from __future__ import annotations

from dataclasses import dataclass, field


SITE_URL = "https://hosungseo.github.io/ai-readable-government/"


@dataclass(frozen=True)
class Variant:
    id: str
    description: str
    raw_base: str
    path_pattern: str
    source_subpath: str  # leading path inside the source repo (e.g. "data/")


@dataclass(frozen=True)
class Dataset:
    id: str
    name: str
    description: str
    update_cadence: str
    license: str
    source_repo: str  # "owner/name"
    variants: tuple[Variant, ...]
    frontmatter_fields: tuple[str, ...]
    primary_variant_id: str  # which variant feeds the sitemap


GAZETTE = Dataset(
    id="gazette",
    name="대한민국 관보 (Government Gazette of Korea)",
    description="Official government record layer — dictionary-corrected markdown corpus.",
    update_cadence="near-daily (source repo)",
    license="Korean Copyright Act Art. 7 — not protected; derived corpus CC0 1.0",
    source_repo="hosungseo/gov-gazette-md",
    variants=(
        Variant(
            id="readable-corrected",
            description="OCR-corrected, dictionary-based fixup (recommended for LLM).",
            raw_base="https://raw.githubusercontent.com/hosungseo/gov-gazette-md/main/derived/readable-corrected/",
            path_pattern="{YYYY-MM-DD}/{NNN}_{institution}_{title}.md",
            source_subpath="derived/readable-corrected/",
        ),
        Variant(
            id="readable-final",
            description="Pre-correction baseline (for diff / research).",
            raw_base="https://raw.githubusercontent.com/hosungseo/gov-gazette-md/main/readable-final/",
            path_pattern="{YYYY-MM-DD}/{NNN}_{institution}_{title}.md",
            source_subpath="readable-final/",
        ),
    ),
    frontmatter_fields=("title", "publisher", "date", "source_raw_md"),
    primary_variant_id="readable-corrected",
)


PRESS = Dataset(
    id="press",
    name="정부 보도자료 (Government Press Releases)",
    description="Government explanatory layer — ministry press releases as markdown.",
    update_cadence="daily (source repo)",
    license="See individual ministry terms (public information, generally open).",
    source_repo="hosungseo/gov-press-md",
    variants=(
        Variant(
            id="data",
            description="Press releases under per-year folders.",
            raw_base="https://raw.githubusercontent.com/hosungseo/gov-press-md/main/data/",
            path_pattern="{YYYY}/{YYYY-MM-DD}/{...}.md",
            source_subpath="data/",
        ),
    ),
    frontmatter_fields=("title", "agency", "date", "source_url"),
    primary_variant_id="data",
)


DATASETS: tuple[Dataset, ...] = (GAZETTE, PRESS)


def dataset_by_id(did: str) -> Dataset:
    for d in DATASETS:
        if d.id == did:
            return d
    raise KeyError(f"unknown dataset: {did}")


def variant_by_id(ds: Dataset, vid: str) -> Variant:
    for v in ds.variants:
        if v.id == vid:
            return v
    raise KeyError(f"unknown variant {vid} in dataset {ds.id}")
```

- [ ] **Step 2: Smoke test**

```bash
python3 -c "
from scripts.agent_artifacts.config import DATASETS, dataset_by_id, variant_by_id
for d in DATASETS:
    print(d.id, d.source_repo, [v.id for v in d.variants])
g = dataset_by_id('gazette')
v = variant_by_id(g, 'readable-corrected')
print(v.raw_base)
"
```

Expected output contains both dataset ids, variant lists, and the raw_base URL.

- [ ] **Step 3: Commit**

```bash
git add scripts/agent_artifacts/config.py
git commit -m "Add dataset config for agent-ready builder"
```

### Task 5: Sitemap generator module

**Files:**
- Create: `scripts/agent_artifacts/sitemaps.py`

- [ ] **Step 1: Write the module**

```python
"""Generate the 3-tier sitemap: site-wide index, per-dataset index, year/month URL lists."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

from .config import SITE_URL, DATASETS, Dataset, Variant

SITEMAP_DIR = "sitemaps"
URL_LIMIT_PER_SITEMAP = 45_000  # 50k hard limit; leave 10% headroom
DATE_SEG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATE_IN_PATH_RE = re.compile(r"/(\d{4})-(\d{2})-\d{2}/")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _doc_url(variant: Variant, path_inside_repo: str) -> str:
    # variant.raw_base already ends with /; strip source_subpath prefix from path
    assert path_inside_repo.startswith(variant.source_subpath), (
        f"path {path_inside_repo!r} missing prefix {variant.source_subpath!r}"
    )
    rel = path_inside_repo[len(variant.source_subpath):]
    parts = [quote(seg, safe="") for seg in rel.split("/")]
    return variant.raw_base + "/".join(parts)


def _doc_lastmod(path_inside_repo: str) -> str:
    """Extract YYYY-MM-DD from the first matching path segment."""
    for seg in path_inside_repo.split("/"):
        if DATE_SEG_RE.match(seg):
            return seg
    return date.today().isoformat()


def _split_year_bucket(
    year_paths: list[str], limit: int = URL_LIMIT_PER_SITEMAP
) -> list[tuple[str, list[str]]]:
    """Return [(suffix, paths), ...] where suffix is '' for whole-year or
    '-MM' for monthly split when year exceeds `limit`."""
    if len(year_paths) <= limit:
        return [("", year_paths)]
    by_month: dict[str, list[str]] = defaultdict(list)
    for p in year_paths:
        m = DATE_IN_PATH_RE.search(p)
        if not m:
            continue
        by_month[m.group(2)].append(p)
    return [(f"-{mm}", paths) for mm, paths in sorted(by_month.items())]


def _urlset_xml(urls_and_lastmods: list[tuple[str, str]]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, lastmod in urls_and_lastmods:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(url)}</loc>")
        lines.append(f"    <lastmod>{escape(lastmod)}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def _sitemapindex_xml(entries: list[tuple[str, str]]) -> str:
    """`entries` = [(loc, lastmod), ...]."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod in entries:
        lines.append("  <sitemap>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        lines.append(f"    <lastmod>{escape(lastmod)}</lastmod>")
        lines.append("  </sitemap>")
    lines.append("</sitemapindex>")
    return "\n".join(lines) + "\n"


def build_dataset_sitemaps(
    dataset: Dataset,
    year_buckets: dict[str, dict[str, list[str]]],
    out_root: Path,
) -> str:
    """Write per-year (and per-month if needed) urlset files plus the dataset
    index. Returns the absolute URL of the dataset index file.
    Only the primary_variant is indexed — variants share the same paths inside
    the source repo, just different raw_base URLs, so one sitemap set per dataset."""
    variant = next(v for v in dataset.variants if v.id == dataset.primary_variant_id)
    sitemap_dir = out_root / SITEMAP_DIR
    sitemap_dir.mkdir(parents=True, exist_ok=True)

    index_entries: list[tuple[str, str]] = []
    for year in sorted(year_buckets.keys()):
        all_year_paths = [p for day_paths in year_buckets[year].values() for p in day_paths]
        for suffix, paths in _split_year_bucket(all_year_paths):
            file_name = f"sitemap-{dataset.id}-{year}{suffix}.xml"
            urls_and_lastmods: list[tuple[str, str]] = []
            for p in sorted(paths):
                urls_and_lastmods.append((_doc_url(variant, p), _doc_lastmod(p)))
            (sitemap_dir / file_name).write_text(_urlset_xml(urls_and_lastmods), encoding="utf-8")
            latest_lastmod = max((lm for _, lm in urls_and_lastmods), default=date.today().isoformat())
            index_entries.append(
                (f"{SITE_URL}{SITEMAP_DIR}/{file_name}", latest_lastmod)
            )

    index_name = f"sitemap-{dataset.id}-index.xml"
    (sitemap_dir / index_name).write_text(_sitemapindex_xml(index_entries), encoding="utf-8")
    return f"{SITE_URL}{SITEMAP_DIR}/{index_name}"


def build_site_sitemap(dataset_index_urls: list[str], out_root: Path) -> None:
    """Write the top-level sitemap.xml pointing to each dataset index."""
    entries = [(u, _now_iso()) for u in dataset_index_urls]
    (out_root / "sitemap.xml").write_text(_sitemapindex_xml(entries), encoding="utf-8")
```

- [ ] **Step 2: Smoke test (with fake inputs — avoids real clone)**

```bash
python3 -c "
from pathlib import Path
from scripts.agent_artifacts.sitemaps import build_dataset_sitemaps, build_site_sitemap
from scripts.agent_artifacts.config import GAZETTE

import shutil, os
out = Path('/tmp/_smoke_sitemaps')
if out.exists(): shutil.rmtree(out)
out.mkdir()

# fake 3 paths across 2 years
fake = {
    '2020': {'2020-01-02': ['derived/readable-corrected/2020-01-02/001_foo_bar.md',
                             'derived/readable-corrected/2020-01-02/002_foo_baz.md']},
    '2026': {'2026-04-07': ['derived/readable-corrected/2026-04-07/100_구_청_가나다.md']},
}
url = build_dataset_sitemaps(GAZETTE, fake, out)
print('dataset_index_url=', url)
build_site_sitemap([url], out)

for p in sorted((out / 'sitemaps').iterdir()):
    print(p.name, len(p.read_text().splitlines()), 'lines')
print('---sitemap.xml---')
print((out / 'sitemap.xml').read_text())
"
```

Expected:
- Prints `dataset_index_url=https://hosungseo.github.io/ai-readable-government/sitemaps/sitemap-gazette-index.xml`
- Three files in `sitemaps/`: `sitemap-gazette-2020.xml`, `sitemap-gazette-2026.xml`, `sitemap-gazette-index.xml`
- Site-level `sitemap.xml` with one `<sitemap>` entry pointing at the gazette index
- Korean filename in 2026 file is URL-encoded (percent-escaped)

- [ ] **Step 3: Commit**

```bash
git add scripts/agent_artifacts/sitemaps.py
git commit -m "Add sitemap generator (3-tier with URL-safe encoding)"
```

---

## Phase 4: Catalog + llms.txt modules

### Task 6: Catalog generator

**Files:**
- Create: `scripts/agent_artifacts/catalog.py`

- [ ] **Step 1: Write the module**

```python
"""Generate agent-catalog.json from dataset buckets."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from .config import DATASETS, SITE_URL, Dataset


def _iso_now() -> str:
    """UTC ISO-8601 with explicit Z. Workflow runs on UTC runners; clean string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sample_urls(dataset: Dataset, sorted_paths: list[str]) -> list[str]:
    """Pick 3 samples spread across the date range (first, mid, last)."""
    variant = next(v for v in dataset.variants if v.id == dataset.primary_variant_id)
    if not sorted_paths:
        return []
    picks_idx = [0, len(sorted_paths) // 2, len(sorted_paths) - 1]
    picks_idx = list(dict.fromkeys(picks_idx))  # dedupe while preserving order
    out = []
    for i in picks_idx:
        p = sorted_paths[i]
        assert p.startswith(variant.source_subpath)
        rel = p[len(variant.source_subpath):]
        segs = [quote(s, safe="") for s in rel.split("/")]
        out.append(variant.raw_base + "/".join(segs))
    return out


def _dataset_node(
    dataset: Dataset,
    total_documents: int,
    date_start: str,
    date_end: str,
    sorted_paths: list[str],
    sitemap_url: str,
) -> dict:
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "format": "text/markdown",
        "total_documents": total_documents,
        "date_range": {"start": date_start, "end": date_end},
        "update_cadence": dataset.update_cadence,
        "license": dataset.license,
        "source_repo": dataset.source_repo,
        "variants": [
            {
                "id": v.id,
                "description": v.description,
                "raw_base": v.raw_base,
                "path_pattern": v.path_pattern,
            }
            for v in dataset.variants
        ],
        "frontmatter_fields": list(dataset.frontmatter_fields),
        "sitemap_url": sitemap_url,
        "sample_documents": _sample_urls(dataset, sorted_paths),
    }


def build_catalog(
    per_dataset: dict[str, dict],
    out_root: Path,
) -> None:
    """`per_dataset` maps dataset_id -> {
        'total_documents': int,
        'date_start': str, 'date_end': str,
        'sorted_paths': list[str],
        'sitemap_url': str,
    }"""
    nodes = []
    for ds in DATASETS:
        info = per_dataset[ds.id]
        nodes.append(
            _dataset_node(
                ds,
                total_documents=info["total_documents"],
                date_start=info["date_start"],
                date_end=info["date_end"],
                sorted_paths=info["sorted_paths"],
                sitemap_url=info["sitemap_url"],
            )
        )
    catalog = {
        "name": "ai-readable-government",
        "description": (
            "Korean government public documents — agent-readable index. "
            "Points to source markdown corpora hosted on GitHub."
        ),
        "site_url": SITE_URL,
        "generated_at": _iso_now(),
        "generator": "scripts/build_agent_artifacts.py",
        "license_note": (
            "Index/catalog under MIT. Document license varies per dataset — "
            "see `license` per dataset."
        ),
        "contact": "https://github.com/hosungseo/ai-readable-government/issues",
        "datasets": nodes,
        "how_to_use": [
            "1. GET /agent-catalog.json for machine-readable index.",
            "2. For structure, fetch each dataset's sitemap_url (XML sitemap index).",
            "3. For documents, fetch raw_base + date/path — plain markdown with YAML frontmatter.",
            "4. For a human-browsable reader, see site_url.",
        ],
    }
    (out_root / "agent-catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
```

- [ ] **Step 2: Smoke test**

```bash
python3 -c "
from pathlib import Path
import shutil, json
from scripts.agent_artifacts.catalog import build_catalog
out = Path('/tmp/_smoke_catalog'); shutil.rmtree(out, ignore_errors=True); out.mkdir()
per = {
    'gazette': {
        'total_documents': 3,
        'date_start': '2020-01-02', 'date_end': '2026-04-07',
        'sorted_paths': [
            'derived/readable-corrected/2020-01-02/001_foo_bar.md',
            'derived/readable-corrected/2024-06-15/200_baz_qux.md',
            'derived/readable-corrected/2026-04-07/300_기관_제목.md',
        ],
        'sitemap_url': 'https://hosungseo.github.io/ai-readable-government/sitemaps/sitemap-gazette-index.xml',
    },
    'press': {
        'total_documents': 0,
        'date_start': '2020-01-01', 'date_end': '2020-01-01',
        'sorted_paths': [],
        'sitemap_url': 'https://hosungseo.github.io/ai-readable-government/sitemaps/sitemap-press-index.xml',
    },
}
build_catalog(per, out)
print(json.dumps(json.loads((out/'agent-catalog.json').read_text()), ensure_ascii=False, indent=2)[:1200])
"
```

Expected: Valid JSON output printed, 3 sample document URLs for gazette (first/middle/last), Korean title in the 3rd URL is percent-encoded, press sample_documents is an empty list.

- [ ] **Step 3: Commit**

```bash
git add scripts/agent_artifacts/catalog.py
git commit -m "Add catalog generator"
```

### Task 7: llms.txt generator

**Files:**
- Create: `scripts/agent_artifacts/llmstxt.py`

- [ ] **Step 1: Write the module**

```python
"""Generate llms.txt — the prose cousin of agent-catalog.json.

Follows the H1 + blockquote + H2 sections convention from llmstxt.org draft.
"""

from __future__ import annotations

from pathlib import Path

from .config import DATASETS, SITE_URL, Dataset


def _dataset_section(dataset: Dataset, total: int, start: str, end: str, sitemap_url: str) -> str:
    lines = [
        f"## {dataset.name}",
        "",
        dataset.description,
        "",
        f"- Documents: {total:,}",
        f"- Date range: {start} ~ {end}",
        f"- Update cadence: {dataset.update_cadence}",
        f"- License: {dataset.license}",
        f"- Source repo: https://github.com/{dataset.source_repo}",
        f"- Sitemap: {sitemap_url}",
        "- Variants:",
    ]
    for v in dataset.variants:
        lines.append(f"  - **{v.id}** — {v.description}")
        lines.append(f"    - Raw base: `{v.raw_base}`")
        lines.append(f"    - Path pattern: `{v.path_pattern}`")
    lines.append("")
    return "\n".join(lines)


def build_llmstxt(per_dataset: dict[str, dict], out_root: Path) -> None:
    lines = [
        "# ai-readable-government",
        "",
        "> Korean government public documents — agent-readable index. "
        "Points to source markdown corpora hosted on GitHub. "
        "The human-browsable reader lives at the site root; this `llms.txt` "
        "summarizes the machine-readable layer.",
        "",
        "## Entry points",
        "",
        "- Machine-readable catalog: `" + SITE_URL + "agent-catalog.json`",
        "- Sitemap index: `" + SITE_URL + "sitemap.xml`",
        "- Human reader: `" + SITE_URL + "`",
        "",
        "## Fetching documents",
        "",
        "Each dataset below lists a `raw_base` and a `path_pattern`. "
        "To fetch a document, concatenate `raw_base` with the URL-encoded path.",
        "All documents are plain markdown with YAML frontmatter.",
        "",
    ]
    for ds in DATASETS:
        info = per_dataset[ds.id]
        lines.append(
            _dataset_section(
                ds,
                total=info["total_documents"],
                start=info["date_start"],
                end=info["date_end"],
                sitemap_url=info["sitemap_url"],
            )
        )
    lines.extend(
        [
            "## License",
            "",
            "Index and catalog artifacts: MIT. Individual document licensing is noted "
            "per dataset above. The gazette originates from a legally unprotected public "
            "record (Korean Copyright Act Art. 7); the press releases are public information.",
            "",
        ]
    )
    (out_root / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
```

- [ ] **Step 2: Smoke test**

```bash
python3 -c "
from pathlib import Path
import shutil
from scripts.agent_artifacts.llmstxt import build_llmstxt
out = Path('/tmp/_smoke_llms'); shutil.rmtree(out, ignore_errors=True); out.mkdir()
per = {
    'gazette': {'total_documents': 128471, 'date_start': '2020-01-02', 'date_end': '2026-04-07',
                'sitemap_url': 'https://hosungseo.github.io/ai-readable-government/sitemaps/sitemap-gazette-index.xml'},
    'press':   {'total_documents': 169801, 'date_start': '2020-01-01', 'date_end': '2026-04-18',
                'sitemap_url': 'https://hosungseo.github.io/ai-readable-government/sitemaps/sitemap-press-index.xml'},
}
build_llmstxt(per, out)
print((out / 'llms.txt').read_text())
"
```

Expected: llms.txt printed with H1 `# ai-readable-government`, one blockquote, at least 3 H2 sections (`## Entry points`, `## Fetching documents`, `## 대한민국 관보 ...`, `## 정부 보도자료 ...`, `## License`), includes the two totals (128,471 and 169,801).

- [ ] **Step 3: Commit**

```bash
git add scripts/agent_artifacts/llmstxt.py
git commit -m "Add llms.txt generator"
```

---

## Phase 5: Orchestrator

### Task 8: build_agent_artifacts.py entry point

**Files:**
- Create: `scripts/build_agent_artifacts.py`

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Orchestrator — clone source repos, group paths, emit all agent artifacts.

Run as a single command; writes all files into the repo root.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.agent_artifacts.catalog import build_catalog
from scripts.agent_artifacts.config import DATASETS
from scripts.agent_artifacts.llmstxt import build_llmstxt
from scripts.agent_artifacts.sitemaps import build_dataset_sitemaps, build_site_sitemap
from scripts.agent_artifacts.source_repos import SourceRepo, group_by_date, group_by_year


CLONE_BASE = Path("/tmp/agent-artifacts-src")


def main() -> int:
    per_dataset: dict[str, dict] = {}
    dataset_index_urls: list[str] = []

    for ds in DATASETS:
        print(f"[*] dataset={ds.id} — cloning {ds.source_repo}", flush=True)
        owner, name = ds.source_repo.split("/")
        repo = SourceRepo(owner, name, CLONE_BASE / name)
        try:
            repo.ensure_cloned()
            paths = repo.list_md_paths()
            variant = next(v for v in ds.variants if v.id == ds.primary_variant_id)
            filtered = [p for p in paths if p.startswith(variant.source_subpath)]
            print(f"    md_paths={len(paths)} primary_variant_paths={len(filtered)}", flush=True)

            date_buckets = group_by_date(filtered)
            if not date_buckets:
                print(f"!!  dataset={ds.id} has zero dated paths — aborting", file=sys.stderr)
                return 2
            year_buckets = group_by_year(date_buckets)

            sitemap_url = build_dataset_sitemaps(ds, year_buckets, REPO_ROOT)
            dataset_index_urls.append(sitemap_url)

            sorted_paths = sorted(filtered)
            all_dates = sorted(date_buckets.keys())
            per_dataset[ds.id] = {
                "total_documents": sum(len(v) for v in date_buckets.values()),
                "date_start": all_dates[0],
                "date_end": all_dates[-1],
                "sorted_paths": sorted_paths,
                "sitemap_url": sitemap_url,
            }
        finally:
            repo.cleanup()

    print("[*] writing site-level sitemap.xml", flush=True)
    build_site_sitemap(dataset_index_urls, REPO_ROOT)

    print("[*] writing agent-catalog.json", flush=True)
    build_catalog(per_dataset, REPO_ROOT)

    print("[*] writing llms.txt", flush=True)
    build_llmstxt(per_dataset, REPO_ROOT)

    print("[✓] done", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Make executable**

```bash
chmod +x scripts/build_agent_artifacts.py
```

- [ ] **Step 3: Run full build (may take 1-3 min)**

```bash
cd /Users/seohoseong/.openclaw/workspace/ai-readable-government
python3 scripts/build_agent_artifacts.py
```

Expected console output (numbers approximate):
```
[*] dataset=gazette — cloning hosungseo/gov-gazette-md
    md_paths=<~250k>  primary_variant_paths=<~128k>
[*] dataset=press — cloning hosungseo/gov-press-md
    md_paths=<~170k>  primary_variant_paths=<~170k>
[*] writing site-level sitemap.xml
[*] writing agent-catalog.json
[*] writing llms.txt
[✓] done
```

And on disk: `sitemap.xml`, `agent-catalog.json`, `llms.txt`, `sitemaps/` with `sitemap-gazette-index.xml`, `sitemap-gazette-2020.xml` through `-2026.xml`, same for press (with month splits in any year exceeding 45k).

- [ ] **Step 4: Spot-check output**

```bash
head -30 agent-catalog.json
head -30 llms.txt
ls sitemaps/ | head -20
wc -l sitemap.xml sitemaps/sitemap-gazette-index.xml sitemaps/sitemap-press-index.xml
```

Expected: all files non-empty, sitemap-gazette-index has 7 `<sitemap>` entries, sitemap-press-index has 7 or more.

- [ ] **Step 5: Commit (scripts + generated artifacts together)**

```bash
git add scripts/build_agent_artifacts.py sitemap.xml agent-catalog.json llms.txt sitemaps/
git commit -m "Add agent artifacts builder + first generated artifacts"
```

---

## Phase 6: Validator

### Task 9: validate_agent_artifacts.py

**Files:**
- Create: `scripts/validate_agent_artifacts.py`

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Validate agent artifacts — run after build_agent_artifacts.py.

Fails (non-zero exit) on any problem so CI catches broken artifacts
before they are pushed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from lxml import etree  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
URL_LIMIT = 50_000

CATALOG_REQUIRED_TOP = {
    "name", "description", "site_url", "generated_at", "generator",
    "license_note", "contact", "datasets", "how_to_use",
}
CATALOG_REQUIRED_DATASET = {
    "id", "name", "description", "format", "total_documents",
    "date_range", "update_cadence", "license", "source_repo",
    "variants", "frontmatter_fields", "sitemap_url", "sample_documents",
}


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def _head_ok(url: str, timeout: int = 15) -> bool:
    try:
        req = Request(url, method="HEAD", headers={"User-Agent": "ai-readable-government-validator"})
        with urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except HTTPError as e:
        # GitHub raw returns 200 on HEAD for public files; anything else is failure
        print(f"    HEAD {url} -> {e.code}", file=sys.stderr)
        return False
    except URLError as e:
        print(f"    HEAD {url} -> URLError: {e}", file=sys.stderr)
        return False


def validate_catalog() -> None:
    path = REPO_ROOT / "agent-catalog.json"
    if not path.exists():
        _fail("agent-catalog.json missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = CATALOG_REQUIRED_TOP - data.keys()
    if missing:
        _fail(f"catalog missing top-level keys: {sorted(missing)}")
    if not isinstance(data["datasets"], list) or not data["datasets"]:
        _fail("catalog.datasets must be a non-empty list")
    for i, ds in enumerate(data["datasets"]):
        miss = CATALOG_REQUIRED_DATASET - ds.keys()
        if miss:
            _fail(f"datasets[{i}] missing keys: {sorted(miss)}")
        if not ds["sample_documents"]:
            _fail(f"datasets[{i}] sample_documents is empty")
        url0 = ds["sample_documents"][0]
        print(f"[*] HEAD {url0}")
        if not _head_ok(url0):
            _fail(f"datasets[{i}] sample_documents[0] returned non-2xx: {url0}")
    print("[✓] agent-catalog.json OK")


def validate_sitemap(path: Path, expect_root: str) -> int:
    if not path.exists():
        _fail(f"{path} missing")
    try:
        tree = etree.parse(str(path))
    except etree.XMLSyntaxError as e:
        _fail(f"{path} XML parse error: {e}")
    root_tag = etree.QName(tree.getroot().tag).localname
    if root_tag != expect_root:
        _fail(f"{path} root is <{root_tag}>, expected <{expect_root}>")
    ns = {"sm": SITEMAP_NS}
    if expect_root == "urlset":
        urls = tree.xpath("//sm:url", namespaces=ns)
        if len(urls) > URL_LIMIT:
            _fail(f"{path} has {len(urls)} urls, exceeds {URL_LIMIT}")
        return len(urls)
    else:  # sitemapindex
        return len(tree.xpath("//sm:sitemap", namespaces=ns))


def validate_sitemaps() -> None:
    site_map = REPO_ROOT / "sitemap.xml"
    n_top = validate_sitemap(site_map, "sitemapindex")
    print(f"[✓] sitemap.xml OK ({n_top} dataset indexes)")
    for idx in sorted((REPO_ROOT / "sitemaps").glob("sitemap-*-index.xml")):
        n = validate_sitemap(idx, "sitemapindex")
        print(f"[✓] {idx.name} OK ({n} year maps)")
    for ym in sorted((REPO_ROOT / "sitemaps").glob("sitemap-*-[0-9][0-9][0-9][0-9]*.xml")):
        if ym.name.endswith("-index.xml"):
            continue
        n = validate_sitemap(ym, "urlset")
        print(f"[✓] {ym.name} OK ({n} urls)")


def validate_llmstxt() -> None:
    path = REPO_ROOT / "llms.txt"
    if not path.exists():
        _fail("llms.txt missing")
    text = path.read_text(encoding="utf-8")
    if not text.lstrip().startswith("# "):
        _fail("llms.txt must start with H1")
    h2_count = sum(1 for line in text.splitlines() if line.startswith("## "))
    if h2_count < 3:
        _fail(f"llms.txt has {h2_count} H2 sections, expected >=3")
    print(f"[✓] llms.txt OK ({h2_count} H2 sections)")


def validate_robots() -> None:
    path = REPO_ROOT / "robots.txt"
    if not path.exists():
        _fail("robots.txt missing")
    text = path.read_text(encoding="utf-8")
    if "Sitemap:" not in text:
        _fail("robots.txt missing Sitemap: directive")
    print("[✓] robots.txt OK")


def main() -> int:
    validate_robots()
    validate_llmstxt()
    validate_catalog()
    validate_sitemaps()
    print("[✓] all artifacts valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Install validator deps**

```bash
python3 -m pip install --user lxml
```

(jsonschema not required since we validate by field-presence.)

- [ ] **Step 3: Run validator against generated artifacts**

```bash
chmod +x scripts/validate_agent_artifacts.py
python3 scripts/validate_agent_artifacts.py
```

Expected: exit 0, every line prefixed `[✓]`. Each HEAD check hits `raw.githubusercontent.com` — will fail if Task 0 public transitions not yet done or propagated.

If HEAD check fails for sample URL: re-verify the repo is public with `curl -sI <url>`. Do not proceed until validator is green.

- [ ] **Step 4: Commit**

```bash
git add scripts/validate_agent_artifacts.py
git commit -m "Add agent artifacts validator"
```

---

## Phase 7: CI workflow

### Task 10: Weekly rebuild workflow

**Files:**
- Create: `.github/workflows/rebuild-agent-artifacts.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: Rebuild agent artifacts

on:
  schedule:
    - cron: "0 0 * * 1"   # Mondays 00:00 UTC = 09:00 KST
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  rebuild:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 1
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: python -m pip install lxml

      - name: Build agent artifacts
        run: python scripts/build_agent_artifacts.py

      - name: Validate artifacts
        run: python scripts/validate_agent_artifacts.py

      - name: Commit and push if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          if git diff --quiet -- sitemap.xml agent-catalog.json llms.txt sitemaps/; then
            echo "no artifact changes"
            exit 0
          fi
          git add sitemap.xml agent-catalog.json llms.txt sitemaps/
          git commit -m "Rebuild agent artifacts ($(date -u +%Y-%m-%d))"
          git push
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/rebuild-agent-artifacts.yml
git commit -m "Add weekly rebuild workflow for agent artifacts"
```

- [ ] **Step 3: Push and trigger manual run after push**

```bash
git push
```

Then in browser → repo → Actions tab → "Rebuild agent artifacts" → Run workflow → main → Run. Verify green check.

---

## Phase 8: README integration + end-to-end verification

### Task 11: Update README.md with Agent-ready section

**Files:**
- Modify: `README.md` (append section before any existing closing matter)

- [ ] **Step 1: Read current README**

```bash
wc -l README.md
tail -5 README.md
```

- [ ] **Step 2: Append the Agent-ready section**

Append the following to the end of `README.md`:

```markdown

## Agent-ready layer

In addition to the human-browsable reader, the site serves a machine-readable
discovery layer so external AI agents can enumerate and consume the underlying
markdown corpora directly.

- Machine catalog: [`/agent-catalog.json`](https://hosungseo.github.io/ai-readable-government/agent-catalog.json)
- Sitemap index: [`/sitemap.xml`](https://hosungseo.github.io/ai-readable-government/sitemap.xml)
- LLM summary: [`/llms.txt`](https://hosungseo.github.io/ai-readable-government/llms.txt)
- Crawler policy: [`/robots.txt`](https://hosungseo.github.io/ai-readable-government/robots.txt)

The catalog points agents at `raw.githubusercontent.com` URLs in the source
markdown repos (`gov-gazette-md`, `gov-press-md`); this repo itself stores
only the catalog and sitemap artifacts, rebuilt weekly via GitHub Actions.
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "Document agent-ready layer in README"
```

### Task 12: Live URL smoke check

**Files:** none (verification only — no edits)

- [ ] **Step 1: Wait for Pages to propagate (up to ~2 min after push)**

```bash
sleep 90
```

- [ ] **Step 2: Check all four artifact URLs return 200**

```bash
for p in robots.txt llms.txt sitemap.xml agent-catalog.json; do
  code=$(curl -sI "https://hosungseo.github.io/ai-readable-government/$p" | head -1)
  echo "$p -> $code"
done
```

Expected: each prints `HTTP/2 200`. If any is 404, re-check Pages "Source" branch/folder and re-push an empty commit if needed (`git commit --allow-empty -m "trigger pages rebuild" && git push`).

- [ ] **Step 3: Check isitagentready.com score**

Browser → https://isitagentready.com → enter `https://hosungseo.github.io/ai-readable-government/` → scan.

Expected:
- **Discoverability**: 100% (robots, llms.txt, sitemap all present)
- **Bot Access Control**: 100% (robots.txt allows AI bots)
- **Content Accessibility**: partial (no `Accept: text/markdown` because static Pages — known, accepted)
- **Protocol**: partial (no MCP server yet — known, deferred to next cycle)

Record the score in an issue on the repo for tracking.

- [ ] **Step 4: End-to-end agent fetch test (manual, one-time)**

In Claude Code (or the agent of your choice), paste:

```
Fetch https://hosungseo.github.io/ai-readable-government/agent-catalog.json,
pick the gazette dataset, fetch sample_documents[0], and summarize the
document in 3 bullets.
```

Expected: the agent returns a 3-bullet summary derived from the actual document. If the agent complains about inaccessible URL: re-check source repo visibility.

- [ ] **Step 5: Note completion**

Open an issue (or checklist in README) marking the MVP shipped with the isitagentready score and the agent fetch confirmation. No code change required.

---

## Phase 9: Cleanup

### Task 13: Delete empty `a2a_government_kr` folder

**Files:** none in this repo. Removes the scratch folder created earlier in conversation.

- [ ] **Step 1: Remove the unused scratch directory**

```bash
rmdir /Users/seohoseong/.openclaw/workspace/a2a_government_kr
```

Expected: no output. If `rmdir` refuses, the folder is not empty — list with `ls -la` and decide.

No commit needed (folder is outside this repo).

---

## Post-plan — handoff to next cycle

The following were explicitly deferred per spec Section 1.3:

- 입법예고 daily-pull pipeline (법제처 API)
- Real MCP server on Mac mini + `.well-known/mcp.json` + `agent-skills.json`
- Read-pattern logging and popularity roll-up
- Community comment endpoints

Each is a separate plan; do not add them here.
