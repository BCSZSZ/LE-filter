"""The common document retains target semantics across both input sources."""
import json
import unittest
from copy import deepcopy

import engine as e
from requirements import read_document, write_document
from build_guide_835_requirements import build_document
from test_engine import first


def as_build(document):
    data = read_document(document)
    return {"id": data["id"], "name": data["name"], "enabled": True,
            "profiles": {"endgame": data["profile"], "leveling": e.empty_profile()},
            "requirement_sources": {"endgame": data["source"]}}


class RequirementTests(unittest.TestCase):
    def test_filter_roundtrip_without_strategy(self):
        for build in e.bootstrap()["config"]["builds"]:
            doc = write_document(build, "endgame")
            self.assertEqual(doc, write_document(as_build(doc), "endgame"))
            self.assertNotIn("leveling_slots", doc["targets"])
            self.assertNotIn("rules", doc.get("source", {}))
            original = build["profiles"]["endgame"]
            restored = read_document(doc)["profile"]
            for category in ("equipment", "idols", "altars"):
                for before, after in zip(original[category], restored[category]):
                    for key in ("bases", "affixes", "corrupted", "enchanted"):
                        self.assertEqual(before[key], after[key])
                    self.assertEqual(before.get("pair_bases", before["bases"]), after.get("pair_bases", after["bases"]))

    def test_explicit_unrestricted_idol_pair_roundtrip(self):
        doc = build_document()
        doc["targets"]["idols"][0]["pair_bases"] = []
        self.assertEqual(write_document(as_build(doc), "endgame")["targets"]["idols"][0]["pair_bases"], [])

    def test_guide_facts_and_frozen_output(self):
        doc = build_document()
        frozen = json.loads((e.ROOT / "requirements/bleed-skeleton-roamer-guide-835.endgame.json").read_text(encoding="utf-8"))
        self.assertEqual(doc, frozen)
        self.assertEqual({k: len(v) for k, v in doc["targets"].items()},
                         {"uniques": 25, "equipment": 13, "altars": 1, "idols": 3, "bases": 3})
        groups = {g["type"]: g for g in doc["targets"]["equipment"]}
        self.assertEqual(groups["BODY_ARMOR"]["affixes"], [406, 408, 407, 505, 52, 192])
        self.assertEqual(groups["AMULET"]["affixes"], [945])
        self.assertEqual(groups["AMULET"]["corrupted"], [1085, 1086])
        self.assertEqual(groups["ONE_HANDED_MACES"]["affixes"], [719])
        self.assertEqual(groups["SHIELD"]["affixes"], [80])
        self.assertEqual(doc["targets"]["idols"][2]["affixes"], [266, 287])
        self.assertEqual([i for i in doc["targets"]["uniques"] if e.CATALOG["uniques"][str(i)]["set"]], [77, 79, 171])

    def test_guide_converts_with_its_new_equipment_families(self):
        doc = build_document()
        build = as_build(doc)
        config = {"version": 1, "main_id": build["id"], "extra_t7": True, "builds": [build]}
        result = e.generate(config)
        for typ, aid in [("ONE_HANDED_MACES", 719), ("SHIELD", 80), ("CATALYST", 26)]:
            self.assertEqual(first(result, typ, {aid: 7})["category"], "BD目标单T7")
        self.assertEqual(first(result, "IDOL_1x3", {266: 1, 287: 1}, base=13, rarity="RARE", corrupted=True)["tier"], 3)
        self.assertEqual(first(result, "BODY_ARMOR", {406: 7, 192: 7})["category"], "BD双目标T7")
        build["requirement_sources"]["endgame"]["warnings"].append("metadata only")
        self.assertEqual(result["sha256"], e.generate(config)["sha256"])

    def test_invalid_documents_do_not_silently_lose_targets(self):
        with self.assertRaises(ValueError):
            read_document([])
        for edit in [lambda d: d.update(stage="unknown"),
                     lambda d: d["targets"]["idols"][0]["affixes"].append(897),
                     lambda d: d["targets"]["equipment"][0]["affixes"].append(1085),
                     lambda d: d["targets"]["equipment"][0].update(corrupted=[945]),
                     lambda d: d["source"].update(warnings="not a list"),
                     lambda d: d["targets"].update(leveling_slots={}),
                     lambda d: d["targets"]["bases"][0].update(affixes=[502])]:
            doc = deepcopy(build_document())
            edit(doc)
            with self.assertRaises(ValueError):
                read_document(doc)


if __name__ == "__main__":
    unittest.main()
