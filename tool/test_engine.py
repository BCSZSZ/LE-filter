"""Bounded source, XML and policy tests. Does not emulate the game client."""
import hashlib
import unittest
import xml.etree.ElementTree as ET
from copy import deepcopy

import engine as e
from verify_generated_filter import ids, predicate


def parsed(output):
    return sorted(ET.fromstring(output["xml"]).find("rules"), key=lambda r: int(r.findtext("Order")))


def first(output, typ="HELMET", affixes=None, categories=None, **extra):
    item = {"type": typ, "base": 0, "affixes": affixes or {}, "level": 100, "rarity": "EXALTED",
            "corrupted": False, "fp": 0, "uid": -1, "lp": 0, "ww": 0, **extra}
    def matches(c):
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
            ("HELMET", {503:7, 1:7, 17:7}, 4, "任意至少三T7"),
            ("HELMET", {503:7, 1:7}, 2, "任意双T7"),
            ("HELMET", {34:7, 503:7}, 3, "双T7含BD目标"),
            ("BOOTS", {676:7, 679:7}, 3, "BD双目标T7"),
            ("HELMET", {34:7}, 2, "BD目标单T7"),
            ("HELMET", {34:4, 503:7}, 1, "非目标T7＋BD目标"),
            ("HELMET", {1156:7}, 0, "Raxx通用"),
            ("HELMET", {503:8}, 1, "Raxx通用"),
            ("HELMET", {503:8, 34:7}, 2, "BD目标单T7"),
            ("HELMET", {503:8, 1:7, 17:7}, 2, "任意双T7"),
            ("HELMET", {718:7}, 0, "Raxx通用")]
        for typ, affixes, tier, category in cases:
            row = first(self.output, typ, affixes)
            self.assertEqual((row["tier"], row["category"]), (tier, category), (typ, affixes, row))
        boots = [r for r in self.output["rules"] if r["category"] == "BD双目标T7" and r["types"] == ["BOOTS"] and r["role"] == "副"]
        self.assertEqual(len(boots), 1)
        self.assertEqual(set(boots[0]["affixes"][0]), {28,676,679})

    def test_idol_normal_count(self):
        for affixes, tier in [({941:1,287:1},3), ({941:1,897:7},2), ({941:1,1071:1},2),
                              ({941:1,287:1,897:7,1071:1},3)]:
            row = first(self.output, "IDOL_1x3", affixes, base=8, rarity="RARE", corrupted=True)
            self.assertEqual(row["tier"], tier)
            self.assertTrue(row["category"].startswith("神像"))
        self.assertEqual(first(self.output,"IDOL_2x1",{862:1},base=1,rarity="RARE")["tier"],2)

    def test_unique_and_ww_cues(self):
        for uid, lp, tier in [(253,0,1),(253,1,3),(253,2,3),(253,3,4),(0,1,2),(0,2,3),(0,3,4)]:
            self.assertEqual(first(self.output,"BOOTS",{},uid=uid,lp=lp,rarity="UNIQUE")["tier"],tier)
        for ww, tier in [(1,1),(13,1),(14,2),(16,2),(17,3),(19,3),(20,4)]:
            self.assertEqual(first(self.output,"BOOTS",{},uid=253,ww=ww,rarity="UNIQUE")["tier"],tier)

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
        p["equipment"] = [{"type": "BOOTS", "bases": [], "affixes": [28]}]
        p["bases"] = [{"type": "BOOTS", "bases": [11]}]
        other = deepcopy(config["builds"][0]);other["id"] = "b";other["name"] = "B"
        other["profiles"]["endgame"]["equipment"][0]["affixes"] = [45]
        other["profiles"]["endgame"]["bases"] = []
        config["builds"].append(other)
        out = e.generate(config)
        for affixes, base, shown in [({}, 11, False), ({503: 7}, 11, False), ({45: 7}, 11, False),
                                     ({28: 6}, 11, False), ({28: 8}, 11, False), ({28: 7}, 0, False), ({28: 7}, 11, True)]:
            self.assertEqual(first(out, "BOOTS", affixes, base=base, level=100, categories={"终局05底材＋BD目标T7"})["action"] != "HIDE", shown)
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
        for i in range(20):
            b=deepcopy(original);b["id"]=f"extra{i}";b["name"]=f"Extra{i}";b["profiles"]["endgame"]["equipment"][0]["affixes"]=[i,i+1];large["builds"].append(b)
        with self.assertRaisesRegex(ValueError,'超过200'):e.generate(large)


if __name__ == "__main__":
    unittest.main()
