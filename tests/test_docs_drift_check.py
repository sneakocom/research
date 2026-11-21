"""Tests for the O21 receipt cache in tools/docs_drift_check.py.

The cache contract: a completed scan of a clean git checkout is reused
only when (repo HEAD, guard script bytes, --allow list) are all
unchanged. A new commit, an edit to the guard script, a changed
exemption list, or a dirty tree must each force a full rescan, so the
cache can never mask a real change.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUARD = REPO_ROOT / "tools" / "docs_drift_check.py"
ORG_LINE = "Old home: https://github.com/opsle/gearbox\n"


def git(root: Path, *argv: str) -> None:
    subprocess.run(
        ["git", "-C", str(root),
         "-c", "user.email=test@example.invalid", "-c", "user.name=Test",
         *argv],
        check=True, capture_output=True, text=True,
    )


def make_repo(root: Path, readme_lines: list[str]) -> Path:
    root.mkdir(parents=True)
    git(root, "init", "-q")
    (root / "README.md").write_text("".join(readme_lines), encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "seed")
    return root


def run_guard(guard: Path, repo: Path, cache_dir: Path, *extra: str) -> str:
    out = subprocess.run(
        [sys.executable, str(guard), str(repo),
         "--cache-dir", str(cache_dir), *extra],
        capture_output=True, text=True,
    )
    return out.stdout


def header(stdout: str) -> str:
    return stdout.splitlines()[0]


class ReceiptCacheTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="drift-cache-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cache = self.tmp / "cache"
        self.repo = make_repo(self.tmp / "repo", ["# Fixture\n", ORG_LINE])

    def test_first_run_scans_second_run_hits_cache(self) -> None:
        first = run_guard(GUARD, self.repo, self.cache)
        self.assertIn("1 fail, 0 review", header(first))
        self.assertNotIn("cached", header(first))

        receipts = list(self.cache.glob("*.receipt.json"))
        self.assertEqual(len(receipts), 1)
        data = json.loads(receipts[0].read_text(encoding="utf-8"))
        head = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertEqual(data["head"], head)
        self.assertEqual(data["fail_count"], 1)
        self.assertEqual(data["review_count"], 0)

        second = run_guard(GUARD, self.repo, self.cache)
        self.assertIn("1 fail, 0 review", header(second))
        self.assertIn("cached", header(second))
        # identical findings, not just identical counts
        self.assertEqual(
            sorted(l for l in first.splitlines() if l.startswith("FAIL")),
            sorted(l for l in second.splitlines() if l.startswith("FAIL")),
        )

    def test_new_commit_invalidates(self) -> None:
        run_guard(GUARD, self.repo, self.cache)
        with (self.repo / "README.md").open("a", encoding="utf-8") as fh:
            fh.write(ORG_LINE)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "second org ref")
        third = run_guard(GUARD, self.repo, self.cache)
        self.assertIn("2 fail, 0 review", header(third))
        self.assertNotIn("cached", header(third))
        fourth = run_guard(GUARD, self.repo, self.cache)
        self.assertIn("2 fail, 0 review", header(fourth))
        self.assertIn("cached", header(fourth))

    def test_dirty_tree_never_cached(self) -> None:
        run_guard(GUARD, self.repo, self.cache)
        with (self.repo / "README.md").open("a", encoding="utf-8") as fh:
            fh.write(ORG_LINE)  # uncommitted: HEAD unchanged, tree changed
        dirty = run_guard(GUARD, self.repo, self.cache)
        self.assertIn("2 fail, 0 review", header(dirty))
        self.assertNotIn("cached", header(dirty))

    def test_allow_list_change_invalidates(self) -> None:
        run_guard(GUARD, self.repo, self.cache)
        exempt = run_guard(GUARD, self.repo, self.cache, "--allow", "README.md")
        self.assertIn("0 fail, 0 review", header(exempt))
        self.assertNotIn("cached", header(exempt))

    def test_script_edit_invalidates(self) -> None:
        guard_copy = self.tmp / "guard_copy.py"
        shutil.copy(GUARD, guard_copy)
        run_guard(guard_copy, self.repo, self.cache)
        hit = run_guard(guard_copy, self.repo, self.cache)
        self.assertIn("cached", header(hit))
        with guard_copy.open("a", encoding="utf-8") as fh:
            fh.write("\n# comment-only edit changes the script hash\n")
        after_edit = run_guard(guard_copy, self.repo, self.cache)
        self.assertNotIn("cached", header(after_edit))
        self.assertIn("1 fail, 0 review", header(after_edit))

    def test_no_cache_flag_scans_and_writes_nothing(self) -> None:
        out = subprocess.run(
            [sys.executable, str(GUARD), str(self.repo),
             "--cache-dir", str(self.cache), "--no-cache"],
            capture_output=True, text=True,
        )
        self.assertIn("1 fail, 0 review", header(out.stdout))
        self.assertFalse(self.cache.exists())


if __name__ == "__main__":
    unittest.main()
