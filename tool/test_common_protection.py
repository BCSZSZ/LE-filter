"""Approved unique coverage, all sets and independent optional common rules."""
from copy import deepcopy
import json
import unittest

import engine as e
from compare_common_unique_protection import compare
from test_engine import first, parsed


class CommonProtectionTests(unittest.TestCase):
    def config(self):
        return {"version": 1, "main_id": "a", "extra_t7": False, "builds": [
            {"id": "a", "name": "A", "enabled": True,
             "profiles": {"endgame": e.empty_profile(), "leveling": e.empty_leveling()}}]}

    def test_missing_settings_default_without_overwriting_explicit_switches(self):
        config = self.config()
        before = deepcopy(config)
        normalized = e.normalize_config(config)
        self.assertFalse(normalized["common"]["exalted_experimentals_enabled"])
        self.assertTrue(normalized["common"]["common_uniques_enabled"])
        self.assertTrue(normalized["common"]["common_sets_enabled"])
        self.assertEqual(config, before)
        normalized["common"].update(exalted_experimentals_enabled=True, common_uniques_enabled=False, common_sets_enabled=False)
        self.assertEqual(e.normalize_config(normalized), normalized)
        for field in ("exalted_experimentals_enabled", "common_uniques_enabled", "common_sets_enabled"):
            invalid = deepcopy(normalized)
            invalid["common"][field] = "false"
            with self.assertRaisesRegex(ValueError, "共通规则开关"):
                e.normalize_config(invalid)

    def test_experimentals_default_off_and_return_only_when_enabled(self):
        config = self.config()
        output = e.generate(config)
        self.assertFalse(any(row["source_raxx_rule"] == 68 for row in output["rules"]))
        self.assertEqual(first(output, "BOOTS", {676: 6})["action"], "HIDE")
        config["common"] = e.default_common()
        config["common"]["exalted_experimentals_enabled"] = True
        row = first(e.generate(config), "BOOTS", {676: 6})
        self.assertEqual((row["source_raxx_rule"], row["tier"]), (68, 1))
        self.assertEqual(e.BASE[68].findtext("isEnabled"), "true")

    def test_independent_switches_keep_t0_bd_sets_and_higher_lp_protection(self):
        config = self.config()
        config["common"] = e.default_common()
        output = e.generate(config)
        self.assertEqual(first(output, uid=35, rarity="UNIQUE")["category"], "通用暗金0LP保护")
        self.assertEqual(first(output, uid=77, rarity="SET")["category"], "通用套装保护")
        config["common"]["common_uniques_enabled"] = False
        output = e.generate(config)
        self.assertEqual(first(output, uid=35, rarity="UNIQUE")["action"], "HIDE")
        self.assertEqual(first(output, uid=77, rarity="SET")["category"], "通用套装保护")
        config["common"].update(common_uniques_enabled=True, common_sets_enabled=False)
        output = e.generate(config)
        self.assertEqual(first(output, uid=35, rarity="UNIQUE")["category"], "通用暗金0LP保护")
        self.assertEqual(first(output, uid=77, rarity="SET")["action"], "HIDE")
        config["common"]["common_uniques_enabled"] = False
        config["builds"][0]["profiles"]["endgame"]["uniques"] = [13, 77]
        output = e.generate(config)
        for uid, rarity in ((13, "UNIQUE"), (77, "SET"), (78, "SET"), (79, "SET")):
            self.assertEqual(first(output, uid=uid, rarity=rarity)["category"], "BD暗金0LP也留")
        self.assertEqual(first(output, uid=61, rarity="UNIQUE")["category"], "T0极稀有暗金0LP起")
        self.assertEqual(first(output, uid=0, rarity="UNIQUE", lp=1)["category"], "任意LP=1")

    def test_historical_pure_reroll_comparison_remains_reproducible(self):
        result = compare()
        self.assertFalse(result["replacementApplied"])
        self.assertEqual(result["counts"], {
            "old": {"uniques": 138, "sets": 21, "total": 159},
            "proposed": {"uniques": 97, "sets": 23, "total": 120},
            "overlap": {"uniques": 47, "sets": 18, "total": 65},
            "old_only": {"uniques": 91, "sets": 3, "total": 94},
            "new_only": {"uniques": 50, "sets": 5, "total": 55}})
        groups = {name: {row["id"] for row in rows} for name, rows in result["groups"].items()}
        self.assertEqual(len(groups["overlap"] | groups["old_only"]), 159)
        self.assertTrue(groups["new_only"] <= e.COMMON_ZERO_LP_IDS)
        self.assertEqual(result["oldOnlyReasons"], {"random_reroll_zero": 10, "not_random_dash": 61, "cocooned_hidden": 23})
        output = e.generate(self.config())
        self.assertEqual(first(output, uid=413, rarity="UNIQUE")["category"], "通用暗金0LP保护")
        self.assertEqual(first(output, uid=11, rarity="UNIQUE")["category"], "通用暗金0LP保护")
        frozen = json.loads((e.ROOT / "analysis/common-unique-comparison.json").read_text(encoding="utf-8"))
        self.assertEqual(result, frozen)

    def test_all_positive_uniques_and_all_sets_collected_without_bd_targets(self):
        metadata = e.read_json("sources/tunklab-unique-reroll-2026-10-18.json")["items"]
        positive = [item for item in metadata if not item["catalog_hidden"] and not item["set"]
                    and not item["type"].startswith("IDOL_") and item["can_drop_randomly"] and item["reroll_chance"] > 0]
        all_sets = {int(uid) for uid, item in e.CATALOG["uniques"].items() if item["set"] and not item["hidden"]}
        self.assertEqual((len(positive), len(all_sets)), (97, 61))
        self.assertEqual(e.COMMON_SET_IDS, all_sets)
        output = e.generate(self.config())
        for item in positive:
            expected = "T0极稀有暗金0LP起" if item["id"] in e.ULTRA_RARE_UNIQUES else "通用暗金0LP保护"
            self.assertEqual(first(output, item["type"], uid=item["id"], rarity="UNIQUE")["category"], expected)
        for uid in all_sets:
            self.assertEqual(first(output, e.CATALOG["uniques"][str(uid)]["type"], uid=uid, rarity="SET")["category"], "通用套装保护")
        rows = [r for r in output["rules"] if r["category"] in {"通用暗金0LP保护", "通用套装保护"}]
        self.assertEqual(len(rows), 2)
        catalog = e.bootstrap()["catalog"]
        self.assertEqual(set(catalog["common_set_ids"]), all_sets)
        self.assertEqual(set(catalog["common_unique_ids"]) | e.ULTRA_RARE_UNIQUES, e.COMMON_UNIQUE_IDS)

    def test_only_seven_legacy_uniques_removed_and_nonrandom_cocoons_retained(self):
        comparison = compare()
        old = {i["id"] for key in ("overlap", "old_only") for i in comparison["groups"][key] if not i["set"]}
        removed = {13, 296, 311, 422, 460, 474, 480}
        self.assertEqual(old - e.COMMON_UNIQUE_IDS, removed)
        self.assertEqual(len(e.COMMON_UNIQUE_IDS - old), 50)
        self.assertEqual(len(e.COMMON_UNIQUE_IDS), 181)
        output = e.generate(self.config())
        for uid in removed:
            self.assertEqual(first(output, e.CATALOG["uniques"][str(uid)]["type"], uid=uid, rarity="UNIQUE")["action"], "HIDE")
        for item in comparison["groups"]["old_only"]:
            if not item["set"] and (item["is_cocooned"] or not item["can_drop_randomly"]):
                self.assertEqual(first(output, item["type"], uid=item["id"], rarity="UNIQUE")["category"], "通用暗金0LP保护")

    def test_new_sets_can_be_disabled_without_disabling_bd_full_set_collection(self):
        config = self.config()
        config["common"] = e.default_common()
        config["common"]["common_sets_enabled"] = False
        output = e.generate(config)
        for uid in (5, 77, 86):
            self.assertEqual(first(output, e.CATALOG["uniques"][str(uid)]["type"], uid=uid, rarity="SET")["action"], "HIDE")
        config["builds"][0]["profiles"]["endgame"]["uniques"] = [5]
        output = e.generate(config)
        for uid in e.SET_MEMBERS[5]:
            self.assertEqual(first(output, e.CATALOG["uniques"][str(uid)]["type"], uid=uid, rarity="SET")["category"], "BD暗金0LP也留")

    def test_common_unique_and_set_pools_remain_complete_with_bd_and_t0_overlap(self):
        config = self.config()
        config["builds"][0]["profiles"]["endgame"]["uniques"] = [337, 61, 77]
        output = e.generate(config)
        rows = {row["category"]: row for row in output["rules"]}
        self.assertEqual(set(rows["通用暗金0LP保护"]["uniques"]), e.COMMON_UNIQUE_IDS)
        self.assertEqual(set(rows["通用套装保护"]["uniques"]), e.COMMON_SET_IDS)
        self.assertEqual(set(e.bootstrap()["catalog"]["common_unique_ids"]), e.COMMON_UNIQUE_IDS)
        self.assertEqual(first(output, "BOOTS", uid=337, rarity="UNIQUE")["category"], "BD暗金0LP也留")
        self.assertEqual(first(output, uid=61, rarity="UNIQUE")["category"], "T0极稀有暗金0LP起")
        self.assertEqual(first(output, uid=77, rarity="SET")["category"], "BD暗金0LP也留")

    def test_common_idol_survives_an_identical_earlier_bd_predicate(self):
        config = self.config()
        config["common"] = e.default_common()
        config["common"]["unique_idols"] = [211]
        config["builds"][0]["profiles"]["endgame"]["uniques"] = [211, 344]
        output = e.generate(config)
        rows = [row for row in output["rules"] if row["category"] == "共通暗金神像"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["uniques"], [211])
        self.assertEqual((rows[0]["role"], rows[0]["owners"]), ("通用", []))
        needle = [row for row in output["rules"] if row["category"] == "先驱者之针常驻" and not row["owners"]]
        self.assertEqual(len(needle), 1)
        self.assertEqual(needle[0]["uniques"], [344])
        self.assertEqual(first(output, "IDOL_2x2", uid=211, rarity="UNIQUE")["category"], "BD暗金0LP也留")
        self.assertEqual(first(output, "IDOL_1x1_ETERRA", uid=344, rarity="UNIQUE")["role"], "主")

    def test_generic_unique_rules_are_identical_when_bd_targets_or_main_change(self):
        categories = {"通用暗金0LP保护", "通用套装保护", "共通暗金神像", "先驱者之针常驻",
                      "名单WW14–16", "名单WW17–19", "WW20+", "任意LP=1", "任意LP=2", "任意LP≥3"}

        def generic_rules(output):
            result = {}
            for node, row in zip(parsed(output), output["rules"]):
                if row["category"] in categories and not row["owners"]:
                    node.find("Order").text = "0"
                    result[row["category"]] = e.tree(node)
            self.assertEqual(set(result), categories)
            return result

        config = self.config()
        baseline = generic_rules(e.generate(config))
        main = config["builds"][0]
        other = deepcopy(main)
        other.update(id="b", name="B")
        config["builds"].append(other)
        main["profiles"]["endgame"]["uniques"] = [337, 211, 344, 61, 77, 487]
        other["profiles"]["endgame"]["uniques"] = [337, 277, 246, 78, 488]
        for main_id in ("a", "b"):
            config["main_id"] = main_id
            before = deepcopy(config)
            self.assertEqual(generic_rules(e.generate(config)), baseline)
            self.assertEqual(config, before)
        main["enabled"] = False
        self.assertEqual(generic_rules(e.generate(config)), baseline)


if __name__ == "__main__":
    unittest.main()
