"""Bounded source, XML and policy tests. Does not emulate the game client."""
import hashlib
import unittest
import xml.etree.ElementTree as ET
from copy import deepcopy

import engine as e
from verify_generated_filter import ids, predicate, structure


def parsed(output):
    return sorted(ET.fromstring(output["xml"]).find("rules"), key=lambda r: int(r.findtext("Order")))


def first(output, typ="HELMET", affixes=None, **extra):
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

    def test_independent_leveling_and_original_gates(self):
        config=deepcopy(self.config)
        p=next(b for b in config["builds"] if b["id"]==config["main_id"])["profiles"]["leveling"]
        p["leveling_slots"]["154"]={"enabled":True,"types":["WAND"],"bases":[],"affixes":[38]}
        out=e.generate(config,"leveling")
        row=next(r for r in out["rules"] if r["category"]=="练级独立目标")
        rule=parsed(out)[row["number"]-1]
        for kind in ["CharacterLevelCondition", "AffixCondition"]:
            before,after=deepcopy(e.condition(e.BASE[154],kind)),deepcopy(e.condition(rule,kind))
            if kind=="AffixCondition":before.find("affixes").clear();after.find("affixes").clear()
            self.assertEqual(structure(before),structure(after))
        self.assertEqual(first(out,"WAND",{38:1},level=29,rarity="MAGIC")["category"],"练级独立目标")
        self.assertNotEqual(first(out,"WAND",{38:1},level=30,rarity="MAGIC")["category"],"练级独立目标")
        self.assertEqual(self.config["builds"][0]["profiles"]["leveling"]["equipment"],[])

    def test_manual_rule_assignment_and_invalid_input(self):
        node=deepcopy(e.BASE[40]);node.find("nameOverride").text="My custom chest targets"
        root=ET.Element("ItemFilter");ET.SubElement(root,"name").text="Custom";ET.SubElement(root,"rules").append(node)
        xml=ET.tostring(root,encoding="unicode")
        self.assertFalse(e.extract(xml)["profile"]["equipment"])
        self.assertTrue(e.extract(xml,{"1":"equipment"})["profile"]["equipment"])
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
        for i in range(12):
            b=deepcopy(original);b["id"]=f"extra{i}";b["name"]=f"Extra{i}";b["profiles"]["endgame"]["equipment"][0]["affixes"]=[i];large["builds"].append(b)
        with self.assertRaisesRegex(ValueError,'超过200'):e.generate(large)


if __name__ == "__main__":
    unittest.main()
