"""Source-specific imports, candidate scope, persistence and rejection boundaries."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import unittest

import engine as e
from browser_runtime import browser_bootstrap, dispatch_json
from character_save import decode_character
from build_shuriken_marksman_requirements import BUILD_ID, build_documents, build_xml_documents
from extract_shuriken_profiles import profile_bundle
from letools import TYPES, decode_key, extract_character, import_profiles, merge_targets, profile_url
from requirements import read_document, write_document
from test_engine import first


class LEToolsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = profile_bundle()
        cls.imported = import_profiles(cls.bundle)

    def decoded_entry(self, index=0):
        entry = self.bundle["profiles"][index]
        return {"url": entry["url"], "data": decode_character(entry["save"], entry["save"]["characterName"])}

    def test_frozen_ui_records_have_76_items_and_decode_with_frozen_enum(self):
        enum = json.loads((e.ROOT / "sources/game-reference.json").read_text(encoding="utf-8"))["equipment_enum"]
        self.assertEqual({typ: i for i, typ in enumerate(TYPES)}, enum)
        self.assertEqual(len(self.bundle["profiles"]), 4)
        self.assertEqual([len(s["items"]) for s in self.imported["source"]["profiles"]], [19] * 4)
        self.assertEqual(decode_key("AGwRhQ"), "611")
        self.assertEqual(decode_key("UAzBMoVgNiA"), "002256")
        self.assertEqual(decode_key("IIwBgLKyiJA"), "1041011000")

    def test_template_is_exact_profile_union_without_old_xml_targets(self):
        endgame, leveling = build_documents()
        self.assertEqual(read_document(endgame)["profile"], self.imported["profile"])
        self.assertEqual({k: len(v) for k, v in endgame["targets"].items()},
                         {"uniques": 13, "equipment": 10, "altars": 1, "idols": 11, "bases": 0})
        self.assertEqual(sum(len(g["affixes"]) for g in endgame["targets"]["equipment"]), 28)
        self.assertNotIn(459, endgame["targets"]["uniques"])
        ring = next(g for g in endgame["targets"]["equipment"] if g["type"] == "RING")
        self.assertEqual(ring["affixes"], [507])
        self.assertEqual(leveling, build_xml_documents()[1])

    def test_special_classification_and_slot_origin_are_both_required(self):
        records = {p["character"]: {r["slot"]: r for r in p["items"]} for p in self.imported["source"]["profiles"]}
        self.assertNotIn(503, records["MaadCity"]["hands"]["affixes"])
        self.assertNotIn(503, records["MaadCity"]["hands"]["corrupted"])
        self.assertEqual(records["MAONG"]["head"]["affixes"], [611, 52])
        self.assertIn(713, records["MaadCity"]["waist"]["affixes"])
        self.assertTrue(records["MAONG"]["ring1"]["fixed"])
        for group in self.imported["profile"]["equipment"]:
            self.assertTrue(all(e.CATALOG["affixes"][str(a)]["special"] in {0, 1, 2, 5} for a in group["affixes"]))
        for group in self.imported["profile"]["idols"]:
            self.assertTrue(all(e.CATALOG["affixes"][str(a)]["special"] in {0, 5} for a in group["affixes"]))
        needle = [g for g in self.imported["profile"]["idols"] if g["type"] == "IDOL_1x1_LAGON"]
        self.assertFalse(needle)  # Unique needle is an ID target, never a normal idol group.

    def test_import_roundtrip_dispatch_and_every_ordinary_equipment_target_matches(self):
        before = deepcopy(self.bundle)
        imported = json.loads(dispatch_json(json.dumps({"path": "/api/profiles/import", "payload": {"bundle": self.bundle}})))
        self.assertEqual(imported, self.imported)
        self.assertEqual(self.bundle, before)
        build = {"id": imported["id"], "name": imported["name"], "enabled": True,
                 "profiles": {"endgame": imported["profile"], "leveling": e.empty_leveling()},
                 "requirement_sources": {"endgame": imported["source"]}}
        self.assertEqual(read_document(write_document(build, "endgame"))["profile"], imported["profile"])
        output = e.generate({"version": 1, "main_id": build["id"], "extra_t7": True, "builds": [build]})
        self.assertLessEqual(output["count"], 200)
        for group in imported["profile"]["equipment"]:
            for aid in group["affixes"]:
                self.assertEqual(first(output, group["type"], {aid: 7}, corrupted=True)["category"], "BD目标单T7")
        for group in imported["profile"]["altars"]:
            for aid in group["affixes"]:
                self.assertEqual(first(output, "IDOL_ALTAR", {aid: 1}, base=group["bases"][0], rarity="RARE")["category"], "祭坛一项目标")

    def test_scope_separation_and_duplicate_links(self):
        duplicate = deepcopy(self.bundle)
        duplicate["profiles"].append(deepcopy(duplicate["profiles"][0]))
        self.assertEqual(import_profiles(duplicate), self.imported)
        groups = [g for g in self.imported["profile"]["idols"] if g["type"] == "IDOL_1x3"]
        self.assertGreater(len(groups), 1)
        self.assertEqual({tuple(g["bases"]) for g in groups}, {(9,), (14,)})

    def test_normal_equipment_adds_its_base_but_unique_bases_are_not_added(self):
        entry = self.decoded_entry()
        profile, _ = extract_character(entry)
        self.assertEqual(profile["bases"], [])
        entry["data"]["equipment"]["head"]["id"] = "IIwBjYJnI"
        profile, _ = extract_character(entry)
        self.assertEqual(profile["bases"], [{"type": "HELMET", "bases": [2], "preferred_bases": []}])

    def test_unknown_and_malformed_data_fail_without_partial_import(self):
        for bad in ("https://example.com/profile/a/character/b", "http://www.lastepochtools.com/profile/a/character/b",
                    "https://www.lastepochtools.com/profile/a", "https://www.lastepochtools.com/profile/a/character/b?x=1",
                    "https://www.lastepochtools.com/profile/a/character/%2f..", "https://www.lastepochtools.com/profile/a/character/b/snapshot/aberroth"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                profile_url(bad)
        self.assertEqual(profile_url("https://lastepochtools.com/profile/zh/a/character/%E8%A7%92%E8%89%B2")[2], "角色")
        for key in ("A!", "A", "xxxxxxxxxxxx", "I"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                decode_key(key)
        bad = deepcopy(self.bundle)
        bad["profiles"][-1] = self.decoded_entry(-1)
        bad["profiles"][-1]["data"]["equipment"]["head"]["affixes"].append({"id": "AA"})
        with self.assertRaises(ValueError):
            import_profiles(bad)
        bad = deepcopy(self.bundle)
        bad["profiles"][-1] = self.decoded_entry(-1)
        bad["profiles"][-1]["data"]["idols"][0]["id"] = "UAzBMoVgNiA"
        with self.assertRaisesRegex(ValueError, "位置不符"):
            import_profiles(bad)
        self.assertEqual(len(browser_bootstrap()["config"]["builds"]), 6)

    @unittest.skipUnless(shutil.which("node"), "Node development checks")
    def test_api_relay_and_personal_save_contract(self):
        result = subprocess.run([shutil.which("node"), "--test", "tool/test_profile_relay.mjs"], cwd=e.ROOT,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_filtered_old_native_api_targets_match_independent_provider(self):
        from profile_proxy import compact_character
        fixture = json.loads((e.ROOT / "sources/builds/letools-character-api-2026-10-18.json").read_text(encoding="utf-8"))
        bundle = {"format": "letools-profile-bundle", "version": 1, "profiles": [
            {"url": row["url"], "data_version": row["response"]["buildInfo"]["data_version"],
             "data": row["response"]["buildInfo"]["data"]} for row in fixture["responses"]]}
        imported = import_profiles(bundle)
        self.assertEqual([len(s["items"]) for s in imported["source"]["profiles"]], [19] * 4)

        def pools(profile):
            result = {"uniques": sorted(profile["uniques"])}
            for category in ("equipment", "idols", "altars", "bases"):
                rows = [{k: sorted(v) if isinstance(v, list) else v for k, v in group.items() if v != []}
                        for group in profile[category]]
                result[category] = sorted(rows, key=lambda x: json.dumps(x, sort_keys=True))
            return result

        native = json.loads((e.ROOT / "sources/builds/maxroll-character-api-2026-10-18.json").read_text(encoding="utf-8"))
        other = import_profiles({"format": "letools-profile-bundle", "version": 1, "profiles": [
            compact_character(row["response"], row["url"]) for row in native["responses"]]})
        self.assertEqual(pools(imported["profile"]), pools(other["profile"]))

    def test_equipment_targets_only_regular_t6_t7_and_keep_valid_duplicate_id(self):
        entry = {"url": "https://www.lastepochtools.com/profile/test/character/test", "data": {
            "equipment": {"head": {"id": {"type_id": 0, "base": 2, "unique_id": 256}, "affixes": [
                {"id": 611, "tier": 7}, {"id": 52, "tier": 6}, {"id": 13, "tier": 5},
                {"id": 503, "tier": 6}, {"id": 1, "tier": 8}],
                "corruptedAffix": {"id": 503, "tier": 7}, "sealedAffix": {"id": 80, "tier": 6}}}, "idols": []}}
        targets, source = extract_character(entry)
        self.assertEqual(targets["equipment"][0]["affixes"], [611, 52, 503])
        self.assertEqual(source["items"][0]["affixes"], [611, 52, 503])
        details = source["items"][0]["affix_details"]
        self.assertEqual({(a["id"], a["origin"]) for a in details if a["target"]},
                         {(611, "affixes"), (52, "affixes"), (503, "affixes")})
        broken = deepcopy(entry)
        broken["data"]["equipment"]["head"]["affixes"][0].pop("tier")
        with self.assertRaisesRegex(ValueError, "阶数"):
            extract_character(broken)
