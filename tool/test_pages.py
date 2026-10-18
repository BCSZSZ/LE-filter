"""Verify that publication contains a complete engine and independent targets."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path

import engine
from browser_runtime import browser_bootstrap, browser_startup_snapshot, dispatch_json
from build_pages import build_archive, build_startup_snapshot
from requirements import write_document


class PagesTests(unittest.TestCase):
    def test_static_bootstrap_preserves_all_editor_inputs_and_frozen_targets(self):
        full = browser_bootstrap()
        snapshot = browser_startup_snapshot()
        self.assertEqual(snapshot["config"], full["config"])
        for key in full["catalog"]:
            if key != "unique_drops":
                self.assertEqual(snapshot["catalog"][key], full["catalog"][key])
        for uid, row in full["catalog"]["unique_drops"]["items"].items():
            self.assertEqual(snapshot["catalog"]["unique_drops"]["items"][uid],
                             {key: row[key] for key in ("kind", "display", "iconUrl") if key in row})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bootstrap.json"
            first = build_startup_snapshot(path)
            self.assertEqual(first, build_startup_snapshot(path))
            self.assertEqual(json.loads(first), snapshot)
            self.assertEqual(path.read_bytes(), first)
            self.assertLess(len(first), len(json.dumps(full, ensure_ascii=False, separators=(",", ":")).encode()))

    def test_archive_runs_in_isolation_and_matches_local_xml(self):
        code = """
import json
from browser_runtime import browser_bootstrap
from engine import generate
config = browser_bootstrap()['config']
default = generate(config)['sha256']
for b in config['builds']:
    b['enabled'] = b['id'] in {'flay-lich-allie-guide', 'bleed-skeleton-roamer-guide-835'}
config['main_id'] = 'flay-lich-allie-guide'
guides = generate(config)['sha256']
for b in config['builds']:
    b['enabled'] = b['id'] == 'ice-heartseeker-planner-al0dkyek'
config['main_id'] = 'ice-heartseeker-planner-al0dkyek'
ice = generate(config)['sha256']
for b in config['builds']:
    b['enabled'] = b['id'] == 'heartseeker-shuriken-marksman'
config['main_id'] = 'heartseeker-shuriken-marksman'
print(json.dumps([default, guides, ice, generate(config)['sha256']]))
"""
        config = deepcopy(browser_bootstrap()["config"])
        expected = [engine.generate(config)["sha256"]]
        for build in config["builds"]:
            build["enabled"] = build["id"] in {"flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"}
        config["main_id"] = "flay-lich-allie-guide"
        expected.append(engine.generate(config)["sha256"])
        for build in config["builds"]:
            build["enabled"] = build["id"] == "ice-heartseeker-planner-al0dkyek"
        config["main_id"] = "ice-heartseeker-planner-al0dkyek"
        expected.append(engine.generate(config)["sha256"])
        for build in config["builds"]:
            build["enabled"] = build["id"] == "heartseeker-shuriken-marksman"
        config["main_id"] = "heartseeker-shuriken-marksman"
        expected.append(engine.generate(config)["sha256"])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            build_archive(path / "one.zip")
            build_archive(path / "two.zip")
            self.assertEqual((path / "one.zip").read_bytes(), (path / "two.zip").read_bytes())
            with zipfile.ZipFile(path / "one.zip") as archive:
                archive.extractall(path)
                self.assertEqual(archive.read("templates/LE-base-v1.xml"), (engine.ROOT / "templates/LE-base-v1.xml").read_bytes())
            result = subprocess.run([sys.executable, "-X", "utf8", "-c", code], cwd=path,
                                    env={**os.environ, "PYTHONPATH": str(path / "tool")},
                                    text=True, capture_output=True, check=True, encoding="utf-8")
            self.assertEqual(json.loads(result.stdout), expected)

    def test_six_separate_examples_and_file_only_dispatch(self):
        boot = json.loads(dispatch_json(json.dumps({"path": "/api/bootstrap"})))
        builds = {b["id"]: b for b in boot["config"]["builds"]}
        self.assertEqual(len(builds), 6)
        for original in engine.bootstrap()["config"]["builds"]:
            self.assertEqual(builds[original["id"]], original)
        for slug in ("flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835", "ice-heartseeker-planner-al0dkyek",
                     "heartseeker-shuriken-marksman"):
            self.assertFalse(builds[slug]["enabled"])
            for stage in ("endgame", "leveling"):
                frozen = json.loads((engine.ROOT / f"requirements/{slug}.{stage}.json").read_text(encoding="utf-8"))
                self.assertEqual(write_document(builds[slug], stage), frozen)
        for name, spec in engine.EVIDENCE["strict_inputs"].items():
            xml = (engine.ROOT / spec["file"]).read_text(encoding="utf-8-sig")
            result = json.loads(dispatch_json(json.dumps({"path": "/api/import", "payload": {"xml": xml}})))
            self.assertEqual(result, engine.extract(xml))
        result = json.loads(dispatch_json(json.dumps({"path": "/api/import-url", "payload": {"url": "https://example.com"}})))
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
