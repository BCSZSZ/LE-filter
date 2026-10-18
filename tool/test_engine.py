"""Bounded source, XML and policy tests. Does not emulate the game client."""
import hashlib
import unittest
import xml.etree.ElementTree as ET
from copy import deepcopy

import engine as e
from generate_filter import tree
from verify_generated_filter import ids, predicate


def parsed(output):
    return sorted(ET.fromstring(output["xml"]).find("rules"), key=lambda r: int(r.findtext("Order")))


def first(output, typ="HELMET", affixes=None, categories=None, **extra):
    item = {"type": typ, "base": 0, "affixes": affixes or {}, "level": 100, "rarity": "EXALTED",
            "corrupted": False, "fp": 0, "uid": -1, "lp": 0, "ww": 0, **extra}
    def matches(c):
        if c.get(e.XSI + "type") == "AffixCountCondition":
            # Only the newly audited Any-sealed count bounds are modelled here.
            if c.findtext("sealedType", "Any") != "Any":
                return None
            sealed = item.get("sealed_affixes", ())
            definitions = [e.CATALOG["affixes"].get(str(aid)) for aid in item["affixes"] if aid not in sealed]
            if any(a is None for a in definitions):
                return None
            prefixes = sum(a["prefix"] for a in definitions)
            suffixes = len(definitions) - prefixes
            for name, count in (("Prefixes", prefixes), ("Suffixes", suffixes)):
                low, high = c.findtext("min" + name), c.findtext("max" + name)
                if low and count < int(low) or high and count > int(high):
                    return False
            return True
        if c.get(e.XSI + "type") == "UniqueModifiersCondition":
            return item["uid"] in ids(c, "Uniques/UniqueId")
        if c.get(e.XSI + "type") == "PotentialCondition":
            for field, value in [("LegendaryPotential", item["lp"]), ("WeaversWill", item["ww"])]:
                low, high = c.findtext("Min" + field), c.findtext("Max" + field)
                if low and value < int(low) or high and value > int(high):
                    return False
            return True
        return predicate(c, item)
    for node, row in zip(parsed(output), output["rules"]):
        if categories is not None and row["category"] not in categories and row["action"] != "HIDE":
            continue
        if node.findtext("isEnabled") == "true" and all(matches(c) is True for c in node.find("conditions")):
            return row
    raise AssertionError("No final hide")


class ToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = e.bootstrap()["config"]
        cls.output = e.generate(cls.config)

    def test_source_intelligence(self):
        old = e.extract((e.ROOT / "sources/builds/maxroll-skeleton-necromancer-strict.xml").read_text(encoding="utf-8"))
        new = e.extract((e.ROOT / "sources/builds/maxroll-skeleton-necromancer-very-strict.xml").read_text(encoding="utf-8"))
        for key in ["equipment", "idols", "altars"]:
            normalized = lambda p: [{k: g[k] for k in ["type", "bases", "affixes", "corrupted", "enchanted"]} for g in p[key]]
            self.assertEqual(normalized(old["profile"]), normalized(new["profile"]))
        self.assertEqual(len(old["profile"]["equipment"]), 9)
        chest = next(g for g in old["profile"]["equipment"] if g["type"] == "BODY_ARMOR")
        self.assertEqual(chest["affixes"], [406])
        large = next(g for g in old["profile"]["idols"] if g["type"] == "IDOL_1x3")
        self.assertEqual(large["affixes"], [285, 287, 941])
        self.assertEqual(large["enchanted"], [897])
        self.assertEqual(new["profile"]["bases"], [])

    def test_xml_and_styles(self):
        rules = parsed(self.output)
        self.assertLessEqual(len(rules), 200)
        self.assertEqual([int(r.findtext("Order")) for r in rules], list(range(len(rules))))
        self.assertEqual(rules[-1].findtext("type"), "HIDE")
        self.assertFalse(len(rules[-1].find("conditions")))
        for rule, row in zip(rules, self.output["rules"]):
            cue = e.ALERTS[row["tier"]]
            self.assertEqual((rule.findtext("SoundId"), rule.findtext("MapIconId"), rule.findtext("BeamSizeOverride")), cue[1:4])
            if row["enabled"]:
                for c in rule.find("conditions"):
                    if c.get(e.XSI + "type") == "AffixCondition":
                        self.assertTrue(len(c.find("affixes")), row["name"])
                    if c.get(e.XSI + "type") == "SubTypeCondition" and row["source_raxx_rule"] != 37:
                        self.assertTrue(len(c.find("type")), row["name"])
            if row["category"].startswith("神像"):
                self.assertTrue(all(e.CATALOG["affixes"][str(i)]["special"] in {0, 5} for pool in row["affixes"] for i in pool))
        self.assertEqual(e.generate(self.config)["xml"], self.output["xml"])

    def test_equipment_priority_and_t8(self):
        cases = [
            ("HELMET", {503:7, 1:7, 17:7}, 4, "任意至少三T7", 100),
            ("HELMET", {503:7, 1:7}, 3, "任意双T7", 100),
            ("HELMET", {34:7, 503:7}, 4, "双T7含BD目标T7", 100),
            ("BOOTS", {676:7, 679:7}, 4, "双T7含BD目标T7", 100),
            ("HELMET", {34:7}, 2, "BD目标单T7", 100),
            ("HELMET", {34:4, 503:7}, 1, "非目标T7＋BD目标", 84),
            ("HELMET", {1156:7}, 0, "Raxx通用", 84),
            ("HELMET", {503:8}, 1, "Raxx通用", 100),
            ("HELMET", {503:8, 34:7}, 2, "BD目标单T7", 100),
            ("HELMET", {503:8, 1:7, 17:7}, 4, "三词条双T7", 100),
            ("HELMET", {718:7}, 0, "Raxx通用", 84)]
        for typ, affixes, tier, category, level in cases:
            row = first(self.output, typ, affixes, level=level)
            self.assertEqual((row["tier"], row["category"]), (tier, category), (typ, affixes, row))
        boots = [r for r in self.output["rules"] if r["category"] == "双T7含BD目标T7" and r["types"] == ["BOOTS"]]
        self.assertEqual(len(boots), 1)
        self.assertEqual(set(boots[0]["affixes"][1]), {28,36,676,679})

    def test_idol_normal_count(self):
        for affixes, tier in [({941:1,287:1},3), ({941:1,897:7},2), ({941:1,1071:1},2),
                              ({941:1,287:1,897:7,1071:1},3)]:
            row = first(self.output, "IDOL_1x3", affixes, base=8, rarity="RARE", corrupted=True)
            self.assertEqual(row["tier"], tier)
            self.assertTrue(row["category"].startswith("神像"))
        self.assertEqual(first(self.output,"IDOL_2x1",{862:1},base=1,rarity="RARE")["tier"],2)

    def test_non_target_single_t7_exits_at_85(self):
        for extra_t7 in (False, True):
            config = deepcopy(self.config)
            config["extra_t7"] = extra_t7
            out = e.generate(config)
            for affixes in ({34: 4, 503: 7}, {406: 4, 503: 7}):
                self.assertEqual(first(out, "HELMET", affixes, level=84)["category"], "非目标T7＋BD目标")
                for level in (85, 100):
                    self.assertEqual(first(out, "HELMET", affixes, level=level)["action"], "HIDE")
            self.assertEqual(first(out, "HELMET", {1156: 7}, level=84)["action"], "SHOW" if extra_t7 else "HIDE")
            for level in (85, 100):
                self.assertEqual(first(out, "HELMET", {1156: 7}, level=level)["action"], "HIDE")
                for aid in (34, 406):
                    self.assertEqual(first(out, "HELMET", {aid: 7}, level=level)["category"], "BD目标单T7")
                self.assertEqual(first(out, "HELMET", {503: 7, 17: 7}, level=level)["category"], "任意双T7")
                self.assertEqual(first(out, "HELMET", {503: 8}, level=level)["tier"], 1)

    def test_multiple_t7_labels_and_beams_follow_bd_then_tier(self):
        cases = [
            ("ONE_HANDED_AXE", {2: 7, 718: 7}, "双T7含BD目标T7"),
            ("BOOTS", {676: 7, 679: 7}, "双T7含BD目标T7"),
            ("HELMET", {34: 7, 503: 7}, "双T7含BD目标T7"),
            ("HELMET", {406: 7, 503: 7}, "双T7含BD目标T7"),
            ("BELT", {52: 7, 503: 7}, "双T7含BD目标T7"),
            ("HELMET", {503: 7, 17: 7}, "任意双T7"),
            ("HELMET", {34: 7, 503: 7, 17: 7}, "任意至少三T7"),
            ("HELMET", {503: 7, 17: 7, 1: 7, 45: 7}, "任意至少三T7"),
        ]
        for main_id in ("flay-mana-lich", "skeleton-necromancer"):
            config = deepcopy(self.config)
            config["main_id"] = main_id
            out = e.generate(config)
            nodes = parsed(out)
            for typ, affixes, category in cases:
                row = first(out, typ, affixes)
                self.assertEqual(row["category"], category)
                node = nodes[row["number"] - 1]
                owner = "flay-mana-lich" if typ == "ONE_HANDED_AXE" or 34 in affixes else "skeleton-necromancer" if typ == "BOOTS" or 406 in affixes else main_id if 52 in affixes else None
                colors = e.ALERTS[row["tier"]][4:6] if owner is None or row["tier"] >= 3 else ("8", "11") if owner == main_id else ("12", "15")
                self.assertEqual((node.findtext("recolor"), node.findtext("color"), node.findtext("BeamColorOverride")),
                                 ("true", *colors), (main_id, row))
                self.assertEqual(node.findtext("SoundId"), e.ALERTS[row["tier"]][1])
            for aid, role in ((34, "主" if main_id == "flay-mana-lich" else "副"),
                              (406, "主" if main_id == "skeleton-necromancer" else "副")):
                row = first(out, "HELMET", {aid: 7, 503: 8})
                self.assertEqual(row["category"], "BD目标单T7")
                node = nodes[row["number"] - 1]
                self.assertEqual((node.findtext("color"), node.findtext("BeamColorOverride")),
                                 ("8", "11") if role == "主" else ("12", "15"))

    def test_persistent_common_resistance_idols(self):
        out = e.generate(self.leveling_config(()))
        category = "共通抗性神像常驻"
        entries = [(n, r) for n, r in zip(parsed(out), out["rules"]) if r["category"] == category]
        self.assertEqual(len(entries), 1)
        node, row = entries[0]
        pools = {"IDOL_1x2": {111, 112, 113, 117, 885, 886, 887, 888},
                 "IDOL_2x1": {114, 115, 116, 430, 867, 868, 869, 870}}
        self.assertEqual(set(row["affixes"][0]), set.union(*pools.values()))
        self.assertEqual(set(row["types"]), set(pools))
        self.assertFalse(row["bases"])
        self.assertFalse(row["owners"])
        self.assertFalse(any(c.get(e.XSI + "type") == "CharacterLevelCondition" for c in node.find("conditions")))
        self.assertEqual(node.findtext("recolor"), "false")
        self.assertIsNone(row["color"])
        self.assertEqual(node.findtext("emphasized"), e.BASE[129].findtext("emphasized"))
        for typ, pool in pools.items():
            for aid in pool:
                for base in (0, 1):
                    match = first(out, typ, {aid: 1}, base=base, rarity="RARE", corrupted=True)
                    self.assertEqual((match["category"], match["tier"]), (category, 0))
        for level in (0, 59, 79, 80, 100):
            self.assertEqual(first(out, "IDOL_1x2", {117: 1}, level=level, rarity="RARE",
                                   categories={category})["category"], category)
        for typ, affixes in [("IDOL_1x2", {}), ("IDOL_1x2", {139: 1}), ("IDOL_1x2", {1070: 1}),
                             ("IDOL_1x2", {897: 7}), ("IDOL_1x1_ETERRA", {835: 1})]:
            self.assertEqual(first(out, typ, affixes, rarity="RARE")["action"], "HIDE")
        self.assertEqual(first(self.output, "IDOL_1x2", {886: 1}, base=1, rarity="RARE")["tier"], 2)
        self.assertEqual(first(self.output, "IDOL_1x2", {876: 1, 886: 1}, base=1, rarity="RARE")["tier"], 3)

    def test_unique_and_ww_cues(self):
        for uid, lp, tier in [(253,0,1),(253,1,3),(253,2,3),(253,3,4),(0,1,2),(0,2,3),(0,3,4)]:
            self.assertEqual(first(self.output,"BOOTS",{},uid=uid,lp=lp,rarity="UNIQUE")["tier"],tier)
        for ww, tier in [(1,1),(13,1),(14,2),(16,2),(17,3),(19,3),(20,4)]:
            self.assertEqual(first(self.output,"BOOTS",{},uid=253,ww=ww,rarity="UNIQUE")["tier"],tier)
        for ww, tier in [(0,1),(1,1),(13,1),(14,2),(16,2),(17,3),(19,3),(20,4)]:
            row = first(self.output, e.CATALOG["uniques"]["344"]["type"], uid=344, ww=ww, rarity="UNIQUE")
            self.assertEqual(row["tier"], tier, (ww, row))
            if ww < 14:
                self.assertEqual(row["category"], "先驱者之针常驻")

    def test_t0_unique_rule_has_no_lp_roll_or_level_gate(self):
        source = e.read_json("sources/ultra-rare-uniques.json")
        expected = {61, 208, 277, 473, 476, 478}
        self.assertEqual({u["id"] for u in source["uniques"]}, expected)
        for item in source["uniques"]:
            self.assertEqual(item["rarity_tier"], "T0")
            self.assertEqual(item["en"], e.CATALOG["uniques"][str(item["id"])]["en"])
        config = self.leveling_config(())
        before = deepcopy(config)
        out = e.generate(config)
        node, row = next((n, r) for n, r in zip(parsed(out), out["rules"])
                         if r["category"] == "T0极稀有暗金0LP起")
        self.assertEqual(row["number"], 1)
        self.assertEqual((row["tier"], row["role"], row["owners"]), (4, "通用", []))
        self.assertTrue(row["enabled"])
        self.assertEqual(set(row["uniques"]), expected)
        self.assertEqual(len(node.find("conditions")), 1)
        self.assertEqual(next(iter(node.find("conditions"))).get(e.XSI + "type"), "UniqueModifiersCondition")
        self.assertTrue(all(not len(u.find("Rolls")) for u in e.condition(node, "UniqueModifiersCondition")))
        self.assertEqual((node.findtext("SoundId"), node.findtext("MapIconId"), node.findtext("BeamSizeOverride")),
                         e.ALERTS[4][1:4])
        self.assertEqual((node.findtext("color"), node.findtext("BeamColorOverride"), node.findtext("emphasized")),
                         ("7", "10", "true"))
        self.assertEqual(config, before)
        self.assertEqual(e.generate(config, "leveling")["xml"], out["xml"])

    def test_t0_highest_alert_precedes_bd_lp_ww_and_legendary(self):
        output = e.generate(self.leveling_config(()))
        for uid in (61, 208, 277, 473, 476, 478):
            for lp, ww, level in ((0, 0, 1), (1, 13, 84), (2, 14, 85), (3, 20, 100), (4, 30, 100)):
                for rarity in ("UNIQUE", "LEGENDARY"):
                    with self.subTest(uid=uid, lp=lp, ww=ww, level=level, rarity=rarity):
                        row = first(output, e.CATALOG["uniques"][str(uid)]["type"], uid=uid,
                                    lp=lp, ww=ww, level=level, rarity=rarity, corrupted=True)
                        self.assertEqual((row["category"], row["tier"]), ("T0极稀有暗金0LP起", 4))
        for main in ("flay-mana-lich", "skeleton-necromancer"):
            config = deepcopy(self.config)
            config["main_id"] = main
            output = e.generate(config)
            for uid in (277, 208):
                row = first(output, uid=uid, lp=0, rarity="UNIQUE")
                self.assertEqual((row["category"], row["role"], row["tier"]), ("T0极稀有暗金0LP起", "通用", 4))

    def test_common_unique_idols_selection_and_persistent_needle(self):
        config = self.leveling_config(())
        old = deepcopy(config)
        normalized = e.normalize_config(config)
        self.assertEqual(config, old)
        self.assertEqual(normalized["common"], e.default_common())
        out = e.generate(config)
        for uid in e.UNIQUE_IDOLS:
            for level in (1, 84, 85, 100):
                row = first(out, e.CATALOG["uniques"][str(uid)]["type"], uid=uid, level=level, rarity="UNIQUE")
                self.assertEqual(row["category"], "先驱者之针常驻" if uid == 344 else "共通暗金神像")
        for common in ({"unique_idols_enabled": False, "unique_idols": sorted(e.UNIQUE_IDOLS - {344})},
                       {"unique_idols_enabled": True, "unique_idols": []},
                       {"unique_idols_enabled": True, "unique_idols": [211]}):
            config["common"] = common
            out = e.generate(config)
            self.assertEqual(first(out, "IDOL_1x1_ETERRA", uid=344, rarity="UNIQUE")["category"], "先驱者之针常驻")
            for uid in e.UNIQUE_IDOLS - {344}:
                row = first(out, e.CATALOG["uniques"][str(uid)]["type"], uid=uid, rarity="UNIQUE")
                expected = "SHOW" if common["unique_idols_enabled"] and uid in common["unique_idols"] else "HIDE"
                self.assertEqual(row["action"], expected, (uid, common, row))
        config["common"] = {"unique_idols_enabled": True, "unique_idols": [253]}
        with self.assertRaises(ValueError):
            e.normalize_config(config)
        config["common"] = {"unique_idols_enabled": True, "unique_idols": [211]}
        config["builds"][0]["profiles"]["endgame"]["uniques"] = [211]
        out = e.generate(config)
        self.assertFalse(any(r["category"] == "共通暗金神像" for r in out["rules"]))
        self.assertEqual(first(out, "IDOL_2x2", uid=211, rarity="UNIQUE")["category"], "BD暗金0LP也留")
        config["common"]["unique_idols_enabled"] = False
        self.assertEqual(first(e.generate(config), "IDOL_2x2", uid=211, rarity="UNIQUE")["category"], "BD暗金0LP也留")
        config["builds"][0]["profiles"]["endgame"]["uniques"] = [344]
        out = e.generate(config)
        needle = next(r for r in out["rules"] if r["category"] == "先驱者之针常驻")
        self.assertEqual((needle["role"], needle["owners"]), ("主", [config["builds"][0]["name"]]))

    def test_seasonal_uniques_protected_without_build_targets(self):
        out = e.generate(self.leveling_config(()))
        source = e.read_json("sources/seasonal-unique-protection.json")
        self.assertEqual([len(r["uniques"]) for r in source["releases"]], [30, 9, 16])
        self.assertEqual(sum(u["primordial"] for r in source["releases"] for u in r["uniques"]), 25)
        for release in source["releases"]:
            for u in release["uniques"]:
                self.assertEqual(e.CATALOG["uniques"][str(u["id"])]["en"], u["en"])
                row = first(out, u["type"], uid=u["id"], rarity="UNIQUE", lp=0, ww=0)
                expected = "T0极稀有暗金0LP起" if u["id"] in e.ULTRA_RARE_UNIQUES else "共通暗金神像" if u["id"] in e.UNIQUE_IDOLS else "通用套装保护" if e.CATALOG["uniques"][str(u["id"])]["set"] else "通用暗金0LP保护"
                self.assertEqual((row["category"], row["tier"], row["role"]), (expected, 4 if u["id"] in e.ULTRA_RARE_UNIQUES else 1, "通用"))
        for lp, tier in [(1, 2), (2, 3), (3, 4)]:
            self.assertEqual(first(out, "IDOL_2x2", uid=486, rarity="UNIQUE", lp=lp)["tier"], tier)
        self.assertEqual(first(out, uid=0, rarity="UNIQUE")["action"], "HIDE")
        self.assertEqual(first(self.output, uid=475, rarity="UNIQUE")["role"], "主")
        self.assertEqual(first(self.output, uid=471, rarity="UNIQUE")["role"], "副")

    def test_common_protection_split_preserves_membership_and_other_rolls(self):
        common = [(n, r) for n, r in zip(parsed(self.output), self.output["rules"]) if r["category"] in {"通用暗金0LP保护", "通用套装保护"}]
        self.assertEqual(len(common), 2)
        actual = {}
        for node, row in common:
            c = e.condition(node, "UniqueModifiersCondition")
            self.assertEqual(len(node.find("conditions")), 1)
            self.assertTrue(all(e.CATALOG["uniques"][str(uid)]["set"] == (row["category"] == "通用套装保护") for uid in row["uniques"]))
            actual.update({int(u.findtext("UniqueId")): u for u in c})
        original = [u for n in [15, 16] for u in e.condition(e.BASE[n], "UniqueModifiersCondition")]
        bd_ids = {uid for b in self.config["builds"] if b["enabled"] for uid in e.expand_unique_sets(b["profiles"]["endgame"]["uniques"])}
        expected = ({int(u.findtext("UniqueId")) for u in original} | e.SEASONAL_UNIQUES) - e.UNIQUE_IDOLS - e.ULTRA_RARE_UNIQUES - bd_ids
        self.assertEqual(set(actual), expected)
        self.assertEqual(sum(len(row["uniques"]) for _, row in common), len(expected))
        for uid in e.SEASONAL_UNIQUES - e.UNIQUE_IDOLS - e.ULTRA_RARE_UNIQUES - bd_ids:
            self.assertFalse(len(actual[uid].find("Rolls")))
        for u in original:
            uid = int(u.findtext("UniqueId"))
            if uid not in e.SEASONAL_UNIQUES | e.UNIQUE_IDOLS | e.ULTRA_RARE_UNIQUES | bd_ids:
                self.assertEqual(tree(actual[uid]), tree(u))
        self.assertFalse(any(r["category"] == "Raxx通用" and r["source_raxx_rule"] in range(12, 17) for r in self.output["rules"]))
        self.assertFalse(any(r["category"] == "珍贵名单低WW静音" for r in self.output["rules"]))

    def test_one_set_piece_collects_all_members_without_rewriting_saved_targets(self):
        config = self.leveling_config(())
        config["builds"][0]["profiles"]["endgame"]["uniques"] = [77]
        before = deepcopy(config)
        out = e.generate(config)
        targets = next(r for r in out["rules"] if r["category"] == "BD暗金0LP也留")
        self.assertEqual(set(targets["uniques"]), {77, 78, 79})
        for uid in (77, 78, 79):
            self.assertEqual(first(out, e.CATALOG["uniques"][str(uid)]["type"], uid=uid, rarity="SET",
                                   categories={"BD暗金0LP也留"})["role"], "主")
        self.assertEqual(first(out, uid=85, rarity="SET", categories={"BD暗金0LP也留"})["action"], "HIDE")
        self.assertEqual(config, before)

    def test_set_completion_respects_enabled_builds_and_shared_main_ownership(self):
        config = self.leveling_config(())
        main = config["builds"][0]
        main["profiles"]["endgame"]["uniques"] = [77]
        other = deepcopy(main); other["id"] = "b"; other["name"] = "B"
        other["profiles"]["endgame"]["uniques"] = [78, 171]
        config["builds"].append(other)
        out = e.generate(config)
        rows = {r["role"]: set(r["uniques"]) for r in out["rules"] if r["category"] == "BD暗金0LP也留"}
        self.assertEqual(rows, {"主": {77, 78, 79}, "副": {170, 171}})
        other["enabled"] = False
        rows = [r for r in e.generate(config)["rules"] if r["category"] == "BD暗金0LP也留"]
        self.assertEqual(len(rows), 1); self.assertEqual(set(rows[0]["uniques"]), {77, 78, 79})

    def test_all_frozen_sets_expand_and_common_rules_have_one_unique_condition(self):
        groups = e.ITEM_SETS.values()
        self.assertEqual(len(e.ITEM_SETS), 24)
        self.assertEqual({uid for g in groups for uid in g["members"]},
                         {int(uid) for uid, u in e.CATALOG["uniques"].items() if u["set"]})
        for group in e.ITEM_SETS.values():
            for uid in group["members"]:
                self.assertEqual(e.expand_unique_sets([uid]), sorted(group["members"]))
        config = self.leveling_config(())
        output = e.generate(config)
        for node, row in zip(parsed(output), output["rules"]):
            if row["category"] in {"通用暗金0LP保护", "通用套装保护", "共通暗金神像", "先驱者之针常驻"}:
                conditions = list(node.find("conditions"))
                self.assertEqual(len(conditions), 1)
                self.assertEqual(conditions[0].get(e.XSI + "type"), "UniqueModifiersCondition")
                self.assertTrue(row["enabled"])

    def test_selection_main_and_phase(self):
        config=deepcopy(self.config)
        config["main_id"]="skeleton-necromancer"
        out=e.generate(config)
        self.assertEqual(first(out,"BOOTS",{},uid=253,rarity="UNIQUE")["role"],"主")
        for b in config["builds"]:
            if b["id"]=="flay-mana-lich":b["enabled"]=False
        out=e.generate(config)
        self.assertFalse(any("Flay Mana Lich" in r["owners"] for r in out["rules"]))
        config["extra_t7"]=False
        out=e.generate(config)
        self.assertEqual(first(out,"HELMET",{1156:7})["action"],"HIDE")
        self.assertEqual(first(out,"HELMET",{406:7})["tier"],2)

    def leveling_config(self, targets=(26, 945, 98, 643, 502, 45, 28, 27)):
        return {"version": 1, "main_id": "a", "extra_t7": False, "builds": [
            {"id": "a", "name": "A", "enabled": True, "profiles": {
                "endgame": e.empty_profile(), "leveling": {"affixes": list(targets), "bases": []}}}]}

    def test_leveling_scores_and_exit(self):
        config = self.leveling_config()
        out = e.generate(config)
        cases = [(29, {502: 1}, True), (30, {502: 2, 45: 2}, False),
                 (30, {502: 3, 45: 2}, True), (49, {502: 3, 45: 2}, True),
                 (50, {502: 3, 45: 2}, False), (60, {502: 5, 45: 3}, True),
                 (60, {502: 5}, False), (79, {502: 5, 45: 3}, True), (80, {502: 5, 45: 3}, False)]
        scoring = {r["category"] for r in out["rules"] if r["category"].startswith("练级") and "底材" not in r["category"] and "拆解" not in r["category"]}
        for level, affixes, shown in cases:
            row = first(out, "HELMET", affixes, level=level, rarity="RARE", categories=scoring)
            self.assertEqual(row["action"] != "HIDE", shown, (level, affixes, row))
        self.assertEqual(first(out, "HELMET", {502: 3, 45: 2}, level=60, rarity="RARE")["action"], "HIDE")
        self.assertFalse(any("T6" in r["category"] for r in out["rules"]))
        self.assertEqual(out["xml"], e.generate(config, "leveling")["xml"])
        self.assertEqual(self.config["builds"][0]["profiles"]["leveling"], e.empty_leveling())
        self.assertEqual(first(self.output, "HELMET", {34: 7}, level=20)["category"], "BD目标单T7")

    def test_leveling_single_eligible_target(self):
        config = self.leveling_config((28, 502))
        out = e.generate(config)
        scoring = {r["category"] for r in out["rules"] if r["category"].startswith("练级50")}
        for tier, shown in [(4, False), (5, True), (6, True)]:
            self.assertEqual(first(out, "HELMET", {502: tier}, level=60, rarity="RARE", categories=scoring)["action"] != "HIDE", shown)
        # Boots can roll both targets: one T5 must not use the single-target exception.
        self.assertEqual(first(out, "BOOTS", {28: 5}, level=60, rarity="RARE", categories=scoring)["action"], "HIDE")

    def test_leveling_primary_first_and_highest_band_within_each_bd(self):
        config = self.leveling_config((502, 28))
        other = deepcopy(config["builds"][0]); other["id"] = "b"; other["name"] = "B"
        other["profiles"]["leveling"]["affixes"] = [45, 27]
        config["builds"].append(other)
        out = e.generate(config)
        bands = []
        for node, row in zip(parsed(out), out["rules"]):
            if row["source_raxx_rule"] == 63:
                c = e.condition(node, "CharacterLevelCondition")
                bands.append((int(c.findtext("minimumLvl")), int(c.findtext("maximumLvl")), row["role"]))
        self.assertEqual(bands, [(50, 79, "主"), (50, 79, "主"), (30, 49, "主"), (0, 29, "主"),
                                 (50, 79, "副"), (50, 79, "副"), (30, 49, "副"), (0, 29, "副")])

    def test_leveling_bases_and_early_fallback(self):
        config = self.leveling_config()
        config["builds"][0]["profiles"]["leveling"]["bases"] = [{"type": "RING", "bases": [7]}]
        config["builds"][0]["profiles"]["leveling"]["bases"] += [{"type": "RELIC", "bases": [15]}, {"type": "RELIC", "bases": [18]}]
        out = e.generate(config)
        relic_layers = [r for r in out["rules"] if r["category"].startswith("练级底材") and r["types"] == ["RELIC"]]
        self.assertEqual(len(relic_layers), 2)
        self.assertTrue(all(r["bases"] == [15, 18] for r in relic_layers))
        base_layers = {r["category"] for r in out["rules"] if r["category"].startswith("练级底材")}
        for level, affixes, shown in [(29, {}, True), (30, {}, False), (30, {26: 1}, True),
                                      (59, {26: 1}, True), (60, {26: 1}, False), (40, {503: 1}, False)]:
            self.assertEqual(first(out, "RING", affixes, base=7, level=level, rarity="MAGIC", categories=base_layers)["action"] != "HIDE", shown)
        self.assertEqual(first(out, "HELMET", {}, level=9, rarity="RARE")["action"], "SHOW")
        self.assertEqual(first(out, "HELMET", {}, level=10, rarity="RARE")["action"], "HIDE")
        self.assertEqual(first(out, "RELIC", {}, base=0, level=10, rarity="NORMAL")["action"], "HIDE")
        self.assertEqual(first(out, "HELMET", {503: 1}, level=30, rarity="UNIQUE")["action"], "SHOW")
        self.assertEqual(first(out, "HELMET", {503: 6}, level=59)["action"], "SHOW")
        self.assertEqual(first(out, "HELMET", {503: 6}, level=60)["action"], "HIDE")

    def test_no_cross_build_leveling_score_or_base_match(self):
        config = self.leveling_config((502, 28))
        other = deepcopy(config["builds"][0]);other["id"] = "b";other["name"] = "B"
        other["profiles"]["leveling"] = {"affixes": [45, 27], "bases": []}
        config["builds"].append(other)
        out = e.generate(config)
        scoring = {r["category"] for r in out["rules"] if r["category"].startswith("练级50")}
        self.assertEqual(first(out, "BOOTS", {502: 4, 45: 4}, level=60, rarity="RARE", categories=scoring)["action"], "HIDE")
        self.assertNotEqual(first(out, "BOOTS", {502: 4, 28: 4}, level=60, rarity="RARE", categories=scoring)["action"], "HIDE")
        config["builds"][0]["profiles"]["leveling"]["bases"] = [{"type": "BOOTS", "bases": [11]}]
        out = e.generate(config)
        self.assertEqual(first(out, "BOOTS", {45: 1}, base=11, level=40, rarity="MAGIC", categories={"练级底材＋目标：30–59级"})["action"], "HIDE")

    def test_endgame_05_requires_own_target_t7_forever(self):
        config = self.leveling_config(())
        p = config["builds"][0]["profiles"]["endgame"]
        # A restricted C1 scope leaves the separately requested 05 bases active.
        p["equipment"] = [{"type": "BOOTS", "bases": [0], "affixes": [28]}]
        p["bases"] = [{"type": "BOOTS", "preferred_bases": [11], "bases": [9]}, {"type": "BOOTS", "bases": [10]}]
        other = deepcopy(config["builds"][0]);other["id"] = "b";other["name"] = "B"
        other["profiles"]["endgame"]["equipment"][0]["affixes"] = [45]
        other["profiles"]["endgame"]["bases"] = []
        config["builds"].append(other)
        out = e.generate(config)
        layers = [r for r in out["rules"] if r["category"].startswith("终局05")]
        self.assertEqual([(r["category"], r["bases"]) for r in layers],
                         [("终局05首选底材＋BD目标T7", [11]), ("终局05替代底材＋BD目标T7", [9, 10])])
        categories = {r["category"] for r in layers}
        for affixes, base, shown in [({}, 11, False), ({503: 7}, 11, False), ({45: 7}, 11, False),
                                     ({28: 6}, 11, False), ({28: 8}, 11, False), ({28: 7}, 0, False),
                                     ({28: 7}, 11, True), ({28: 7}, 9, True), ({28: 7}, 10, True),
                                     ({45: 7}, 9, False), ({503: 7}, 10, False)]:
            self.assertEqual(first(out, "BOOTS", affixes, base=base, level=100, categories=categories)["action"] != "HIDE", shown)
        self.assertEqual(first(out, "BOOTS", {}, base=11, level=100, rarity="NORMAL")["action"], "HIDE")
        p["equipment"] = []
        self.assertTrue(e.generate(config)["warnings"])

    def test_salvage_and_generic_idol_boundaries(self):
        out = e.generate(self.leveling_config((502, 945)))
        for node, row in zip(parsed(out), out["rules"]):
            if 84 <= row["source_raxx_rule"] <= 90:
                self.assertEqual(e.condition(node, "CharacterLevelCondition").findtext("maximumLvl"), "59")
        for level, shown in [(49, True), (50, False)]:
            self.assertEqual(first(out, "HELMET", {502: 3}, level=level, rarity="RARE", categories={"练级拆解：目标T≥3，50级退出"})["action"] != "HIDE", shown)
        # BD targets keep the BD color rather than falling into a broad original salvage rule.
        row = first(out, "GLOVES", {945: 4}, level=40, rarity="RARE")
        self.assertEqual(row["category"], "练级拆解：目标T≥3，50级退出")
        self.assertEqual(row["role"], "主")
        generic = [r for r in self.output["rules"] if r["source_raxx_rule"] in {128, 129, 135}]
        for row in generic:
            self.assertNotIn(941, row["affixes"][0])
            self.assertTrue(all(e.CATALOG["affixes"][str(i)]["special"] in {0, 5} for i in row["affixes"][0]))
        for level, shown in [(74, True), (75, False)]:
            self.assertEqual(first(self.output, "IDOL_1x1_LAGON", {107: 1}, base=0, level=level, rarity="RARE", categories={"Raxx通用"})["action"] != "HIDE", shown)

    def test_manual_rule_assignment_and_invalid_input(self):
        node=deepcopy(e.BASE[40]);node.find("nameOverride").text="My custom chest targets"
        root=ET.Element("ItemFilter");ET.SubElement(root,"name").text="Custom";ET.SubElement(root,"rules").append(node)
        xml=ET.tostring(root,encoding="unicode")
        self.assertFalse(e.extract(xml)["profile"]["equipment"])
        self.assertTrue(e.extract(xml,{"1":"equipment"})["profile"]["equipment"])
        node = deepcopy(e.BASE[89]);node.find("nameOverride").text = "Custom flat targets"
        root.find("rules")[:] = [node]
        flat = e.extract(ET.tostring(root, encoding="unicode"), {"1": "equipment"})
        self.assertFalse(flat["profile"]["equipment"])
        self.assertEqual(set(flat["leveling_profile"]["affixes"]), ids(e.condition(node, "AffixCondition"), "affixes/int"))
        with self.assertRaises(ValueError):e.extract('<!DOCTYPE ItemFilter><ItemFilter/>')
        node=deepcopy(e.BASE[99]);node.find("nameOverride").text="1 Affix - Test Idol";node.find("isEnabled").text="true"
        e.set_affix(node,[843,999999])
        root.find("rules")[:]=[node]
        unknown=e.extract(ET.tostring(root,encoding="unicode"))
        self.assertEqual(unknown["profile"]["unresolved_affixes"],[999999])
        with self.assertRaisesRegex(ValueError,'未识别'):e.validate_profile(unknown["profile"])
        config=deepcopy(self.config);config["builds"][0]["profiles"]["endgame"]["idols"][0]["affixes"].append(897)
        with self.assertRaises(ValueError):e.generate(config)
        large=deepcopy(self.config)
        original=large["builds"][0]
        for i in range(80):
            b=deepcopy(original);b["id"]=f"extra{i}";b["name"]=f"Extra{i}";b["profiles"]["endgame"]["equipment"][0]["affixes"]=[i,i+1];large["builds"].append(b)
        with self.assertRaisesRegex(ValueError,'超过200'):e.generate(large)


if __name__ == "__main__":
    unittest.main()
