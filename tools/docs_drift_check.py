#!/usr/bin/env python3
"""Docs-drift guard for Opsle repositories (autopilot O12, 2026-11-13).

The Core 4 friction pass (2026-11-10 to 11-13) found the same decay four
times in four shapes, all in prose and metadata that no verify command
exercises. Three of those shapes are deterministic greps, not intelligence
work. This script runs them over local clones:

  (a) deleted-org references: "github.com/opsle/" or "github:opsle/"
      anywhere in Markdown or package metadata. The opsle org was deleted
      in October 2026; canonical owner is sneakocom. Pinned historical
      evidence may legitimately quote old URLs, so paths can be exempted
      with --allow <path-substring> (repeatable). Exemptions must be
      deliberate and reviewed, never broad.
  (b) retired-product claims: the literal "Opsle Tasks" appearing in a
      README outside a past-tense or retirement context is flagged for
      human review (heuristic, reported as REVIEW not FAIL). Opsle Tasks
      retired 2026-10-31.
  (c) version-literal drift: a sub-package README naming "version X.Y.Z"
      or a tarball "*-X.Y.Z.tgz" that disagrees with the nearest
      package.json version.

Usage:
  python3 tools/docs_drift_check.py <repo-dir> [<repo-dir> ...]
          [--allow <path-substring>] ...

Exit code: 0 when no FAIL findings, 1 otherwise. REVIEW findings are
printed but do not fail the run; a human (or the autopilot) decides
whether the present-tense mention is legitimate history.

Stdlib only. No network. Deterministic output (sorted findings).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".toml", ".txt"}
SKIP_DIRS = {".git", "node_modules", "_work", "dist", "build"}
ORG_PATTERNS = ["github.com/opsle/", "github:opsle/"]
RETIRED_PRODUCT = "Opsle Tasks"
PAST_TENSE_HINTS = (
    "retir", "former", "was ", "were ", "historical", "archive",
    "past tense", "no longer", "consolidated",
)
VERSION_RE = re.compile(r"(?:version\s+|[-_])(\d+\.\d+\.\d+)(?:\.tgz|\b)")


def iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            yield path


def package_version(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    version = data.get("version")
    return version if isinstance(version, str) else None


def check_repo(root: Path, allow: list[str]) -> tuple[list[str], list[str]]:
    fails: list[str] = []
    reviews: list[str] = []
    root = root.resolve()

    def exempt(path: Path) -> bool:
        rel = str(path.relative_to(root))
        return any(a in rel for a in allow)

    # (c) needs the version map first: dir -> declared version
    versions: dict[Path, str] = {}
    for pkg in root.rglob("package.json"):
        if any(part in SKIP_DIRS for part in pkg.parts):
            continue
        v = package_version(pkg)
        if v:
            versions[pkg.parent] = v

    for path in iter_text_files(root):
        rel = str(path.relative_to(root))
        try:
            lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        is_readme = path.name.lower().startswith("readme")
        # nearest declared version for (c): walk up from the file's dir
        declared = None
        cursor = path.parent
        while cursor >= root:
            if cursor in versions:
                declared = versions[cursor]
                break
            if cursor == root:
                break
            cursor = cursor.parent
        for lineno, line in enumerate(lines, 1):
            if not exempt(path):
                for pat in ORG_PATTERNS:
                    if pat in line:
                        fails.append(f"FAIL org-ref {rel}:{lineno}: {line.strip()[:120]}")
            if is_readme and RETIRED_PRODUCT in line:
                lowered = line.lower()
                if not any(hint in lowered for hint in PAST_TENSE_HINTS):
                    reviews.append(
                        f"REVIEW retired-product {rel}:{lineno}: {line.strip()[:120]}"
                    )
            if is_readme and declared and "package.json" not in rel:
                for m in VERSION_RE.finditer(line):
                    if m.group(1) != declared:
                        fails.append(
                            f"FAIL version-drift {rel}:{lineno}: names {m.group(1)}, "
                            f"package declares {declared}: {line.strip()[:100]}"
                        )
    return fails, reviews


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repos", nargs="+", help="repository directories to check")
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        help="path substring exempt from the org-ref check (repeatable)",
    )
    args = parser.parse_args()

    all_fails: list[str] = []
    all_reviews: list[str] = []
    for repo in args.repos:
        fails, reviews = check_repo(Path(repo), args.allow)
        print(f"== {repo}: {len(fails)} fail, {len(reviews)} review ==")
        all_fails.extend(fails)
        all_reviews.extend(reviews)
    for line in sorted(all_fails):
        print(line)
    for line in sorted(all_reviews):
        print(line)
    print(f"TOTAL: {len(all_fails)} fail, {len(all_reviews)} review")
    return 1 if all_fails else 0


if __name__ == "__main__":
    sys.exit(main())
