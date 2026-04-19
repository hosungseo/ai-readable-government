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
