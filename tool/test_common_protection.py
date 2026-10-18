"""Independent optional common rules preserve the complete old fixed pool."""
from copy import deepcopy
import json
import unittest

import engine as e
from compare_common_unique_protection import compare
from test_engine import first


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
        self.assertEqual(first(output, uid=13, rarity="UNIQUE")["category"], "通用暗金0LP保护")
        self.assertEqual(first(output, uid=77, rarity="SET")["category"], "通用套装保护")
        config["common"]["common_uniques_enabled"] = False
        output = e.generate(config)
        self.assertEqual(first(output, uid=13, rarity="UNIQUE")["action"], "HIDE")
        self.assertEqual(first(output, uid=77, rarity="SET")["category"], "通用套装保护")
        config["common"].update(common_uniques_enabled=True, common_sets_enabled=False)
        output = e.generate(config)
        self.assertEqual(first(output, uid=13, rarity="UNIQUE")["category"], "通用暗金0LP保护")
        self.assertEqual(first(output, uid=77, rarity="SET")["action"], "HIDE")
        config["common"]["common_uniques_enabled"] = False
        config["builds"][0]["profiles"]["endgame"]["uniques"] = [13, 77]
        output = e.generate(config)
        for uid, rarity in ((13, "UNIQUE"), (77, "SET"), (78, "SET"), (79, "SET")):
            self.assertEqual(first(output, uid=uid, rarity=rarity)["category"], "BD暗金0LP也留")
        self.assertEqual(first(output, uid=61, rarity="UNIQUE")["category"], "T0极稀有暗金0LP起")
        self.assertEqual(first(output, uid=0, rarity="UNIQUE", lp=1)["category"], "任意LP=1")

    def test_proposal_is_comparison_only_and_not_the_active_fixed_list(self):
        result = compare()
        self.assertFalse(result["replacementApplied"])
        self.assertEqual(result["counts"], {
            "old": {"uniques": 138, "sets": 21, "total": 159},
            "proposed": {"uniques": 97, "sets": 23, "total": 120},
            "overlap": {"uniques": 47, "sets": 18, "total": 65},
            "old_only": {"uniques": 91, "sets": 3, "total": 94},
            "new_only": {"uniques": 50, "sets": 5, "total": 55}})
        groups = {name: {row["id"] for row in rows} for name, rows in result["groups"].items()}
        self.assertEqual(groups["overlap"] | groups["old_only"], e.COMMON_ZERO_LP_IDS)
        self.assertFalse(groups["new_only"] & e.COMMON_ZERO_LP_IDS)
        self.assertEqual(result["oldOnlyReasons"], {"random_reroll_zero": 10, "not_random_dash": 61, "cocooned_hidden": 23})
        output = e.generate(self.config())
        self.assertEqual(first(output, uid=413, rarity="UNIQUE")["category"], "通用暗金0LP保护")
        self.assertEqual(first(output, uid=11, rarity="UNIQUE")["action"], "HIDE")
        frozen = json.loads((e.ROOT / "analysis/common-unique-comparison.json").read_text(encoding="utf-8"))
        self.assertEqual(result, frozen)


if __name__ == "__main__":
    unittest.main()
