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
