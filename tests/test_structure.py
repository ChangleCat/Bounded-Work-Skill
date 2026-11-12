from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml


SKILL_ROOT = Path(__file__).resolve().parent.parent


class StructureTests(unittest.TestCase):
    def test_all_yaml_and_json_files_parse_safely(self) -> None:
        for path in SKILL_ROOT.rglob("*.yaml"):
            with self.subTest(path=path):
                yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in SKILL_ROOT.rglob("*.json"):
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_relative_markdown_links_resolve(self) -> None:
        pattern = re.compile(r"\]\(([^)]+)\)")
        failures: list[str] = []
        for path in SKILL_ROOT.rglob("*.md"):
            for target in pattern.findall(path.read_text(encoding="utf-8")):
                target = target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (path.parent / target).resolve(strict=False)
                if not resolved.exists():
                    failures.append(f"{path.relative_to(SKILL_ROOT)} -> {target}")
        self.assertEqual(failures, [])

    def test_behavior_eval_catalog_is_complete(self) -> None:
        payload = json.loads((SKILL_ROOT / "evals/evals.json").read_text(encoding="utf-8"))
        actual = [entry["id"] for entry in payload["evals"]]
        expected = [f"BW-E{index:02d}" for index in range(1, 19)]
        self.assertEqual(actual, expected)
        for entry in payload["evals"]:
            self.assertTrue(entry["prompt"])
            self.assertTrue(entry["expected"])
            self.assertTrue(entry["forbidden"])

    def test_trigger_eval_catalog_balances_positive_and_negative_queries(self) -> None:
        payload = json.loads((SKILL_ROOT / "evals/trigger-evals.json").read_text(encoding="utf-8"))
        queries = payload["queries"]
        self.assertEqual(len({entry["id"] for entry in queries}), len(queries))
        self.assertGreaterEqual(sum(entry["should_trigger"] is True for entry in queries), 8)
        self.assertGreaterEqual(sum(entry["should_trigger"] is False for entry in queries), 8)

    def test_legacy_names_are_absent(self) -> None:
        legacy = re.compile(r"controlled[-_ ](?:execution|migration)|\bCE-E\d+\b", re.IGNORECASE)
        matches: list[str] = []
        for path in SKILL_ROOT.rglob("*"):
            if path == Path(__file__).resolve():
                continue
            if path.is_file() and path.suffix in {".md", ".yaml", ".json", ".py", ".txt"}:
                if legacy.search(path.read_text(encoding="utf-8")):
                    matches.append(str(path.relative_to(SKILL_ROOT)))
        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
