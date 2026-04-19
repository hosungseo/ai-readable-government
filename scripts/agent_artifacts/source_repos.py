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
        # core.quotePath=false disables git's default double-quoting of non-ASCII
        # paths; without it, Korean filenames come back as `"...".md` and the
        # .endswith('.md') check silently misses 98% of the corpus.
        result = subprocess.run(
            ["git",
             "-C", str(self.clone_dir),
             "-c", "core.quotePath=false",
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
