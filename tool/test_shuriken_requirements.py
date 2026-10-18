"""Keep source targets separate from Very Strict and other BD policies."""
from copy import deepcopy
import hashlib
import json
import unittest

import engine as e
from build_shuriken_marksman_requirements import BUILD_ID, SOURCE, SOURCE_SHA256, build_documents, build_xml_documents
from requirements import read_document, write_document
from test_engine import first


class ShurikenRequirementsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.endgame, cls.leveling = build_documents()
        cls.build = {"id": BUILD_ID, "name": "追心手里剑", "enabled": True,
                     "profiles": {stage: read_document(doc)["profile"]
                                  for stage, doc in (("endgame", cls.endgame), ("leveling", cls.leveling))},
                     "requirement_sources": {"endgame": cls.endgame["source"], "leveling": cls.leveling["source"]}}
        cls.config = {"version": 1, "main_id": BUILD_ID, "extra_t7": True, "builds": [cls.build]}
        cls.output = e.generate(cls.config)

    def test_frozen_source_target_scope_and_requirements_roundtrip(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)
        original = build_xml_documents()[0]
        self.assertEqual({k: len(v) for k, v in original["targets"].items()},
                         {"uniques": 11, "equipment": 10, "altars": 1, "idols": 7, "bases": 0})
        self.assertEqual(original["targets"]["uniques"], [17, 133, 134, 189, 256, 271, 337, 413, 436, 459, 477])
        groups = {g["type"]: g for g in original["targets"]["equipment"]}
        self.assertEqual(groups["HELMET"]["affixes"], [611, 52])
        self.assertEqual(groups["RING"]["affixes"], [507, 503])
        self.assertEqual(groups["BOW"]["affixes"], [432, 6])
        self.assertEqual(groups["BOW"]["corrupted"], [966])
        self.assertEqual(groups["AMULET"]["affixes"], [88])
        self.assertEqual(self.leveling["targets"], e.empty_leveling())
        self.assertEqual(self.build["id"], BUILD_ID)
        for document in (self.endgame, self.leveling):
            frozen = json.loads((e.ROOT / f"requirements/{BUILD_ID}.{document['stage']}.json").read_text(encoding="utf-8"))
            self.assertEqual(document, frozen)
            self.assertEqual(write_document(self.build, document["stage"]), frozen)

    def test_existing_base_gates_replace_source_thresholds(self):
        self.assertFalse(self.output["warnings"])
        before = deepcopy(self.config)
        self.assertEqual(e.generate(self.config), self.output)
        self.assertEqual(self.config, before)
        row = first(self.output, "AMULET", {88: 7}, corrupted=True, fp=0)
        self.assertEqual((row["category"], row["tier"]), ("BD目标单T7", 2))
        self.assertEqual(first(self.output, "AMULET", {88: 2, 17: 7}, level=84)["category"], "非目标T7＋BD目标")
        self.assertEqual(first(self.output, "AMULET", {88: 2, 17: 7}, level=85)["action"], "HIDE")
        self.assertEqual(first(self.output, "BOW", {966: 7}, categories={"BD目标单T7", "非目标T7＋BD目标"})["action"], "HIDE")
        self.assertEqual(first(self.output, "AMULET", {503: 7}, categories={"BD目标单T7"})["action"], "HIDE")
        self.assertEqual(first(self.output, "IDOL_ALTAR", {1094: 1}, base=11, rarity="RARE", corrupted=True)["category"], "祭坛一项目标")
        self.assertEqual(first(self.output, uid=337, rarity="UNIQUE", lp=0)["category"], "BD暗金0LP也留")

    def test_idol_scopes_and_special_references_do_not_change_ordinary_counts(self):
        idols = {g["type"]: g for g in build_xml_documents()[0]["targets"]["idols"]}
        large = idols["IDOL_1x3"]
        self.assertEqual(large["bases"], [10, 11, 12, 13, 14])
        self.assertEqual(large["pair_bases"], [4, 9, 10, 11, 12, 13, 14])
        self.assertEqual((large["affixes"], large["enchanted"], large["corrupted"]), ([942, 117], [892], [1052]))
        for affixes, tier in (({116: 1, 892: 7, 1043: 7}, 2), ({116: 1, 763: 1}, 3)):
            self.assertEqual(first(self.output, "IDOL_1x3", affixes, base=14, rarity="RARE", corrupted=True)["tier"], tier)
        categories = {"神像一普通目标", "神像两普通目标"}
        self.assertEqual(first(self.output, "IDOL_1x3", {942: 1}, base=4, rarity="RARE", categories=categories)["action"], "HIDE")
        self.assertEqual(first(self.output, "IDOL_1x3", {942: 1, 117: 1}, base=4, rarity="RARE", categories=categories)["action"], "HIDE")
        self.assertEqual(first(self.output, "IDOL_1x3", {942: 1, 117: 1}, base=9, rarity="RARE", categories=categories)["tier"], 3)
        self.assertEqual(first(self.output, "IDOL_1x1_ETERRA", {1070: 1}, base=0, rarity="RARE", categories=categories)["action"], "HIDE")
        for group in idols.values():
            self.assertTrue(all(e.CATALOG["affixes"][str(a)]["special"] in {0, 5} for a in group["affixes"]))


if __name__ == "__main__":
    unittest.main()
