"""Fill Base v1 from extracted Strict targets and the reviewed Flay idol policy."""
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from copy import deepcopy

from extract_raxx_variables import inspect_rule
from generate_filter import ROOT, XSI, T7_SLOTS, condition, frozen, read_json, replace_ints, signature

OUTPUT = "filters/Flay-Mana-Lich+Skeleton-Necromancer-v2.xml"
REPORT = "analysis/current-filter-report.json"
MAIN, SECONDARY = "flay-mana-lich", "skeleton-necromancer"
COLORS = {MAIN: "8", SECONDARY: "12"}


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
    for owner, ids in [(MAIN, common), (MAIN, set(targets[MAIN]) - common),
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
        if ids == common:
            row["owners"] = [MAIN, SECONDARY]
            row["strict_refs"] = [[c["build"], c["x"]] for c in candidates("V01")]
    base[15].find("nameOverride").text = "Raxx rare uniques + build whitelist (0 LP kept)"

    for c in candidates("V05"):
        assert len(c["types"]) == 1 and not c["subtypes"]
        typ = c["types"][0]
        add(T7_SLOTS[typ], c, "C1", "[1 TARGET T7] " + typ, c["affix_ids"], 1, True)
        add(62, c, "C3", "[3 TARGET + T7] " + typ, c["affix_ids"], 1)
    for c in candidates("V10"):
        add(63 if T7_SLOTS[c["types"][0]] < 40 else 64, c,
            "target_t6", "Target T6+ (level 0-84): " + c["types"][0], c["affix_ids"], 1)

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
    assert len(output) <= 200
    root.find("rules")[:] = list(reversed(output))
    root.find("name").text = "LE S5 - Flay + Skeleton v2 - Base v1"
    root.find("description").text = "MAIN Flay pink; SECONDARY Skeleton blue. Shared uses MAIN. Manually disable [4 ALL T7 PHASE] after collecting."
    ET.indent(root, space="  ")
    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
    (ROOT / OUTPUT).write_bytes(raw)
    report = {"output": OUTPUT, "output_sha256": hashlib.sha256(raw).hexdigest(), "base_template": m,
              "extraction_sha256": hashlib.sha256((ROOT / "analysis/raxx-variable-extraction.json").read_bytes()).hexdigest(),
              "display": {"main": MAIN, "secondary": SECONDARY, "shared_uses_main": True},
              "rules": len(output), "enabled": sum(r["enabled"] for r in rows), "output_rules": rows,
              "target_ids": targets, "target_union": evidence["target_union"], "baseline_dispositions": dispositions,
              "stage_rule": next(r["number"] for r in rows if r["category"] == "C4"),
              "defaults": {"urgent_shards": False, "ascendance": False, "ordinary_experimentals": False,
                           "target_bases": True, "skeleton_idols": "two ordinary targets; original Strict BIS subtypes"},
              "game_execution_tested": False}
    (ROOT / REPORT).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ["output", "rules", "enabled", "stage_rule"]}))


if __name__ == "__main__":
    main()
