"""Fill the frozen Raxx template from the two supplied Maxroll Strict exports."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
ET.register_namespace("i", XSI[1:-1])
BUILD_NAMES = {"flay-mana-lich": "FLAY", "skeleton-necromancer": "NECRO"}
COLORS = {"FLAY": 8, "NECRO": 12, "SHARED": 15}
T7_SLOTS = {"ONE_HANDED_AXE": 38, "TWO_HANDED_AXE": 38,
            "ONE_HANDED_DAGGER": 39, "HELMET": 40, "BODY_ARMOR": 41,
            "BELT": 42, "BOOTS": 43, "GLOVES": 44, "AMULET": 45,
            "RING": 46, "RELIC": 47}
OUTPUT = "filters/Flay-Mana-Lich+Skeleton-Necromancer.xml"


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def frozen(source):
    path = source.get("file", source.get("local_path"))
    raw = (ROOT / path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source["sha256"], path
    return ET.fromstring(raw) if path.endswith(("xml", "txt")) else json.loads(raw)


def condition(rule, kind):
    return next(c for c in rule.find("conditions") if c.get(XSI + "type") == kind)


def ints(node, path):
    return [int(e.text) for e in node.findall(path)]


def replace_ints(node, path, values):
    target = node.find(path)
    target.clear()
    for value in sorted(set(values)):
        ET.SubElement(target, "int").text = str(value)


def tree(node):
    # AND conditions and selection lists commute; retain repeated objects and nil.
    return (node.tag, sorted(node.attrib.items()), (node.text or "").strip(),
            sorted((tree(c) for c in node), key=repr))


def signature(rule):
    return repr(tree(rule.find("conditions")))


def generate():
    manifest = read_json("sources/manifest.json")
    strict_manifest = read_json("sources/builds/maxroll-strict-manifest.json")
    build_manifest = read_json("sources/builds/manifest.json")
    guide = read_json("sources/builds/flay-mana-lich-guide.json")["guide_facts"]
    reference = read_json("sources/builds/transfer-reference.json")
    equipment_enum = read_json("sources/game-reference.json")["equipment_enum"]
    root = frozen(manifest["baseline"])
    base = {int(r.findtext("Order")) + 1: r for r in root.find("rules")}
    source_rules, builds, source_report = {}, {}, []
    additions = defaultdict(list)
    report = {"game_execution_tested": False, "output": OUTPUT,
              "rule_limit": 200, "baseline_source": manifest["baseline"],
              "sources": {}, "baseline": [], "strict": source_report,
              "supplements": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in ["sources/builds/flay-mana-lich-guide.json", "sources/builds/transfer-reference.json"]}}

    def add(slot, source, owners, name, category, refs=(), loud=False):
        r = deepcopy(base[slot])
        r.find("conditions").clear()
        r.find("conditions").extend(deepcopy(list(source.find("conditions"))))
        row = {"template": slot, "category": category, "owners": sorted(owners),
               "source_rules": list(refs), "label": name}
        additions[slot].append((r, row, loud))
        return r

    for slug, label in BUILD_NAMES.items():
        spec = strict_manifest["inputs"][slug]
        source_rules[slug] = list(frozen(spec).find("rules"))
        builds[slug] = frozen(build_manifest["inputs"][slug])
        report["sources"][slug] = {"strict": spec, "planner": build_manifest["inputs"][slug]}
        for pos, r in enumerate(source_rules[slug], 1):
            name = r.findtext("nameOverride") or ""
            row = {"build": slug, "xml_position": pos, "name": name,
                   "disposition": "disabled_in_source" if r.findtext("isEnabled") == "false"
                   else "replaced_by_raxx_general_policy", "output_numbers": []}
            source_report.append(row)
            if r.findtext("isEnabled") != "true":
                continue
            slot, category = None, None
            if re.fullmatch(r"Tier [67] - (?!Class Specific Affixes).+", name):
                t = condition(r, "SubTypeCondition").findtext("type/EquipmentType")
                a = condition(r, "AffixCondition")
                assert a.findtext("minOnTheSameItem") == "1" and a.findtext("advanced") == "true"
                assert a.findtext("combinedComparsion") == "ANY"
                assert a.findtext("comparsionValue") == name[5]
                slot = T7_SLOTS[t] if name[5] == "7" else (63 if t in T7_SLOTS and T7_SLOTS[t] < 40 else 64)
                category = "tier" + name[5]
            elif name == "Tier 7 - Class Specific Affixes":
                slot, category = 61, "class_t7"
            elif "(Rune of Havoc)" in name or name in {"Tier 7 Highly Craftable Items (52+ FP)", "Tier 7 Eternal Gauntlets"}:
                slot, category = 62, "crafting"
            elif name == "Wanted Experimental Affixes":
                slot, category = 69, "experimental"
            elif name.startswith("Rare Strict "):
                slot, category = 82, "rare_base"
            elif name == "Shatter / Removal (Edit Affixes)":
                slot, category = 83, "shatter"
            elif name == "Shatter / Removal (Class Specific Affixes)":
                slot, category = 84, "class_shatter"
            elif name.startswith("Shatter / Removal - Increased Health"):
                slot, category = 90, "health_shatter"
            elif name.startswith("Strict - ") and name != "Strict - Weaver Idols":
                slot, category = 99, "idol_strict"
            elif name.startswith("1 Affix - "):
                slot, category = 128, "idol_one_affix"
            elif name in {"Strict - Weaver Idols", "Reflect Idols (Alt Leveling)"}:
                slot, category = 129, "idol_generic"
            elif name == "Unique Idols":
                slot, category = 16, "unique_idols"
            elif "Altar" in name:
                slot, category = 127, "altar"
            if slot:
                add(slot, r, {label}, name, category, [(slug, pos)], category in {"tier7", "idol_strict", "altar"})
                row["disposition"] = "mapped_conditions"
            elif "From Planner" in name:
                row["disposition"] = "planner_whitelist_rebuilt"

    # Split only count-one / combined-ANY tier predicates: intersection + per-BD remainder.
    for slot in range(38, 65):
        grouped = defaultdict(list)
        for entry in additions[slot]:
            r, row, _ = entry
            key_rule = deepcopy(r)
            if row["category"] in {"tier6", "tier7"}:
                replace_ints(condition(key_rule, "AffixCondition"), "affixes", [])
            grouped[(row["category"], signature(key_rule))].append(entry)
        additions[slot] = []
        for (category, _), entries in grouped.items():
            if category in {"tier6", "tier7"} and len(entries) == 2:
                common = set(ints(condition(entries[0][0], "AffixCondition"), "affixes/int")) & set(ints(condition(entries[1][0], "AffixCondition"), "affixes/int"))
                if common:
                    r, row, loud = deepcopy(entries[0])
                    replace_ints(condition(r, "AffixCondition"), "affixes", common)
                    row["owners"] = ["FLAY", "NECRO"]
                    row["source_rules"] = entries[0][1]["source_rules"] + entries[1][1]["source_rules"]
                    additions[slot].append((r, row, loud))
                    for r, _, _ in entries:
                        replace_ints(condition(r, "AffixCondition"), "affixes", set(ints(condition(r, "AffixCondition"), "affixes/int")) - common)
            additions[slot].extend(e for e in entries if category not in {"tier6", "tier7"} or ints(condition(e[0], "AffixCondition"), "affixes/int"))

    pools = {}
    for slug, label in BUILD_NAMES.items():
        rules = source_rules[slug]
        selected = next(r for r in rules if r.findtext("nameOverride") == "Uniques & Sets From Planner (Optional: Add More)")
        pools[label] = set(ints(condition(selected, "UniqueModifiersCondition"), "Uniques/UniqueId"))
        if label == "FLAY":
            pools[label].update(guide["additional_collection_unique_ids"])
        for idol in {json.dumps(i, sort_keys=True): i for i in builds[slug]["idols"] if i}.values():
            ids = sorted(a["id"] for a in idol["affixes"])
            key = (idol["itemType"], idol["subType"], tuple(ids))
            if any(e[1].get("idol_key") == list(key[:2]) + [ids] for e in additions[99]):
                continue
            r = add(99, selected, {label}, "Planner idol combination", "idol_pair", loud=True)
            r.find("conditions").clear()
            t = deepcopy(condition(next(r for r in rules if r.findtext("nameOverride") == "1 Affix - Minor Idols"), "SubTypeCondition"))
            t.find("type").clear()
            enum = next(k for k, v in equipment_enum.items() if v == idol["itemType"])
            ET.SubElement(t.find("type"), "EquipmentType").text = enum
            replace_ints(t, "subTypes", [idol["subType"]])
            a = deepcopy(condition(next(r for r in rules if r.findtext("nameOverride") == "1 Affix - Minor Idols"), "AffixCondition"))
            replace_ints(a, "affixes", ids)
            a.find("minOnTheSameItem").text = str(len(ids))
            r.find("conditions").extend([t, a])
            additions[99][-1][1]["idol_key"] = list(key[:2]) + [ids]
        for pos, src in enumerate(rules, 1):
            name = src.findtext("nameOverride") or ""
            if re.fullmatch(r"Tier 6 - .+", name):
                ids = [i for i in ints(condition(src, "AffixCondition"), "affixes/int") if reference["special_affix_type"][str(i)] == 6]
                if ids:
                    r = add(75, src, {label}, "Wanted corrupted affix (any tier)", "corrupted_supplement", [(slug, pos)])
                    a = condition(r, "AffixCondition")
                    replace_ints(a, "affixes", ids)
                    a.find("advanced").text = "false"
                    condition(r, "CorruptionCondition").find("Corruption").text = "OnlyCorrupted"

    # Core uniques: preserve each Strict potential layer, then a zero-LP-safe whitelist.
    report["target_unique_ids"] = {label: sorted(ids) for label, ids in pools.items()}
    common = pools["FLAY"] & pools["NECRO"]
    for owner, ids in [("SHARED", common), ("FLAY", pools["FLAY"] - common), ("NECRO", pools["NECRO"] - common)]:
        slug = "skeleton-necromancer" if owner == "NECRO" else "flay-mana-lich"
        candidates = [(pos, r) for pos, r in enumerate(source_rules[slug], 1) if "From Planner" in (r.findtext("nameOverride") or "")]
        selected = next(r for _, r in candidates if r.findtext("nameOverride") == "Uniques & Sets From Planner (Optional: Add More)")
        layers = [next((pos, r) for pos, r in candidates if f"{level} LP" in r.findtext("nameOverride")) for level in [3, 2, 1]]
        layers.append(next((pos, r) for pos, r in candidates if r is selected))
        for pos, src in layers:
            refs = [(slug, pos)]
            if owner == "SHARED":
                refs += [(other, p) for other in BUILD_NAMES if other != slug for p, candidate in enumerate(source_rules[other], 1) if candidate.findtext("nameOverride") == src.findtext("nameOverride")]
            r = add(8, src, {owner} if owner != "SHARED" else {"FLAY", "NECRO"}, "Build uniques: " + src.findtext("nameOverride").split(" (", 1)[0], "build_unique", refs, src is not selected)
            c = condition(r, "UniqueModifiersCondition")
            template = deepcopy(c.find("Uniques"))
            shapes = []
            for u in c.findall("Uniques"):
                u = deepcopy(u)
                u.find("UniqueId").text = "0"
                shapes.append(repr(tree(u)))
            assert len(set(shapes)) == 1, "Review item-specific unique roll bounds before rebuilding the whitelist"
            for e in list(c):
                c.remove(e)
            for uid in sorted(ids):
                u = deepcopy(template)
                u.find("UniqueId").text = str(uid)
                c.append(u)

    # Guide-confirmed Frailty fallback and optional armor altar / corruption idol.
    flay_pair = next(e for e in additions[99] if e[1].get("idol_key", [])[:2] == [28, 1])
    r = add(99, flay_pair[0], {"FLAY"}, "Ignite + Frailty fallback", "guide_idol", loud=True)
    replace_ints(condition(r, "AffixCondition"), "affixes", [876, 891])
    r = add(128, flay_pair[0], {"FLAY"}, "Optional critical avoidance corruption", "guide_idol")
    t = condition(r, "SubTypeCondition")
    t.find("type/EquipmentType").text = "IDOL_1x1_LAGON"
    a = condition(r, "AffixCondition")
    replace_ints(a, "affixes", [1067])
    a.find("minOnTheSameItem").text = "1"
    r = add(127, base[127], {"FLAY"}, "Guide armor altar base (inspect manually)", "guide_altar")
    t = condition(r, "SubTypeCondition")
    replace_ints(t, "subTypes", [4])
    for c in list(r.find("conditions")):
        if c is not t:
            r.find("conditions").remove(c)

    # Preserve global Raxx policy; resolve unused personal templates explicitly.
    disabled = {29: "Class hide not requested", 60: "T7 weapon pools mapped above",
                70: "Champion affixes not requested", 81: "Ascend target not requested",
                85: "Mage shards not requested", 86: "Primalist shards not requested",
                87: "Rogue shards not requested", 88: "Sentinel shards not requested",
                89: "Extra offensive shard inventory not supplied",
                136: "Campaign weapon bases not supplied", 137: "Campaign offhand bases not supplied",
                152: "Bow not used", 154: "Wand/staff not used", 157: "Catalyst not used",
                158: "Quiver not used", 159: "Shield not used"}
    types = sorted(T7_SLOTS)
    all_ids = sorted({int(e.text) for rules in source_rules.values() for r in rules for c in r.find("conditions") if c.get(XSI + "type") == "AffixCondition" for e in c.findall("affixes/int")})
    for n in [37, 48]:
        replace_ints(condition(base[n], "AffixCondition"), "affixes", all_ids)
    for n in [48, 60, 153]:
        t = condition(base[n], "SubTypeCondition")
        t.find("type").clear()
        for name in (types if n == 48 else ["ONE_HANDED_AXE", "ONE_HANDED_DAGGER", "TWO_HANDED_AXE"]):
            ET.SubElement(t.find("type"), "EquipmentType").text = name
    experiment = next(r for r in source_rules["skeleton-necromancer"] if r.findtext("nameOverride") == "Wanted Experimental Affixes")
    replace_ints(condition(base[68], "AffixCondition"), "affixes", ints(condition(experiment, "AffixCondition"), "affixes/int"))
    base[68].find("nameOverride").text = "NECRO - Exalted items with wanted experimentals"
    base[68].find("recolor").text = "true"
    base[68].find("color").text = "12"
    for n in [15, 16, 48]:
        base[n].find("nameOverride").text = {15: "Raxx rare unique protection", 16: "Raxx selected sets", 48: "Double exalts on either build's equipment types"}[n]
    for n, reason in disabled.items():
        base[n].find("isEnabled").text = "false"
        base[n].find("nameOverride").text = "OFF - " + reason

    output, output_rows = [], []
    for n in range(1, 164):
        original = base[n]
        blue = original.findtext("color") == "12" and original.findtext("isEnabled") == "false" and n not in disabled
        disposition = "player_instruction_removed" if blue else "replaced" if additions[n] or 100 <= n <= 126 else "disabled_explicitly" if n in disabled else "retained"
        if n in {8, 16}:
            disposition = "augmented"
        elif n in {15, 37, 48, 68, 153}:
            disposition = "configured"
        report["baseline"].append({"number": n, "disposition": disposition})
        if blue or 100 <= n <= 126:
            continue
        entries = additions[n]
        if n in {99, 127}:
            entries.sort(key=lambda e: (0 if e[1]["category"] in {"idol_pair", "guide_idol"} else 1 if "Tier 7" in e[1]["label"] or "Double" in e[1]["label"] else 3 if e[1]["category"] == "guide_altar" else 2))
        dedup = {}
        for r, row, loud in entries:
            key = signature(r)
            if key in dedup:
                dedup[key][1]["owners"] = sorted(set(dedup[key][1]["owners"]) | set(row["owners"]))
                dedup[key][1]["source_rules"].extend(row["source_rules"])
            else:
                dedup[key] = (r, row, loud)
        for r, row, loud in dedup.values():
            owner = row["owners"][0] if len(row["owners"]) == 1 else "SHARED"
            row["name"] = owner + " - " + row["label"]
            for field, value in {"type": "SHOW", "isEnabled": "true", "nameOverride": row["name"], "recolor": "true", "color": str(COLORS[owner]), "emphasized": str(loud).lower(), "SoundId": "6" if loud else "1"}.items():
                r.find(field).text = value
            if not loud:
                r.find("BeamOverride").text = "false"
                r.find("BeamSizeOverride").text = "NONE"
                r.find("MapIconId").text = "0"
            output.append(r)
            output_rows.append(row)
        if not entries or n in {8, 16}:
            output.append(original)
            output_rows.append({"template": n, "category": "experimental_exalted" if n == 68 else "raxx", "name": original.findtext("nameOverride"), "owners": ["NECRO"] if n == 68 else [], "source_rules": []})

    assert len(output) <= report["rule_limit"], len(output)
    assert sum(r["disposition"] == "player_instruction_removed" for r in report["baseline"]) == 56
    for i, (r, row) in enumerate(zip(output, output_rows)):
        r.find("Order").text = str(i)
        row.update(number=i + 1, enabled=r.findtext("isEnabled") == "true")
    for row in source_report:
        row["output_numbers"] = [r["number"] for r in output_rows if (row["build"], row["xml_position"]) in r["source_rules"]]
        if row["disposition"] == "planner_whitelist_rebuilt":
            layer = re.search(r"([123]) LP", row["name"])
            row["output_numbers"] = [r["number"] for r in output_rows if r["category"] == "build_unique" and BUILD_NAMES[row["build"]] in r["owners"] and (bool(layer) and layer.group(0) in r["label"] or not layer and " LP" not in r["label"])]
    root.find("rules").clear()
    root.find("rules").extend(reversed(output))
    root.find("name").text = "LE S5 - Flay + Skeleton - Raxx x Strict"
    root.find("description").text = "CoF endgame collection. Equal build priority. Pink=Flay, Blue=Skeleton, Mint=shared. See COMBINED_FILTER_GUIDE."
    ET.indent(root, space="  ")
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
    (ROOT / "filters").mkdir(exist_ok=True)
    (ROOT / OUTPUT).write_bytes(data)
    report.update(rules=len(output), enabled=sum(r["enabled"] for r in output_rows), output_sha256=hashlib.sha256(data).hexdigest(), output_rules=output_rows)
    (ROOT / "analysis/transfer-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = ["# 双 BD 成品规则索引", "", "由 scripts/generate_filter.py 生成。G=成品 Order+1，R=原基底编号，X=Strict 原XML物理位置。按G升序匹配；完整条件在成品XML，全部原规则处置见 analysis/transfer-report.json。", "", "| G | 状态 | R槽位 | 名称 | 依据 |", "|---:|---|---:|---|---|"]
    for row in output_rows:
        refs = "; ".join(BUILD_NAMES[slug] + " X" + str(pos) for slug, pos in row["source_rules"])
        if "idol_key" in row:
            refs = "Planner JSON " + str(row["idol_key"])
        lines.append(f"| {row['number']} | {'启用' if row['enabled'] else '关闭'} | {row['template']} | {(row['name'] or '').replace('|', '/')} | {refs or row['category']} |")
    (ROOT / "docs/GENERATED_RULE_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ["output", "rules", "enabled", "output_sha256", "target_unique_ids"]}))
    return root, report


if __name__ == "__main__":
    generate()
