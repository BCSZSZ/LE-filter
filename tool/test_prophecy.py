"""Guard the published scientific snapshot and workbook, using only stdlib."""

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from scripts.build_pages import ROOT, PROBABILITY_WORKBOOK, build_probability_page


class ProphecyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "analysis/prophecy-probabilities.json").read_text(encoding="utf-8"))
        cls.pools = json.loads((ROOT / "sources/t7-equipment-pools.json").read_text(encoding="utf-8"))

    def test_complete_verified_pool_snapshot(self):
        self.assertEqual(self.data["sourceSHA256"], hashlib.sha256(
            (ROOT / "sources/t7-equipment-pools.json").read_bytes()).hexdigest())
        self.assertEqual(len(self.data["profiles"]), 36)
        self.assertEqual(len({p["id"] for p in self.data["profiles"]}), 36)
        self.assertEqual({p["typeID"] for p in self.data["profiles"]}, set(range(24)) - {11})
        for p in self.pools["profiles"]:
            self.assertEqual(len(p["affixes"]), len({a["id"] for a in p["affixes"]}))
            self.assertTrue(p["prophecyReward"]["forceExalted"])
            self.assertEqual(p["prophecyReward"]["rarityGroup"], 5)
        blocked = {a["id"] for p in self.pools["profiles"] if p["id"] == "body_armor-sentinel"
                   for a in p["affixes"] if not a["naturalT6Eligible"]}
        self.assertEqual(blocked, {7, 10, 13, 17, 19, 24, 45, 656})

    def test_distributions_and_independent_previous_ring_result(self):
        for p in self.data["profiles"]:
            for regime in p["probabilities"].values():
                for distribution in regime.values():
                    self.assertEqual(len(distribution), 5)
                    self.assertAlmostEqual(sum(distribution), 1, places=11)
                    self.assertTrue(all(0 <= probability <= 1 for probability in distribution))
        ring = next(p for p in self.data["profiles"] if p["id"] == "ring-none")
        previous = json.loads((ROOT / "analysis/t7-lens-probability-results.json").read_text(encoding="utf-8"))
        for row in previous["ordinary_exalted_ring_prophecy"]:
            actual = ring["probabilities"]["9"][row["lens"] or "none"]
            for a, b in zip(actual, row["p_T7_count"]):
                self.assertAlmostEqual(a, b, places=12)

    def test_natural_components_preserve_exalted_denominator(self):
        for profile in self.data["profiles"]:
            components = profile["naturalComponents"]
            self.assertEqual(set(components), {"0", "4", "9", "11"})
            for rows in components.values():
                self.assertEqual(len(rows), 5)
                self.assertEqual(rows[0], {"p_T7_count": [1., 0., 0., 0., 0.], "p_exalted": 0.})
                for row in rows:
                    count, exalted = row["p_T7_count"], row["p_exalted"]
                    self.assertAlmostEqual(sum(count), 1., places=11)
                    self.assertTrue(all(-1e-12 <= p <= 1. + 1e-12 for p in count))
                    self.assertTrue(0 <= exalted <= 1)
                    self.assertLessEqual(sum(count[1:]), exalted + 1e-12)
            for n in (1, 2):
                self.assertEqual(components["11"][n], components["9"][n])
            for n in (3, 4):
                self.assertAlmostEqual(components["11"][n]["p_exalted"],
                                       .75 * components["9"][n]["p_exalted"] + .25, places=12)

    def test_player_class_type_selection_keeps_native_candidate_distribution(self):
        path = ROOT / "sources/t7-natural-type-selection.json"
        self.assertEqual(self.data["typeSelectionSHA256"], hashlib.sha256(path.read_bytes()).hexdigest())
        selection = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(self.data["naturalRarity"]["typeSelection"], selection)
        self.assertEqual({p["id"] for p in selection["players"]}, set(range(5)))
        for player in selection["players"]:
            self.assertEqual(player["classRequirementMask"], 1 << player["id"])
            self.assertEqual(set(map(int, player["raw2EquipmentFactorByType"])), set(range(24)) - {11})
            modes = player["modes"]
            for mode in modes.values():
                self.assertEqual(mode["candidateCount"], 42)
                self.assertEqual(len(mode["acceptWeightsByTypeID"]), 42)
                self.assertAlmostEqual(sum(mode["acceptWeightsByTypeID"]), mode["acceptedWeightSum"], places=12)
            gear, idols = modes["ordinaryRaw0_1_3_4"], modes["ordinaryRaw2"]
            expected = gear["acceptedWeightSum"] / idols["acceptedWeightSum"]
            for coefficient in player["raw2EquipmentFactorByType"].values():
                self.assertAlmostEqual(coefficient, expected, places=12)

    def test_workbook_values_match_every_profile_and_lens(self):
        ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        with zipfile.ZipFile(ROOT / PROBABILITY_WORKBOOK) as archive:
            sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        cells = {cell.get("r"): cell for cell in sheet.findall(".//s:c", ns)}
        for row, profile in enumerate(self.data["profiles"], 5):
            expected = [profile["probabilities"]["9"][lens][i]
                        for lens in ("none", "quality", "origin", "finality") for i in (1, 2)]
            for col, value in zip("CDEFGHIJ", expected):
                cell = cells[f"{col}{row}"]
                self.assertNotIn(cell.get("t"), ("s", "inlineStr", "str", "e"))
                self.assertAlmostEqual(float(cell.find("s:v", ns).text), value, places=14)

    def test_static_page_is_self_contained_and_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            build_probability_page(target)
            first = {p.name: p.read_bytes() for p in (target / "probability").iterdir()}
            build_probability_page(target)
            self.assertEqual(first, {p.name: p.read_bytes() for p in (target / "probability").iterdir()})
            self.assertEqual(first["probabilities.json"], (ROOT / "analysis/prophecy-probabilities.json").read_bytes())
            self.assertEqual(first["probabilities.xlsx"], (ROOT / PROBABILITY_WORKBOOK).read_bytes())
            self.assertIn(b'./model.mjs?v=', first["app.js"])

    @unittest.skipUnless(shutil.which("node"), "Node is used for browser model checks")
    def test_browser_model(self):
        result = subprocess.run([shutil.which("node"), "--test", "tool/test_prophecy.mjs"],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
