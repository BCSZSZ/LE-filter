"""Fill Base v1 from extracted Strict targets and the reviewed Flay idol policy."""
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from copy import deepcopy

from extract_raxx_variables import inspect_rule
from generate_filter import ROOT, XSI, T7_SLOTS, condition, frozen, read_json, replace_ints, signature

OUTPUT = "filters/Flay-Mana-Lich+Skeleton-Necromancer-v3.xml"
REPORT = "analysis/current-filter-report.json"
MAIN, SECONDARY = "flay-mana-lich", "skeleton-necromancer"
COLORS = {MAIN: "8", SECONDARY: "12"}
STYLE_REFERENCE = "sources/filter-style-reference.json"
# Name, sound, map icon, beam size, common label color, common beam color.
ALERTS = {
    0: ("静音", "1", "1", "NONE", "1", "0"),
    1: ("铁匠", "14", "2", "SMALL", "3", "4"),
    2: ("开始", "6", "7", "MEDIUM", "4", "6"),
    3: ("灵感", "9", "8", "LARGE", "5", "7"),
    4: ("彗星", "12", "5", "LARGEST", "7", "10"),
}


def set_scope(rule, candidate):
    c = condition(rule, "SubTypeCondition")
    c.find("type").clear()
    for typ in candidate["types"]:
        ET.SubElement(c.find("type"), "EquipmentType").text = typ
    replace_ints(c, "subTypes", candidate["subtypes"])


def main():
    m = read_json("templates/base-manifest.json")
    evidence = read_json("analysis/raxx-variable-extraction.json")
    assert evidence["active_template"] == m
    root = frozen(m)
    nodes = sorted(root.find("rules"), key=lambda r: int(r.findtext("Order")))
    base = dict(zip(m["source_rule_order"], nodes, strict=True))
    positions = {n: i + 1 for i, n in enumerate(m["source_rule_order"])}
    variables = {v["id"]: v for v in evidence["variables"]}
    for spec in evidence["strict_inputs"].values():
        frozen(spec)
    flags = read_json("sources/builds/strict-variable-reference.json")["special_affix_type"]
    replacements = defaultdict(list)
    disabled = {29: "Class hide not selected", 70: "Champion targets not selected",
                81: "Ascendance target not selected", 83: "Check shard inventory before enabling",
                85: "Mage shards not requested", 86: "Primalist shards not requested",
                87: "Rogue shards not requested", 88: "Sentinel shards not requested",
                136: "Campaign weapon bases not supplied", 137: "Campaign offhand bases not supplied"}
    blue = set(evidence["fixed_instruction_slots"]) | {n for v in variables.values() for n in v["instruction_slots"]}
    assert len(blue) == 56

    def candidates(vid):
        return sorted((c for c in variables[vid]["evidence"] if c["enabled_in_source"]),
                      key=lambda c: (c["build"] != MAIN, c["x"]))

    def add(n, c, category, label, ids=None, count=None, loud=False):
        r = deepcopy(base[n])
        if c["types"]:
            set_scope(r, c)
        if ids is not None:
            a = [c for c in r.find("conditions") if c.get(XSI + "type") == "AffixCondition"][1 if category == "C3" else 0]
            replace_ints(a, "affixes", ids)
            if count is not None:
                a.find("minOnTheSameItem").text = str(count)
        r.find("nameOverride").text = label
        r.find("recolor").text = "true"
        r.find("color").text = COLORS[c["build"]]
        r.find("emphasized").text = str(loud).lower()
        r.find("SoundId").text = "6" if loud else "1"
        if not loud:
            for field, text in {"BeamOverride": "false", "BeamSizeOverride": "NONE", "MapIconId": "0"}.items():
                r.find(field).text = text
        row = {"source_raxx_rule": n, "base_rule": positions[n], "category": category,
               "owners": [c["build"]], "strict_refs": [[c["build"], c["x"]]] if "x" in c else []}
        replacements[n].append((r, row))
        return r, row

    # Target names join the original rare whitelist; separate cues keep BD ownership.
    targets = evidence["target_ids"]
    common = set(targets[MAIN]) & set(targets[SECONDARY])
    sources = {slug: list(frozen(spec).find("rules")) for slug, spec in evidence["strict_inputs"].items()}
    for owner, ids in [(MAIN, set(targets[MAIN])),
                       (SECONDARY, set(targets[SECONDARY]) - common)]:
        c = next(c for c in candidates("V01") if c["build"] == owner)
        r, row = add(15, c, "bd_unique", "Build uniques (0 LP kept)")
        src = condition(sources[owner][c["x"] - 1], "UniqueModifiersCondition")
        selected = deepcopy(src)
        selected[:] = []
        for uid in sorted(ids):
            item = next(u for u in src.findall("Uniques") if int(u.findtext("UniqueId")) == uid)
            selected.append(deepcopy(item))
            if uid not in inspect_rule(base[15])["unique_ids"]:
                condition(base[15], "UniqueModifiersCondition").append(deepcopy(item))
        r.find("conditions").clear()
        r.find("conditions").append(selected)
        row["shared_unique_ids"] = sorted(ids & common)
        if ids & common:
            row["strict_refs"] = [[c["build"], c["x"]] for c in candidates("V01")]
    base[15].find("nameOverride").text = "Raxx rare uniques + build whitelist (0 LP kept)"

    for c in candidates("V05"):
        assert len(c["types"]) == 1 and not c["subtypes"]
        typ = c["types"][0]
        add(T7_SLOTS[typ], c, "C1", "[C1 BD目标T7] " + typ, c["affix_ids"], 1, True)
        add(62, c, "C3", "[C3 非目标单T7＋BD目标词缀] " + typ, c["affix_ids"], 1)
    t6_groups = {}
    for c in candidates("V10"):
        n = 63 if T7_SLOTS[c["types"][0]] < 40 else 64
        assert not c["subtypes"]
        key = (n, c["build"], tuple(c["affix_ids"]))
        if key not in t6_groups:
            t6_groups[key] = (deepcopy(c), [])
        else:
            t6_groups[key][0]["types"].extend(c["types"])
        t6_groups[key][1].append([c["build"], c["x"]])
    for (n, _, _), (c, refs) in t6_groups.items():
        _, row = add(n, c, "target_t6", "[过渡T6：85级退出] " + "/".join(c["types"]), c["affix_ids"], 1)
        row["strict_refs"] = refs
    base[48].find("nameOverride").text = "[C2 任意双／多T7]"
    base[60].find("nameOverride").text = "[C4 额外单T7阶段：手动关闭]"
    replace_ints(condition(base[37], "AffixCondition"), "affixes", m["full_affix_ids"])
    base[37].find("nameOverride").text = "[T8保留兜底：铁匠] 全量词缀池"

    for c in candidates("V11"):
        add(69, c, "experimental_optional", "Optional wanted experimentals (OFF)", c["affix_ids"], 1)
    corruption = {i for c in candidates("V13") if not any(t.startswith("IDOL_") for t in c["types"])
                  for i in c["affix_ids"]}
    replace_ints(condition(base[75], "AffixCondition"), "affixes", corruption)
    base[75].find("nameOverride").text = "Selected corrupted equipment (level 0-59)"
    for c in candidates("V15"):
        add(82, c, "target_base", "Target base: " + c["types"][0])
    replace_ints(condition(base[83], "AffixCondition"), "affixes",
                 {i for c in candidates("V16") for i in c["affix_ids"]})

    # Flay's two ordinary targets define graduation; corruption never fills a slot.
    for c in evidence["user_reviewed_flay_idol_layers"]:
        count = c["min_matching_ordinary_affixes"]
        _, row = add(99, c, "idol_bis" if count == 2 else "idol_candidate",
                     "Idol " + ("pair complete: " if count == 2 else "one target: ") + c["types"][0],
                     c["affix_ids"], count, count == 2)
        row["strict_refs"] = [[c["build"], x] for x in c["source_x"]]
        row["policy"] = "User-reviewed Flay 1/2 ordinary targets; both Weaver and Lagon"
    for c in candidates("V19"):
        if c["build"] == SECONDARY and any(r["build"] == c["build"] and r["x"] == c["x"] and r["family"] == "idol_bis" for r in evidence["strict_rules"]):
            add(99, c, "idol_bis", "Idol two ordinary targets: " + c["types"][0], c["affix_ids"], 2, True)
    # Altars use Raxx's one-target, any-tier gate with BD-specific base bindings.
    altar_groups = {}
    for c in candidates("V20"):
        key = (c["build"], tuple(c["types"]), tuple(c["subtypes"]))
        if key not in altar_groups:
            altar_groups[key] = (deepcopy(c), set(), [])
        altar_groups[key][1].update(c["affix_ids"])
        altar_groups[key][2].append([c["build"], c["x"]])
    for c, ids, refs in altar_groups.values():
        _, row = add(127, c, "altar", "Altar target (any tier)", ids, 1, True)
        row["strict_refs"] = refs
    ordinary = {i for c in candidates("V19") for i in c["affix_ids"]}
    for n in [128, 129]:
        a = condition(base[n], "AffixCondition")
        replace_ints(a, "affixes", ordinary | {int(i.text) for i in a.findall("affixes/int") if flags[i.text] != 6})
        base[n].find("nameOverride").text = "General ordinary idol targets (level 0-" + ("89" if n == 128 else "74") + ")"
    for n, reason in disabled.items():
        base[n].find("isEnabled").text = "false"
        base[n].find("nameOverride").text = "OFF - " + reason

    output, rows, dispositions = [], [], []
    for n in m["source_rule_order"]:
        disposition = "instruction_removed" if n in blue else "idol_template_replaced" if 100 <= n <= 126 else "replaced" if replacements[n] else "disabled" if n in disabled else "retained_or_filled"
        dispositions.append({"source_raxx_rule": n, "base_rule": positions[n], "disposition": disposition})
        if n in blue or 100 <= n <= 126:
            continue
        dedup = {}
        for r, row in replacements[n]:
            key = (signature(r), r.findtext("isEnabled"), r.findtext("SoundId"))
            if key in dedup:
                dedup[key][1]["owners"] = sorted(set(dedup[key][1]["owners"]) | set(row["owners"]))
                dedup[key][1]["strict_refs"].extend(row["strict_refs"])
            else:
                dedup[key] = (r, row)
        entries = sorted(dedup.values(), key=lambda e: (e[1]["category"] == "idol_candidate", MAIN not in e[1]["owners"]))
        if not entries or n == 15:
            entries.append((base[n], {"source_raxx_rule": n, "base_rule": positions[n],
                                     "category": {48: "C2", 60: "C4"}.get(n, "base"), "owners": [], "strict_refs": []}))
        for r, row in entries:
            role = "MAIN" if MAIN in row["owners"] else "SECONDARY" if row["owners"] else "COMMON"
            if row["owners"]:
                r.find("color").text = "8" if role == "MAIN" else "12"
                r.find("nameOverride").text = role + " - " + r.findtext("nameOverride")
            r.find("Order").text = str(len(output))
            row.update(number=len(output) + 1, role=role, enabled=r.findtext("isEnabled") == "true",
                       name=r.findtext("nameOverride"), strict_refs=sorted({tuple(x) for x in row["strict_refs"]}))
            output.append(r)
            rows.append(row)

    # Explicit LP and WW branches allow independent sounds without guessing an OR.
    def set_potential(rule, dimension, low, high=None):
        p = condition(rule, "PotentialCondition")
        for e in p:
            e.clear()
            e.set(XSI + "nil", "true")
        for prefix, value in [("Min", low), ("Max", high)]:
            if value is not None:
                e = p.find(prefix + dimension)
                e.attrib.clear()
                e.text = str(value)

    entries = list(zip(output, rows))
    lp, ww = {}, {}
    for r, row in entries:
        n = row["source_raxx_rule"]
        if n not in {12, 13, 14}:
            continue
        wr, wrow = deepcopy(r), deepcopy(row)
        threshold = {12: 20, 13: 17, 14: 14}[n]
        set_potential(wr, "WeaversWill", threshold, {13: 19, 14: 16}.get(n))
        if n != 12:
            selected = condition(wr, "UniqueModifiersCondition")
            missing = set(evidence["target_union"]) - set(inspect_rule(wr)["unique_ids"])
            for uid in sorted(missing):
                selected.append(deepcopy(next(u for u in condition(base[15], "UniqueModifiersCondition").findall("Uniques") if int(u.findtext("UniqueId")) == uid)))
        wr.find("nameOverride").text = "WW暗金：" + str(threshold) + ("+" if n == 12 else "–" + str({13: 19, 14: 16}[n]))
        wrow.update(category="ww_unique", ww_min=threshold)
        ww[n] = (wr, wrow)
        selected = next((c for c in r.find("conditions") if c.get(XSI + "type") == "UniqueModifiersCondition"), None)
        if selected is not None:
            r.find("conditions").remove(selected)
        count = {12: 3, 13: 2, 14: 1}[n]
        set_potential(r, "LegendaryPotential", count, None if count == 3 else count)
        r.find("nameOverride").text = "任意暗金：LP" + ("≥3" if count == 3 else "=" + str(count))
        row.update(category="lp_unique", lp_min=count)
        lp[n] = (r, row)
    target_lp1 = []
    for r, row in entries:
        if row["category"] != "bd_unique":
            continue
        r.find("nameOverride").text = row["role"] + " - BD目标暗金（0LP也留）"
        tr, trow = deepcopy(r), deepcopy(row)
        tr.find("conditions").append(deepcopy(condition(lp[14][0], "PotentialCondition")))
        tr.find("conditions").append(deepcopy(condition(lp[14][0], "RarityCondition")))
        tr.find("nameOverride").text = row["role"] + " - BD目标暗金：LP=1"
        trow.update(category="bd_unique_lp1", lp_min=1)
        target_lp1.append((tr, trow))
    insertion = next(i for i, (_, row) in enumerate(entries) if row["source_raxx_rule"] == 12)
    entries = [e for e in entries if e[1]["source_raxx_rule"] not in {12, 13, 14}]
    entries[insertion:insertion] = [lp[12], ww[12], lp[13], ww[13], *target_lp1, lp[14], ww[14]]
    # Low-WW non-BD items keep their original whitelist path, silently.
    insertion = next(i for i, (_, row) in enumerate(entries) if row["category"] == "base" and row["source_raxx_rule"] == 15)
    r, row = deepcopy(entries[insertion])
    r.find("conditions").append(deepcopy(condition(lp[14][0], "PotentialCondition")))
    set_potential(r, "WeaversWill", 1, 13)
    r.find("nameOverride").text = "珍贵名单WW1–13：静音保留"
    row.update(category="low_ww_saved", alert_tier=0)
    entries.insert(insertion, (r, row))

    # Multi-T7 needs to precede C1; otherwise a target T7 steals its sound.
    indices = [i for i, (_, row) in enumerate(entries) if row["category"] in {"C1", "C2"}]
    multi = next(e for e in entries if e[1]["category"] == "C2")
    multi_rules = []
    for count, tier in [(4, 4), (3, 3), (2, 1)]:
        r, row = deepcopy(multi)
        condition(r, "AffixCondition").find("minOnTheSameItem").text = str(count)
        r.find("nameOverride").text = "[C2 任意" + str(count) + "条以上T7]"
        row.update(minimum_t7=count, alert_tier=tier)
        multi_rules.append((r, row))
    c1 = sorted((e for e in entries if e[1]["category"] == "C1"), key=lambda e: e[1]["role"] != "MAIN")
    entries[min(indices):max(indices) + 1] = multi_rules + c1
    indices = [i for i, (_, row) in enumerate(entries) if row["category"] == "target_t6"]
    entries[min(indices):max(indices) + 1] = sorted((entries[i] for i in indices), key=lambda e: e[1]["role"] != "MAIN")
    quality = [e for e in entries if e[1]["source_raxx_rule"] in {68, 69, 70}]
    entries = [e for e in entries if e[1]["source_raxx_rule"] not in {68, 69, 70}]
    insertion = next(i for i, (_, row) in enumerate(entries) if row["category"] == "C4")
    entries[insertion:insertion] = quality
    # T8 is a separate fallback, not another T7 for target or multi-affix counts.
    for r, row in entries:
        if row["category"] in {"C1", "C2", "C3", "C4"}:
            condition(r, "AffixCondition").find("comparsion").text = "EQUAL"
    t8 = next(e for e in entries if e[1]["source_raxx_rule"] == 37)
    entries.remove(t8)
    insertion = next(i for i, (_, row) in enumerate(entries) if row["category"] == "C4")
    entries.insert(insertion, t8)
    peaks = [e for e in entries if e[1]["category"] == "C2" and e[1]["minimum_t7"] == 4]
    entries = peaks + [e for e in entries if e not in peaks]

    style = read_json(STYLE_REFERENCE)
    output, rows = [], []
    for r, row in entries:
        tier = row.get("alert_tier", {"C1": 2, "C3": 1, "bd_unique": 1, "bd_unique_lp1": 3,
                                     "idol_bis": 3, "idol_candidate": 2, "altar": 2,
                                     "experimental_optional": 1}.get(row["category"],
                                     {8: 3, 15: 1, 16: 1, 37: 1, 68: 1, 70: 1}.get(row["source_raxx_rule"], 0)))
        if row["category"] in {"lp_unique", "ww_unique"}:
            tier = {1: 2, 2: 3, 3: 4}[row["lp_min"]] if row["category"] == "lp_unique" else {14: 2, 17: 3, 20: 4}[row["ww_min"]]
        name, sound, icon, size, color, beam = ALERTS[tier]
        assert style["sounds"][sound]["zh"] == name and icon in style["map_icons"]
        if row["owners"]:
            color, beam = ("8", "11") if row["role"] == "MAIN" else ("12", "15")
        for field, value in {"SoundId": sound, "MapIconId": icon, "BeamOverride": "true",
                             "BeamSizeOverride": size, "BeamColorOverride": beam if tier else "0"}.items():
            r.find(field).text = value
        if tier or not row["owners"]:
            r.find("recolor").text = "true"
            r.find("color").text = color
            r.find("emphasized").text = str(tier >= 3).lower()
        r.find("Order").text = str(len(output))
        row.update(number=len(output) + 1, name=r.findtext("nameOverride"), alert_tier=tier, sound_name=name)
        output.append(r)
        rows.append(row)
    assert len(output) <= 200
    root.find("rules")[:] = list(reversed(output))
    root.find("name").text = "LE S5 - Flay + Skeleton v3 - Four sounds"
    root.find("description").text = "MAIN pink; SECONDARY blue; shared MAIN. Smith / Begin / Inspiration / Comet. Silent rules have no map icon or beam. Disable C4 manually."
    ET.indent(root, space="  ")
    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
    (ROOT / OUTPUT).write_bytes(raw)
    report = {"output": OUTPUT, "output_sha256": hashlib.sha256(raw).hexdigest(), "base_template": m,
              "extraction_sha256": hashlib.sha256((ROOT / "analysis/raxx-variable-extraction.json").read_bytes()).hexdigest(),
              "display": {"main": MAIN, "secondary": SECONDARY, "shared_uses_main": True},
              "rules": len(output), "enabled": sum(r["enabled"] for r in rows), "output_rules": rows,
              "target_ids": targets, "target_union": evidence["target_union"], "baseline_dispositions": dispositions,
              "stage_rule": next(r["number"] for r in rows if r["category"] == "C4"),
              "feedback_reference": {"local_path": STYLE_REFERENCE, "sha256": hashlib.sha256((ROOT / STYLE_REFERENCE).read_bytes()).hexdigest()},
              "feedback": {"tiers": ALERTS, "silent_map_icon_is_none": True, "ww_thresholds": [14, 17, 20],
                           "t7_priority": ["C2 (4+)", "C2 (3)", "C2 (2)", "C1", "C3", "C4"],
                           "t7_exact_tier": 7, "t8_fallback_tier": 1,
                           "t8_after_targets_and_experimentals": True,
                           "experimental_and_champion_before_phase": True,
                           "t6_rules": len(t6_groups), "t6_collection_unchanged": True, "per_rule_volume": False},
              "defaults": {"urgent_shards": False, "ascendance": False, "ordinary_experimentals": False,
                           "target_bases": True, "skeleton_idols": "two ordinary targets; original Strict BIS subtypes"},
              "game_execution_tested": False}
    (ROOT / REPORT).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ["output", "rules", "enabled", "stage_rule"]}))


if __name__ == "__main__":
    main()
