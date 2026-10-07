"""Import target intelligence and fill the reviewed Raxx template."""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from extract_raxx_variables import family, gate_text, inspect_rule
from generate_filter import XSI, condition, frozen, read_json, replace_ints, signature
from generate_current_filter import ALERTS

CATALOG = read_json("sources/tool-catalog.json")
MANIFEST = read_json("templates/base-manifest.json")
EVIDENCE = read_json("analysis/raxx-variable-extraction.json")
BLUE = set(EVIDENCE["fixed_instruction_slots"]) | {n for v in EVIDENCE["variables"] for n in v["instruction_slots"]}
BASE_ROOT = frozen(MANIFEST)
BASE = dict(zip(MANIFEST["source_rule_order"], sorted(BASE_ROOT.find("rules"), key=lambda r: int(r.findtext("Order")))))
LEVEL_SLOTS = [n for n in [63, 64, 75, 128, 129, *range(135, 162)] if any(c.get(XSI + "type") in {"AffixCondition", "SubTypeCondition"} for c in BASE[n].find("conditions"))]
FAMILIES = {"planner": "uniques", "tier7": "equipment", "idol_single": "idols", "idol_bis": "idols",
            "altar": "altars", "rare_base": "bases", "crafting_base": "bases"}


def empty_profile():
    return {"uniques": [], "equipment": [], "altars": [], "idols": [], "bases": [], "leveling_slots": {}}


def extract(xml, assignments=None):
    if "<!DOCTYPE" in xml.upper() or "<!ENTITY" in xml.upper():
        raise ValueError("请使用普通Last Epoch XML，不能包含DTD或实体定义。")
    root = ET.fromstring(xml.lstrip("\ufeff"))
    if root.tag != "ItemFilter" or root.find("rules") is None:
        raise ValueError("这不是Last Epoch的ItemFilter XML。")
    profile, rows, warnings = empty_profile(), [], []
    groups = defaultdict(dict)
    for x, node in enumerate(root.find("rules"), 1):
        row = inspect_rule(node)
        auto = FAMILIES.get(family(row["name"]), "") if row["enabled"] and row["action"] in {"SHOW", "RECOLOR"} else ""
        if "[C1 BD目标T7]" in row["name"] or "[BD目标单T7]" in row["name"]:
            auto = "equipment" if row["enabled"] else ""
        category = (assignments or {}).get(str(x), auto)
        if category not in {"", *FAMILIES.values()}:
            raise ValueError("未知情报分类。")
        rows.append({"x": x, "name": row["name"], "enabled": row["enabled"], "action": row["action"],
                     "category": category, "auto": auto, "types": row["types"],
                     "affix_count": sum(map(len, row["affix_pools"])), "gate": gate_text(row)})
        if not category:
            continue
        if category == "uniques":
            profile[category].extend(row["unique_ids"])
            continue
        ids = sorted({i for pool in row["affix_pools"] for i in pool})
        unknown = [i for i in ids if str(i) not in CATALOG["affixes"]]
        if unknown:
            warnings.append(f"X{x}有词库未收录ID {unknown}，请更新词库或取消该规则的提取。")
            if category != "bases":
                profile["unresolved_affixes"] = sorted(set(profile.get("unresolved_affixes", [])) | set(unknown))
        if not row["types"]:
            warnings.append(f"X{x}没有物品类型，不能自动绑定{category}，请在编辑器中指定部位。")
            continue
        for typ in row["types"]:
            if typ not in CATALOG["types"]:
                warnings.append(f"X{x}未知物品类型{typ}。")
                continue
            special = lambda i: CATALOG["affixes"].get(str(i), {}).get("special", -1)
            core = [i for i in ids if special(i) in ({0, 5} if category == "idols" else {0, 1, 2, 3, 5, 7, -1})]
            if category == "altars":
                core = ids
            if category == "bases":
                core = []
            key = (typ, tuple(core)) if category == "idols" else (typ, tuple(row["subtypes"]))
            g = groups[category].setdefault(key, {"type": typ, "bases": [], "affixes": [], "corrupted": [], "enchanted": [], "sources": []})
            g["sources"].append({"x": x, "name": row["name"]})
            for field, values in [("bases", row["subtypes"]), ("affixes", core),
                                  ("corrupted", [i for i in ids if special(i) == 6]), ("enchanted", [i for i in ids if special(i) == 4])]:
                g[field] = sorted(set(g[field]) | set(values))
            if category == "idols":
                field = "pair_bases" if family(row["name"]) == "idol_bis" else "candidate_bases"
                g[field] = sorted(set(g.get(field, [])) | set(row["subtypes"]))
    for category, values in groups.items():
        for g in values.values():
            if category == "idols":
                g["pair_bases"] = g.get("pair_bases", g["bases"])
                g["bases"] = g.pop("candidate_bases", g["bases"])
            if category == "bases" or g["affixes"]:
                profile[category].append(g)
    profile["uniques"] = sorted(set(profile["uniques"]))
    for i in profile["uniques"]:
        if str(i) not in CATALOG["uniques"]:
            warnings.append(f"暗金ID {i}未在冻结词库中，请更新词库或移除。")
    return {"name": root.findtext("name") or "导入BD", "profile": profile, "rules": rows,
            "warnings": warnings, "source_sha256": hashlib.sha256(xml.encode()).hexdigest()}


def set_scope(rule, types, bases=()):
    c = condition(rule, "SubTypeCondition")
    c.find("type").clear()
    for typ in types:
        ET.SubElement(c.find("type"), "EquipmentType").text = typ
    replace_ints(c, "subTypes", bases)


def set_affix(rule, ids, count=1, tier=None, index=0, op="EQUAL"):
    c = [c for c in rule.find("conditions") if c.get(XSI + "type") == "AffixCondition"][index]
    replace_ints(c, "affixes", ids)
    for name, value in {"minOnTheSameItem": count, "advanced": str(tier is not None).lower(),
                        "comparsion": op if tier is not None else "ANY", "comparsionValue": tier or 0,
                        "combinedComparsion": "ANY"}.items():
        c.find(name).text = str(value)


def select_uniques(rule, ids):
    c = deepcopy(condition(BASE[15], "UniqueModifiersCondition"))
    prototype = deepcopy(c.find("Uniques"))
    prototype.find("Rolls").clear()
    c.clear()
    c.set(XSI + "type", "UniqueModifiersCondition")
    for uid in sorted(set(ids)):
        u = deepcopy(prototype)
        u.find("UniqueId").text = str(uid)
        c.append(u)
    rule.find("conditions").clear()
    rule.find("conditions").append(c)


def potential(rule, dimension, low, high=None):
    c = condition(rule, "PotentialCondition")
    for e in c:
        e.clear()
        e.set(XSI + "nil", "true")
    for prefix, value in [("Min", low), ("Max", high)]:
        if value is not None:
            e = c.find(prefix + dimension)
            e.attrib.clear()
            e.text = str(value)


def validate_profile(profile):
    if profile.get("unresolved_affixes"):
        raise ValueError(f"词库未识别这些来源词缀：{profile['unresolved_affixes']}。请更新词库或取消对应来源规则的提取。")
    for uid in profile["uniques"]:
        if str(uid) not in CATALOG["uniques"]:
            raise ValueError(f"暗金ID {uid}未在词库中。")
    for category in ["equipment", "altars", "idols", "bases"]:
        for g in profile[category]:
            typ = g["type"]
            allowed = typ in MANIFEST["scope_types"] if category in {"equipment", "bases"} else typ == "IDOL_ALTAR" if category == "altars" else typ.startswith("IDOL_") and typ != "IDOL_ALTAR"
            if not allowed:
                raise ValueError(f"{category}的物品类型不正确：{typ}。")
            for bid in set(g["bases"] + g.get("pair_bases", [])):
                if f"{typ}:{bid}" not in CATALOG["bases"]:
                    raise ValueError(f"未知底材{typ}:{bid}。")
            for aid in g["affixes"]:
                a = CATALOG["affixes"].get(str(aid))
                if a is None:
                    raise ValueError(f"词缀{aid}未在词库中，请检查来源或选择。")
                if category == "idols" and a["special"] not in {0, 5}:
                    raise ValueError(f"神像词缀{aid}是特殊附加词缀，不能加入普通计数。")
                if category == "equipment" and a["special"] in {4, 6}:
                    raise ValueError(f"装备词缀{aid}需另存附加参考，不属于普通T7目标池。")
    for key, override in profile["leveling_slots"].items():
        if int(key) not in LEVEL_SLOTS:
            raise ValueError(f"不存在练级入口R{key}。")
        if any(t not in CATALOG["types"] for t in override["types"]):
            raise ValueError("练级入口含未知物品类型。")
        if int(key) in {136, 137} and override["enabled"] and not override["types"]:
            raise ValueError("启用练级武器／副手入口前，请先选具体类型。")
        for aid in override["affixes"]:
            if str(aid) not in CATALOG["affixes"]:
                raise ValueError(f"练级词缀{aid}未在词库中。")
        for typ in override["types"]:
            for bid in override["bases"]:
                if f"{typ}:{bid}" not in CATALOG["bases"]:
                    raise ValueError(f"练级底材{typ}:{bid}未在词库中。")


def generate(config, mode="endgame"):
    if mode not in {"endgame", "leveling"}:
        raise ValueError("请选择终局或练级配置。")
    builds = [b for b in config["builds"] if b["enabled"]]
    if not builds or config["main_id"] not in {b["id"] for b in builds}:
        raise ValueError("请勾选至少一个BD，并把勾选的BD之一设为主套路。")
    builds.sort(key=lambda b: b["id"] != config["main_id"])
    for b in builds:
        validate_profile(b["profiles"][mode])
        if mode != "leveling":
            validate_profile(b["profiles"]["leveling"])
    replacements, result = defaultdict(list), []
    skip = BLUE | set(range(38, 49)) | {62, 63, 64, 69, 81, 82, 83, *range(99, 128)}
    full = MANIFEST["full_affix_ids"]

    def add(n, category, tier, build=None, group=None, count=1, affix_tier=None, index=0, name=None):
        r = deepcopy(BASE[n])
        if group is not None:
            set_scope(r, [group["type"]], group["bases"])
            if category != "bases":
                set_affix(r, group["affixes"], count, affix_tier, index)
        role = "主" if build and build["id"] == config["main_id"] else "副" if build else "通用"
        r.find("nameOverride").text = name or f"[{role} {category}] " + (build["name"] + " " if build else "") + (CATALOG["types"][group["type"]]["zh"] if group else "")
        r.find("isEnabled").text = "true"
        row = {"category": category, "tier": tier, "role": role, "owners": [build["name"]] if build else [], "source_raxx_rule": n}
        replacements[n].append((r, row))
        return r

    # Global multi-T7 and per-build layers are ordered by cue, then main/secondary.
    add(38, "任意至少三T7", 4, name="[任意至少三T7]")
    replacements[38][-1] = (deepcopy(BASE[48]), replacements[38][-1][1])
    r = replacements[38][-1][0]
    r.find("nameOverride").text = "[任意至少三T7]"
    set_affix(r, full, 3, 7)
    for category, count, alert, template in [("BD双目标T7", 2, 3, 38), ("双T7含BD目标", 1, 3, 38), ("BD目标单T7", 1, 2, 38), ("非目标T7＋BD目标", 1, 1, 62)]:
        for b in builds:
            for g in b["profiles"][mode]["equipment"]:
                if not g["affixes"] or category == "BD双目标T7" and len(set(g["affixes"])) < 2:
                    continue
                r = add(template, category, alert, b, g, count, None if template == 62 else 7, 1 if template == 62 else 0)
                if template == 62:
                    set_affix(r, full, 1, 7)
                elif category == "双T7含BD目标":
                    r.find("conditions").append(deepcopy(condition(BASE[48], "AffixCondition")))
                    set_affix(r, full, 2, 7, 1)
    c1 = [e for e in replacements[38] if e[1]["category"] == "BD目标单T7"]
    replacements[38] = [e for e in replacements[38] if e not in c1]
    r = add(38, "任意双T7", 2, name="[任意双T7]")
    r.find("conditions")[:] = deepcopy(BASE[48].find("conditions")[:])
    set_affix(r, full, 2, 7)
    replacements[38].extend(c1)
    peak = replacements[38].pop(0)
    result.append(peak)

    all_targets = {i for b in builds for i in b["profiles"][mode]["uniques"]}
    claimed = set()
    for b in builds:
        ids = set(b["profiles"][mode]["uniques"]) - claimed
        claimed |= ids
        if not ids:
            continue
        r = add(15, "BD暗金0LP也留", 1, b)
        select_uniques(r, ids)
        r = add(14, "BD暗金1LP", 3, b)
        select_uniques(r, ids)
        r.find("conditions").append(deepcopy(condition(BASE[14], "RarityCondition")))
        r.find("conditions").append(deepcopy(condition(BASE[14], "PotentialCondition")))
        potential(r, "LegendaryPotential", 1, 1)
    for n, lp, ww, tier in [(12, 3, 20, 4), (13, 2, 17, 3), (14, 1, 14, 2)]:
        r = add(n, f"任意LP{'≥' if lp == 3 else '='}{lp}", tier)
        r.find("conditions")[:] = [deepcopy(c) for c in BASE[n].find("conditions") if c.get(XSI + "type") != "UniqueModifiersCondition"]
        potential(r, "LegendaryPotential", lp, None if lp == 3 else lp)
        r = add(n, f"WW{ww}+" if ww == 20 else f"名单WW{ww}–{ww + 2}", tier)
        potential(r, "WeaversWill", ww, None if ww == 20 else ww + 2)
        if ww < 20:
            c = condition(r, "UniqueModifiersCondition")
            missing = all_targets - set(inspect_rule(r)["unique_ids"])
            tmp = deepcopy(BASE[15])
            select_uniques(tmp, missing)
            c.extend(deepcopy(condition(tmp, "UniqueModifiersCondition")[:]))
    # Put BD LP1 after higher potentials, ahead of generic LP1.
    replacements[14].sort(key=lambda e: e[1]["category"] != "BD暗金1LP")
    r = add(15, "珍贵名单低WW静音", 0)
    r.find("conditions").append(deepcopy(condition(BASE[14], "PotentialCondition")))
    potential(r, "WeaversWill", 1, 13)

    idol_targets = set()
    equipment_targets = set()
    for b in builds:
        p = b["profiles"][mode]
        for g in p["equipment"]:
            equipment_targets.update(g["affixes"])
            if g["affixes"]:
                r = add(63, "BD过渡T6：85级退出", 0, b, g, affix_tier=6)
                set_affix(r, g["affixes"], 1, 6, op="MORE_OR_EQUAL")
        for g in p["bases"]:
            if g["bases"]:
                add(82, "bases", 0, b, g)
        for g in p["altars"]:
            if g["affixes"]:
                add(127, "祭坛一项目标", 2, b, g)
        for g in p["idols"]:
            idol_targets.update(g["affixes"])
            if len(set(g["affixes"])) >= 2:
                add(99, "神像两普通目标", 3, b, {**g, "bases": g.get("pair_bases", g["bases"])}, 2)
            if g["affixes"]:
                add(99, "神像一普通目标", 2, b, g)
    replacements[99].sort(key=lambda e: -e[1]["tier"])

    # Raxx's early stages remain intact; separate explicit overrides only change targets.
    leveling_profiles = [b["profiles"]["leveling"] for b in builds]
    for n in LEVEL_SLOTS:
        overrides = [(b, p["leveling_slots"][str(n)]) for b, p in zip(builds, leveling_profiles) if str(n) in p["leveling_slots"]]
        if not overrides:
            continue
        replacements[n] = []
        skip.add(n)
        for b, override in overrides:
            r = add(n, "练级独立目标", 0, b, name=f"[{b['name']} 练级R{n}] 保留原等级与阶数")
            if override.get("types"):
                set_scope(r, override["types"], override.get("bases", []))
            a = next((c for c in r.find("conditions") if c.get(XSI + "type") == "AffixCondition"), None)
            if a is not None:
                replace_ints(a, "affixes", override["affixes"])
            r.find("isEnabled").text = str(override["enabled"] and (a is None or bool(override["affixes"]))).lower()
            if n in {128, 129, 135} and a is not None:
                replace_ints(a, "affixes", [i for i in override["affixes"] if CATALOG["affixes"][str(i)]["special"] in {0, 5}])
                if not len(a.find("affixes")):
                    r.find("isEnabled").text = "false"

    base = deepcopy(BASE)
    for n in [136, 137]:
        base[n].find("isEnabled").text = "false"
    for n in [128, 129, 135]:
        ids = {i for pool in inspect_rule(base[n])["affix_pools"] for i in pool if CATALOG["affixes"][str(i)]["special"] in {0, 5}}
        replace_ints(condition(base[n], "AffixCondition"), "affixes", ids | idol_targets)
    set_affix(base[37], full, 1, 8, op="MORE_OR_EQUAL")
    set_affix(base[60], full, 1, 7)
    base[60].find("isEnabled").text = str(config.get("extra_t7", True)).lower()
    base[60].find("nameOverride").text = "[额外单T7阶段：手动关闭]"
    for n in range(84, 89):
        base[n].find("isEnabled").text = str(bool(equipment_targets & {i for pool in inspect_rule(base[n])["affix_pools"] for i in pool})).lower()
    # Experimentals and T8 precede the silent optional single-T7 fallback.
    order = [n for n in MANIFEST["source_rule_order"] if n not in {37, 68, 70}]
    order[order.index(60):order.index(60)] = [68, 70, 37]
    for n in order:
        entries = list(replacements[n])
        if n not in skip:
            tier = {8: 3, 15: 1, 16: 1, 37: 1, 68: 1, 70: 1}.get(n, 0)
            entries.append((base[n], {"category": "Raxx通用", "tier": tier, "role": "通用", "owners": [], "source_raxx_rule": n}))
        result.extend(entries)
    # Deduplicate identical predicates, preserving main ownership and cue priority.
    merged, rows = {}, []
    for rule, row in result:
        key = (signature(rule), rule.findtext("isEnabled"), row["tier"])
        if key in merged:
            merged[key][1]["owners"] += [name for name in row["owners"] if name not in merged[key][1]["owners"]]
        else:
            merged[key] = (rule, row)
    if len(merged) > 200:
        raise ValueError(f"这些BD生成{len(merged)}条规则，超过200条。请减少选中的BD或目标分组；没有截断规则。")
    rules = []
    for i, (r, row) in enumerate(merged.values()):
        tier = row["tier"]
        sound_name, sound, icon, size, color, beam = ALERTS[tier]
        for field, value in {"Order": i, "SoundId": sound, "MapIconId": icon, "BeamOverride": "true", "BeamSizeOverride": size}.items():
            r.find(field).text = str(value)
        if row["owners"]:
            r.find("recolor").text = "true"
            r.find("color").text = "8" if row["role"] == "主" else "12"
        if tier:
            if row["owners"]:
                color, beam = ("8", "11") if row["role"] == "主" else ("12", "15")
            for field, value in {"recolor": "true", "color": color, "BeamColorOverride": beam, "emphasized": str(tier >= 3).lower()}.items():
                r.find(field).text = value
        facts = inspect_rule(r)
        rows.append({**row, "number": i + 1, "name": facts["name"] or ("显示传奇" if row["source_raxx_rule"] == 8 else "最终隐藏"),
                     "sound": sound_name, "enabled": facts["enabled"], "types": facts["types"],
                     "bases": facts["subtypes"], "affixes": facts["affix_pools"], "gate": gate_text(facts), "action": facts["action"]})
        rules.append(r)
    root = deepcopy(BASE_ROOT)
    root.find("rules")[:] = list(reversed(rules))
    label = "终局" if mode == "endgame" else "练级"
    root.find("name").text = f"LE Filter - {label} - " + " + ".join(b["name"] for b in builds)
    root.find("description").text = "Raxx base; main pink, secondary blue, shared main. Only exact T7 counts. Idols exclude enchantments and corruption."
    ET.indent(root, space="  ")
    xml = ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"
    return {"xml": xml, "rules": rows, "count": len(rows), "enabled": sum(r["enabled"] for r in rows),
            "mode": mode, "sha256": hashlib.sha256(xml.encode()).hexdigest()}


def bootstrap():
    catalog = deepcopy(CATALOG)
    catalog["equipment_types"] = MANIFEST["scope_types"]
    catalog["leveling_slots"] = [{"id": n, **inspect_rule(BASE[n]), "enabled": False if n in {136, 137} else BASE[n].findtext("isEnabled") == "true", "gate": gate_text(inspect_rule(BASE[n]))} for n in LEVEL_SLOTS]
    examples = []
    for slug, spec in EVIDENCE["strict_inputs"].items():
        imported = extract((ROOT / spec["file"]).read_text(encoding="utf-8-sig"))
        if slug == "flay-mana-lich":
            for g in imported["profile"]["idols"]:
                g["pair_bases"] = list(g["bases"])
        examples.append({"id": slug, "name": imported["name"], "enabled": True,
                         "profiles": {"endgame": imported["profile"], "leveling": empty_profile()},
                         "source": {"name": Path(spec["file"]).name, "warnings": imported["warnings"], "rules": imported["rules"]}})
    return {"catalog": catalog, "config": {"version": 1, "main_id": "flay-mana-lich", "extra_t7": True, "builds": examples}}
