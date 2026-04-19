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
