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
