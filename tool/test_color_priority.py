"""First-match regressions for Comet, Inspiration, then BD identity."""
import unittest
from copy import deepcopy

import engine as e
from browser_runtime import browser_bootstrap
from test_engine import first, parsed


class ColorPriorityTests(unittest.TestCase):
    def config(self, main="flay-mana-lich"):
        config = deepcopy(e.bootstrap()["config"])
        config["main_id"] = main
        return config

    def assert_style(self, output, item, color, beam, tier):
        row = first(output, **item)
        node = parsed(output)[row["number"] - 1]
        self.assertEqual((node.findtext("color"), node.findtext("BeamColorOverride")), (color, beam), row)
        self.assertEqual(row["tier"], tier, row)
        self.assertEqual((node.findtext("SoundId"), node.findtext("MapIconId"), node.findtext("BeamSizeOverride")),
                         e.ALERTS[tier][1:4])

    def test_four_lp_traitors_tongue_is_comet_red_before_bd_color(self):
        for main in ("flay-mana-lich", "skeleton-necromancer"):
            output = e.generate(self.config(main))
            for lp in (3, 4):
                self.assert_style(output, {"typ": "ONE_HANDED_DAGGER", "uid": 342, "lp": lp, "rarity": "UNIQUE"},
                                  "7", "10", 4)

    def test_owned_uniques_keep_bd_colors_below_inspiration(self):
        for main in ("flay-mana-lich", "skeleton-necromancer"):
            output = e.generate(self.config(main))
            for uid, owner in ((475, "flay-mana-lich"), (471, "skeleton-necromancer"), (253, main)):
                color, beam = ("8", "11") if owner == main else ("12", "15")
                for lp, tier in ((0, 1), (1, 3), (2, 4), (3, 4), (4, 4)):
                    self.assert_style(output, {"uid": uid, "lp": lp, "rarity": "UNIQUE"},
                                      *(e.ALERTS[tier][4:6] if tier >= 3 else (color, beam)), tier)
                for ww, tier in ((13, 1), (14, 2), (16, 2), (17, 3), (19, 3), (20, 4)):
                    self.assert_style(output, {"uid": uid, "ww": ww, "rarity": "UNIQUE"},
                                      *(e.ALERTS[tier][4:6] if tier >= 3 else (color, beam)), tier)
                self.assert_style(output, {"uid": uid, "rarity": "LEGENDARY"}, "5", "7", 3)

    def test_t0_is_always_comet_red(self):
        for main in ("flay-mana-lich", "skeleton-necromancer"):
            output = e.generate(self.config(main))
            for uid, owner in ((277, "flay-mana-lich"), (208, "skeleton-necromancer"), (61, None)):
                for lp in (0, 1, 4):
                    self.assert_style(output, {"uid": uid, "lp": lp, "rarity": "UNIQUE"}, "7", "10", 4)

    def test_t0_and_needle_keep_bd_priority_with_complete_common_rules(self):
        for targets in ([61], [277], [344], [61, 277, 344]):
            config = self.config()
            for build in config["builds"]:
                build["enabled"] = build["id"] == config["main_id"]
                build["profiles"]["endgame"]["uniques"] = list(targets)
            before = deepcopy(config)
            output = e.generate(config)
            self.assertEqual(config, before)
            for row in output["rules"]:
                if row["tier"] < 4 and (row["owners"] or row["category"].startswith("BD暗金")):
                    self.assertFalse(set(row["uniques"]) & e.ULTRA_RARE_UNIQUES, row)
                if row["category"] == "BD暗金0LP也留":
                    self.assertNotIn(344, row["uniques"], row)
            self.assert_style(output, {"uid": 344, "rarity": "UNIQUE"},
                              *(('8', '11') if 344 in targets else ('3', '4')), 1)

    def test_owned_lp1_has_one_inspiration_pool_and_lp2_has_one_comet_pool(self):
        config = self.config()
        before = deepcopy(config)
        output = e.generate(config)
        self.assertEqual(config, before)
        self.assertFalse(any(row["owners"] and row["category"] == "任意LP=1" for row in output["rules"]))
        targets = set().union(*(set(e.expand_unique_sets(b["profiles"]["endgame"]["uniques"]))
                                for b in config["builds"] if b["enabled"])) - e.ULTRA_RARE_UNIQUES
        for lp, tier in ((1, 3), (2, 4)):
            category = f"BD暗金{lp}LP"
            entries = [(node, row) for node, row in zip(parsed(output), output["rules"])
                       if row["category"] == category]
            self.assertEqual(len(entries), 1)
            node, row = entries[0]
            self.assertEqual((row["role"], row["owners"], row["tier"]), ("通用", [], tier))
            self.assertEqual(set(row["uniques"]), targets)
            self.assertEqual(sum(c.get(e.XSI + "type") == "UniqueModifiersCondition"
                                 for c in node.find("conditions")), 1)
            bounds = e.condition(node, "PotentialCondition")
            self.assertEqual((bounds.findtext("MinLegendaryPotential"), bounds.findtext("MaxLegendaryPotential")),
                             (str(lp), str(lp)))
            for uid in (475, 471, 253):
                self.assertEqual(first(output, uid=uid, rarity="UNIQUE", lp=lp)["category"], category)
                self.assert_style(output, {"uid": uid, "rarity": "UNIQUE", "lp": lp},
                                  *e.ALERTS[tier][4:6], tier)
        self.assertEqual(first(output, uid=0, rarity="UNIQUE", lp=2)["category"], "任意LP=2")
        secondary = next(b for b in config["builds"] if b["id"] != config["main_id"])
        secondary["enabled"] = False
        self.assertEqual(first(e.generate(config), uid=471, rarity="UNIQUE", lp=2)["category"], "任意LP=2")

    def test_inspiration_idol_pair_precedes_primary_single_target(self):
        config = deepcopy(browser_bootstrap()["config"])
        config["main_id"] = "flay-lich-allie-guide"
        for build in config["builds"]:
            build["enabled"] = build["id"] in {"flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"}
        output = e.generate(config)
        self.assert_style(output, {"typ": "IDOL_1x1_LAGON", "base": 1, "affixes": {842: 1, 855: 1}}, "5", "7", 3)
        self.assert_style(output, {"typ": "IDOL_1x1_LAGON", "base": 1, "affixes": {851: 1, 855: 1}}, "5", "7", 3)
        self.assert_style(output, {"typ": "IDOL_1x1_LAGON", "base": 1, "affixes": {842: 1}}, "8", "11", 2)

    def test_all_double_t7_inspiration_precedes_bd_and_keeps_exact_tier(self):
        output = e.generate(self.config())
        self.assert_style(output, {"typ": "HELMET", "level": 84, "affixes": {406: 7, 503: 7, 17: 2, 1: 2}}, "7", "10", 4)
        self.assert_style(output, {"typ": "HELMET", "level": 84, "affixes": {34: 4, 503: 7, 17: 7, 1: 2}}, "5", "7", 3)
        self.assert_style(output, {"typ": "HELMET", "level": 85, "affixes": {34: 4, 503: 7, 17: 7, 1: 2}}, "5", "7", 3)
        self.assert_style(output, {"typ": "HELMET", "level": 84, "affixes": {34: 4, 503: 7, 17: 8}}, "8", "11", 1)
        self.assert_style(output, {"typ": "HELMET", "level": 100, "affixes": {34: 7}}, "8", "11", 2)
        self.assert_style(output, {"typ": "HELMET", "uid": 999, "rarity": "LEGENDARY", "affixes": {34: 7}}, "5", "7", 3)
        self.assert_style(output, {"typ": "HELMET", "uid": 999, "rarity": "LEGENDARY", "affixes": {503: 7, 17: 7, 1: 7}}, "7", "10", 4)

    def test_double_bd_targets_and_any_triples_are_comet_red(self):
        for main in ("flay-mana-lich", "skeleton-necromancer"):
            output = e.generate(self.config(main))
            for typ, affixes, owner in (("ONE_HANDED_AXE", {2: 7, 718: 7}, "flay-mana-lich"),
                                       ("BOOTS", {676: 7, 679: 7}, "skeleton-necromancer"),
                                       ("HELMET", {34: 7, 503: 7, 17: 7}, "flay-mana-lich"),
                                       ("HELMET", {406: 7, 503: 7, 17: 7}, "skeleton-necromancer"),
                                       ("HELMET", {34: 7, 406: 7, 503: 7}, main)):
                self.assert_style(output, {"typ": typ, "affixes": affixes}, "7", "10", 4)
            self.assert_style(output, {"typ": "HELMET", "affixes": {503: 7, 17: 7, 1: 7}}, "7", "10", 4)
            self.assert_style(output, {"typ": "HELMET", "affixes": {503: 7, 17: 7}}, "5", "7", 3)
            self.assert_style(output, {"typ": "HELMET", "affixes": {34: 7, 503: 7}}, "7", "10", 4)

    def test_all_23_equipment_types_are_kept_and_idols_are_outside_scope(self):
        output = e.generate(self.config())
        doubles = [r for r in output["rules"] if r["category"] == "任意双T7"]
        self.assertEqual(len(doubles), 1)
        self.assertEqual(set(doubles[0]["types"]), set(e.MANIFEST["scope_types"]))
        self.assertFalse(any(r["category"] == "BD双目标T7" for r in output["rules"]))
        self.assertEqual(len([r for r in output["rules"] if r["category"] == "三词条双T7"]), 2)
        general = next(r for r in output["rules"] if r["category"] == "任意至少三T7" and r["role"] == "通用")
        self.assertEqual(set(general["types"]), set(e.MANIFEST["scope_types"]))
        self.assertEqual(len(general["types"]), 23)
        for typ in general["types"]:
            self.assert_style(output, {"typ": typ, "affixes": {1154: 7, 1155: 7}}, "5", "7", 3)
            self.assertEqual(first(output, typ, {1154: 7, 1155: 7, 1156: 7},
                                   categories={"任意至少三T7"})["tier"], 4)
        self.assertEqual(first(output, "IDOL_1x2", {1154: 7, 1155: 7, 1156: 7},
                               categories={"任意至少三T7"})["action"], "HIDE")

    def test_three_affix_double_t7_requires_exactly_three_ordinary_slots(self):
        config = self.config()
        for build in config["builds"]:
            build["profiles"]["endgame"]["equipment"] = []
        output = e.generate(config)
        for affixes in ({503: 7, 17: 7, 1: 2}, {503: 7, 34: 2, 17: 7}):
            row = first(output, affixes=affixes)
            self.assertEqual(row["category"], "三词条双T7")
            self.assert_style(output, {"affixes": affixes}, "7", "10", 4)
        for affixes in ({503: 7, 17: 7}, {503: 7, 34: 2, 17: 7, 1: 2}):
            self.assertEqual(first(output, affixes=affixes)["category"], "任意双T7")
            self.assert_style(output, {"affixes": affixes}, "5", "7", 3)
        self.assertEqual(first(output, affixes={503: 7, 34: 2, 17: 8})["tier"], 1)
        self.assertEqual(first(output, affixes={503: 7, 17: 7, 1: 8})["category"], "三词条双T7")
        self.assertEqual(first(output, affixes={503: 7, 17: 7, 1: 2, 45: 3},
                               sealed_affixes=[45])["category"], "三词条双T7")
        self.assertEqual(first(output, affixes={503: 7, 34: 2, 17: 7, 1: 2, 45: 3},
                               sealed_affixes=[45])["category"], "任意双T7")
        scopes = []
        for node, row in zip(parsed(output), output["rules"]):
            if row["category"] != "三词条双T7":
                continue
            self.assertEqual(set(row["types"]), set(e.MANIFEST["scope_types"]))
            self.assertIn("未封印前缀", row["gate"])
            c = e.condition(node, "AffixCountCondition")
            self.assertEqual(c.findtext("sealedType"), "Any")
            self.assertEqual(c.findtext("minPrefixes"), c.findtext("maxPrefixes"))
            self.assertEqual(c.findtext("minSuffixes"), c.findtext("maxSuffixes"))
            scopes.append((c.findtext("minPrefixes"), c.findtext("minSuffixes")))
        self.assertEqual(set(scopes), {("1", "2"), ("2", "1")})

    def test_bd_double_comet_uses_one_t7_target_and_preserves_type_base_binding(self):
        config = self.config()
        main = next(b for b in config["builds"] if b["id"] == config["main_id"])
        secondary = next(b for b in config["builds"] if b["id"] != config["main_id"])
        main["profiles"]["endgame"]["equipment"] = [{"type": "HELMET", "bases": [70], "affixes": [34]}]
        secondary["profiles"]["endgame"]["equipment"] = [{"type": "HELMET", "bases": [70], "affixes": [406]}]
        before = deepcopy(config)
        output = e.generate(config)
        self.assertEqual(config, before)
        for targets in ({34: 7, 503: 7}, {406: 7, 503: 7}, {34: 7, 406: 7}):
            self.assertEqual(first(output, affixes=targets, base=70)["category"], "双T7含BD目标T7")
            self.assert_style(output, {"affixes": targets, "base": 70}, "7", "10", 4)
        for target_tier in (4, 8):
            self.assertEqual(first(output, affixes={34: target_tier, 503: 7, 17: 7, 1: 2},
                                   base=70)["category"], "任意双T7")
        self.assertEqual(first(output, affixes={34: 7, 503: 8}, base=70)["category"], "BD目标单T7")
        self.assertEqual(first(output, affixes={34: 7, 503: 7}, base=0)["category"], "任意双T7")
        self.assertEqual(first(output, typ="BODY_ARMOR", affixes={34: 7, 503: 7}, base=70)["category"], "任意双T7")
        common = [r for r in output["rules"] if r["category"] == "双T7含BD目标T7"]
        self.assertEqual(len(common), 1)
        self.assertEqual(set(common[0]["affixes"][1]), {34, 406})
        self.assertEqual(set(common[0]["owners"]), {main["name"], secondary["name"]})
        self.assertFalse(any(r["category"] == "BD双目标T7" for r in output["rules"]))
        secondary["enabled"] = False
        output = e.generate(config)
        self.assertEqual(first(output, affixes={406: 7, 503: 7}, base=70)["category"], "任意双T7")

    def test_all_builtin_combinations_fit_rule_limit(self):
        config = deepcopy(browser_bootstrap()["config"])
        ice = "ice-heartseeker-planner-al0dkyek"
        for selected in ({"flay-mana-lich", "skeleton-necromancer"},
                         {"flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"},
                         {"flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835", ice},
                         {"flay-mana-lich", "skeleton-necromancer", ice},
                         {"flay-mana-lich", "skeleton-necromancer", "flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"},
                         {"heartseeker-shuriken-marksman"}, {ice, "heartseeker-shuriken-marksman"}):
            for main in sorted(selected):
                config["main_id"] = main
                for build in config["builds"]:
                    build["enabled"] = build["id"] in selected
                before = deepcopy(config)
                output = e.generate(config)
                self.assertLessEqual(output["count"], 200)
                self.assertEqual(config, before)
                bands = [(0 if r["tier"] == 4 else 1 if r["tier"] == 3 else 2 if r["role"] == "主" else 3 if r["owners"] else 4, -r["tier"])
                         for r in output["rules"]]
                self.assertEqual(bands, sorted(bands))

    def test_all_templates_over_limit_report_without_truncation(self):
        config = deepcopy(browser_bootstrap()["config"])
        for build in config["builds"]:
            build["enabled"] = True
        before = deepcopy(config)
        with self.assertRaisesRegex(ValueError, "超过200条.*没有截断规则"):
            e.generate(config)
        self.assertEqual(config, before)

    def test_every_emitted_color_uses_bd_or_tier_and_unowned_silent_is_uncolored(self):
        output = e.generate(self.config())
        for node, row in zip(parsed(output), output["rules"]):
            if row["tier"] >= 3:
                expected = e.ALERTS[row["tier"]][4:6]
            elif row["owners"]:
                expected = ("8", "11") if row["role"] == "主" else ("12", "15")
            elif row["tier"]:
                expected = e.ALERTS[row["tier"]][4:6]
            else:
                self.assertEqual(node.findtext("recolor"), "false", row)
                continue
            self.assertEqual(node.findtext("recolor"), "true", row)
            self.assertEqual(node.findtext("color"), expected[0], row)
            if row["tier"]:
                self.assertEqual(node.findtext("BeamColorOverride"), expected[1], row)

    def test_covered_05_and_disabled_rules_preserve_saved_inputs_and_collection(self):
        config = self.config()
        build = next(b for b in config["builds"] if b["id"] == "flay-mana-lich")
        build["profiles"]["endgame"]["bases"] = [{"type": "BOOTS", "preferred_bases": [11], "bases": [9, 10]}]
        before = deepcopy(config)
        output = e.generate(config)
        self.assertFalse(any(r["category"].startswith("终局05") for r in output["rules"]))
        self.assertTrue(all(r["enabled"] for r in output["rules"]))
        for base in (9, 10, 11):
            self.assert_style(output, {"typ": "BOOTS", "base": base, "affixes": {36: 7}}, "8", "11", 2)
        self.assertEqual(config, before)

    def test_matching_pools_are_not_mixed_between_equipment_types(self):
        output = e.generate(self.config())
        self.assertEqual(first(output, "HELMET", {718: 7})["action"], "HIDE")
        self.assertEqual(first(output, "BOOTS", {718: 7})["action"], "HIDE")
        self.assert_style(output, {"typ": "ONE_HANDED_AXE", "affixes": {718: 7}}, "8", "11", 2)
        self.assert_style(output, {"typ": "ONE_HANDED_DAGGER", "affixes": {718: 7}}, "8", "11", 2)

    def test_shadowed_target_layers_are_omitted_without_widening_bases(self):
        config = self.config()
        main = next(b for b in config["builds"] if b["id"] == config["main_id"])
        secondary = next(b for b in config["builds"] if b["id"] != config["main_id"])
        alternative = next(int(k.split(":")[1]) for k in e.CATALOG["bases"] if k.startswith("HELMET:") and k != "HELMET:70")
        main["profiles"]["endgame"]["equipment"] = [{"type": "HELMET", "bases": [70], "affixes": [34, 406]}]
        secondary["profiles"]["endgame"]["equipment"] = [{"type": "HELMET", "bases": [70], "affixes": [406]}]
        before = deepcopy(config)
        output = e.generate(config)
        self.assertFalse(any(r["role"] == "副" and r["category"] in {"BD目标单T7", "非目标T7＋BD目标"} for r in output["rules"]))
        self.assert_style(output, {"typ": "HELMET", "base": 70, "affixes": {406: 7}}, "8", "11", 2)
        self.assertEqual(config, before)
        secondary["profiles"]["endgame"]["equipment"][0]["bases"] = [alternative]
        output = e.generate(config)
        self.assert_style(output, {"typ": "HELMET", "base": alternative, "affixes": {406: 7}}, "12", "15", 2)
        self.assert_style(output, {"typ": "HELMET", "base": 70, "affixes": {406: 7}}, "8", "11", 2)


if __name__ == "__main__":
    unittest.main()
