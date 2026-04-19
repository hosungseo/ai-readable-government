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
