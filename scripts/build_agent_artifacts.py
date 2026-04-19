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
