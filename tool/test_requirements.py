"""The common document retains target semantics across both input sources."""
import json
import unittest
from copy import deepcopy

import engine as e
from requirements import read_document, write_document
from build_guide_835_requirements import build_document, build_leveling_document
from build_flay_allie_requirements import build_documents as build_allie_documents
from test_engine import first


def as_build(document):
    data = read_document(document)
    return {"id": data["id"], "name": data["name"], "enabled": True,
            "profiles": {"endgame": data["profile"], "leveling": e.empty_leveling()},
            "requirement_sources": {"endgame": data["source"]}}


class RequirementTests(unittest.TestCase):
    def test_allie_guide_targets_and_roundtrip(self):
        endgame, leveling = build_allie_documents()
        self.assertEqual({k: len(v) for k, v in endgame["targets"].items()},
                         {"uniques": 17, "equipment": 10, "altars": 0, "idols": 4, "bases": 8})
        self.assertEqual(sum(len(g["bases"]) for g in endgame["targets"]["bases"]), 28)
        groups = {g["type"]: g for g in endgame["targets"]["equipment"]}
        self.assertEqual(groups["ONE_HANDED_AXE"]["affixes"], [943, 2, 718, 724])
        self.assertEqual(groups["ONE_HANDED_DAGGER"]["affixes"], [943, 2, 718, 724])
        self.assertNotIn(502, groups["BELT"]["affixes"])
        self.assertEqual(groups["BOOTS"]["affixes"], [502, 97, 505, 36, 715])
        self.assertEqual(endgame["targets"]["idols"][2]["affixes"], [843, 854, 842, 856])
        self.assertEqual(endgame["targets"]["idols"][2]["corrupted"], [1069])
        self.assertEqual(endgame["targets"]["idols"][3],
                         {"type": "IDOL_1x1_ETERRA", "bases": [2], "affixes": [835, 837]})
        self.assertTrue({132, 253, 277, 353, 413, 469, 477} <= set(endgame["targets"]["uniques"]))
        self.assertIn(75, groups["BELT"]["affixes"])
        self.assertEqual(endgame["source"]["updated"], "2026-10-07")
        self.assertIn(376, endgame["targets"]["uniques"])
        self.assertNotIn(374, endgame["targets"]["uniques"])
        self.assertEqual(len(leveling["targets"]["affixes"]), 19)
        self.assertNotIn(119, leveling["targets"]["affixes"])
        build = as_build(endgame)
        build["profiles"]["leveling"] = read_document(leveling)["profile"]
        build["requirement_sources"]["leveling"] = leveling["source"]
        for doc in (endgame, leveling):
            frozen = json.loads((e.ROOT / f"requirements/{doc['id']}.{doc['stage']}.json").read_text(encoding="utf-8"))
            self.assertEqual(doc, frozen)
            self.assertEqual(doc, write_document(build, doc["stage"]))

    def test_allie_guide_uses_current_base_rules(self):
        endgame, leveling = build_allie_documents()
        build = as_build(endgame)
        build["profiles"]["leveling"] = read_document(leveling)["profile"]
        result = e.generate({"version": 1, "main_id": build["id"], "extra_t7": True, "builds": [build]})
        self.assertEqual(first(result, "ONE_HANDED_AXE", {943: 7, 724: 7})["category"], "BD双目标T7")
        self.assertEqual(first(result, "IDOL_1x2", {139: 1}, base=0, rarity="RARE")["tier"], 2)
        self.assertEqual(first(result, "IDOL_1x1_LAGON", {843: 1, 854: 1}, base=1, rarity="RARE")["tier"], 3)

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

    def test_compact_leveling_roundtrip_and_validation(self):
        doc = {"format": "le-filter-requirements", "version": 1, "id": "level", "name": "练级BD",
               "stage": "leveling", "targets": {"affixes": [26, 945, 98, 643, 502, 45, 28, 27],
               "bases": [{"type": "RING", "bases": [7]}, {"type": "RELIC", "bases": [15, 18]}]}}
        data = read_document(doc)
        build = {"id": data["id"], "name": data["name"], "profiles": {"endgame": e.empty_profile(), "leveling": data["profile"]}}
        self.assertEqual(write_document(build, "leveling"), doc)
        for aid in [897, 1085, 287, 999999]:
            invalid = deepcopy(doc);invalid["targets"]["affixes"].append(aid)
            with self.assertRaises(ValueError):
                read_document(invalid)
        invalid = deepcopy(doc);invalid["targets"]["bases"][0]["bases"] = [999999]
        with self.assertRaises(ValueError):
            read_document(invalid)

    def test_guide_leveling_is_explicit_and_independent(self):
        doc = build_leveling_document()
        self.assertEqual(doc["targets"]["affixes"], [26, 945, 98, 643, 502, 45, 28, 27])
        self.assertEqual(sum(len(g["bases"]) for g in doc["targets"]["bases"]), 5)
        self.assertEqual(doc["id"], build_document()["id"])
        frozen = json.loads((e.ROOT / "requirements/bleed-skeleton-roamer-guide-835.leveling.json").read_text(encoding="utf-8"))
        self.assertEqual(doc, frozen)

    def test_legacy_config_migration_retains_other_stage_and_original(self):
        config = e.bootstrap()["config"]
        legacy = e.empty_profile()
        legacy["equipment"] = [{"type": "TWO_HANDED_AXE", "bases": [], "affixes": [98]}]
        legacy["idols"] = deepcopy(config["builds"][0]["profiles"]["endgame"]["idols"])
        legacy["leveling_slots"] = {"154": {"enabled": True, "types": ["WAND"], "bases": [], "affixes": [38]},
                                     "160": {"enabled": True, "types": ["RING"], "bases": [7], "affixes": []}}
        config["builds"][0]["profiles"]["leveling"] = legacy
        migrated = e.normalize_config(config)
        self.assertEqual(migrated["builds"][0]["profiles"]["leveling"], {"affixes": [38, 98], "bases": [{"type": "RING", "bases": [7]}]})
        self.assertEqual(migrated["builds"][0]["legacy_leveling"], legacy)
        self.assertEqual(migrated["builds"][0]["profiles"]["endgame"], config["builds"][0]["profiles"]["endgame"])
        self.assertEqual(migrated["main_id"], config["main_id"])
        self.assertEqual(migrated, e.normalize_config(migrated))
        self.assertIn("leveling_slots", config["builds"][0]["profiles"]["leveling"])

    def test_legacy_leveling_document_keeps_non_equipment_as_source(self):
        doc = build_document();doc["stage"] = "leveling"
        data = read_document(doc)
        self.assertEqual(set(data["profile"]), {"affixes", "bases"})
        self.assertEqual(data["source"]["legacy_targets"], doc["targets"])
        build = {"id": data["id"], "name": data["name"], "profiles": {"leveling": data["profile"]},
                 "requirement_sources": {"leveling": data["source"]}}
        self.assertEqual(read_document(write_document(build, "leveling"))["source"], data["source"])


if __name__ == "__main__":
    unittest.main()
