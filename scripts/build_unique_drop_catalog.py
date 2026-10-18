"""Build the selector's drop information from frozen, attributed game data.

This script has no network or game-install dependency and does not alter the
filter engine, target inputs, or original catalog. Probabilities are per reward
item, not per prophecy and not the item's reroll percentage.
"""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "sources/unique-drop-inputs-2026-10-18.json"
OUTPUT = ROOT / "sources/unique-drop-catalog.json"
CLASSES = {"Sentinel": 4, "Mage": 2, "Primalist": 1, "Acolyte": 8, "Rogue": 16}
CLASS_ZH = {"Sentinel": "守卫", "Mage": "法师", "Primalist": "原始人", "Acolyte": "侍祭", "Rogue": "游侠"}


def reroll_distribution(reroll_chances, max_rerolls=60):
    """Uniform proposals, 60 rejected proposals, then accept the final draw.

    Returns a distribution in input order. This also works for the all-reject
    limiting case, where the final untested proposal remains uniform.
    """
    if not reroll_chances:
        return []
    if max_rerolls < 0 or any(not 0 <= r <= 1 for r in reroll_chances):
        raise ValueError("Invalid reroll model")
    n = len(reroll_chances)
    rejection = sum(reroll_chances) / n
    factor = sum(rejection ** attempt for attempt in range(max_rerolls)) / n
    final_draw = rejection ** max_rerolls / n
    return [(1 - r) * factor + final_draw for r in reroll_chances]


def class_compatible(item, class_mask):
    return any(not sub["classRequirement"] or sub["classRequirement"] & class_mask
               for sub in item["subTypeRequirements"])


def prophecy_distribution(pool, class_mask, compatibility_chance=0.800000011920929, max_rerolls=60):
    """Mix unrestricted and class-compatible unique selection; no BD guessing."""
    all_rates = dict(zip((i["uniqueID"] for i in pool),
                         reroll_distribution([i["rerollChance"] for i in pool], max_rerolls)))
    compatible = [i for i in pool if class_compatible(i, class_mask)]
    # SpawnRewardForPlayer tests whether the compatible pool exists; if not,
    # spawning proceeds without the optional compatibility constraint.
    if not compatible:
        return all_rates
    compatible_rates = dict(zip((i["uniqueID"] for i in compatible),
                                reroll_distribution([i["rerollChance"] for i in compatible], max_rerolls)))
    return {uid: (1 - compatibility_chance) * rate + compatibility_chance * compatible_rates.get(uid, 0)
            for uid, rate in all_rates.items()}


def single_reward_probability(attempts, weight, total_weight):
    """Chance for one independent reward opportunity, ignoring extra draws."""
    if attempts <= 0 or weight <= 0 or total_weight <= 0:
        return 0.0
    return min(attempts, 1) * weight / total_weight


def independent_reward_scenarios(rates):
    """List single-reward rates with their gates; never combine extra rewards.

    Zero tier rows denote inactive groups. Show a zero only if the item has no
    active group at that tier. Equal independent rewards share a display entry,
    while their original source indexes remain available for inspection.
    """
    tiers = sorted({t["tier"] for r in rates for t in r.get("tierProbabilities", [])}) or [None]
    result, seen = [], {}
    for tier in tiers:
        candidates = []
        for rate in rates:
            if rate.get("tierProbabilities"):
                low = high = next((t["probability"] for t in rate["tierProbabilities"] if t["tier"] == tier), 0)
            elif "probability" in rate:
                low, high = rate["probability"], rate.get("maximumProbability", rate["probability"])
            else:
                continue
            gates = {k: rate.get(k, 0) for k in ["minLevel", "maxLevel", "minCorruption", "maxCorruption"]}
            candidates.append({"tier": tier, "hostOnly": bool(rate.get("hostOnly")), "probability": low,
                               "maximumProbability": high, **gates, "sourceGroups": [rate.get("sourceGroupIndex")]})
        active = [c for c in candidates if c["maximumProbability"] > 0]
        for scenario in active or candidates[:1]:
            key = tuple((k, v) for k, v in scenario.items() if k != "sourceGroups")
            if key in seen:
                seen[key]["sourceGroups"].extend(scenario["sourceGroups"])
            else:
                result.append(scenario)
                seen[key] = scenario
    return result


def percentage(value):
    if value == 0:
        return "0%"
    if value == 1:
        return "100%"
    percent = value * 100
    digits = 4 if percent < 0.01 else 3 if percent < 0.1 else 2
    return f"{percent:.{digits}f}".rstrip("0").rstrip(".") + "%"


def range_text(values):
    low, high = min(values), max(values)
    return percentage(low) if math.isclose(low, high, rel_tol=1e-10, abs_tol=1e-14) else f"{percentage(low)}–{percentage(high)}"


def rate_from_group(group, target):
    rate = {k: v for k, v in group.items() if k != "targets"}
    rate.update(target)
    rate["probability"] = single_reward_probability(group["dropChance"], target["weight"], target["totalWeight"])
    rate["maximumProbability"] = single_reward_probability(max(group["dropChance"], group.get("maxDropChance", 0)), target["weight"], target["totalWeight"])
    rate["tierProbabilities"] = [{"tier": t["tier"] + 1, "probability": single_reward_probability(t["dropChance"], target["weight"], target["totalWeight"])}
                                 for t in group.get("dropChancesForTiers", [])]
    return rate


def source_location(kind, name, url, rates):
    scenarios = independent_reward_scenarios(rates)
    values, conditions = [], []
    has_host_condition = any(r.get("hostOnly") for r in rates)
    for scenario in scenarios:
        low, high = scenario["probability"], scenario["maximumProbability"]
        values.extend([low, high])
        labels = []
        if scenario["tier"] is not None:
            labels.append(f"T{scenario['tier']}")
        if has_host_condition:
            labels.append("开启者专属奖励" if scenario["hostOnly"] else "所有玩家独立奖励")
        if labels:
            conditions.append("／".join(labels) + " " + range_text([low, high]))
    for rate in rates:
        if rate.get("minLevel", 0) >= 100:
            conditions.append("仅强化时间线")
        elif rate.get("minLevel", 0) > 0:
            conditions.append(f"区域等级≥{rate['minLevel']}")
        if rate.get("maxLevel", 0) > 0:
            conditions.append(f"区域等级≤{rate['maxLevel']}")
        if rate.get("minCorruption", 0) > 0:
            conditions.append(f"腐化≥{rate['minCorruption']}")
        if rate.get("maxCorruption", 0) > 0:
            conditions.append(f"腐化≤{rate['maxCorruption']}")
        if rate.get("chanceMultiplierPerCorruption", 0) or rate.get("multiplyChanceBySquareTierPercent") or rate.get("chanceModifier") in [1, 3, 4]:
            conditions.append("受腐化／层级影响，数值为基础值")
    if any(s["maximumProbability"] > s["probability"] for s in scenarios):
        conditions.append("范围随物品稀有度提高")
    if kind == "boss":
        conditions.append("单次独立奖励基础掉率；未计命运阵营加成")
    elif scenarios:
        conditions.append("每次独立奖励")
    probability = range_text(values) if values else "未公开固定概率"
    return {"kind": kind, "name": name, "url": url, "probabilityText": probability,
            "conditions": list(dict.fromkeys(conditions)), "rates": rates, "scenarios": scenarios}


def build():
    frozen = json.loads(INPUT.read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "sources/tool-catalog.json").read_text(encoding="utf-8"))
    native = {i["uniqueID"]: i for i in frozen["uniques"]}
    assert set(native) == {int(k) for k in catalog["uniques"]}
    active = [i for i in native.values() if i["canDropRandomly"] and not i["hideFromPlayers"] and
              (i["customDropLevel"] <= 100 if i["useCustomDropLevel"] else
               i["levelRequirement"] <= 100 if i["overrideLevelRequirement"] else
               any(s["levelRequirement"] <= 100 for s in i["subTypeRequirements"]))]
    unique_pools = defaultdict(list)
    for item in active:
        if not item["isSetItem"]:
            unique_pools[item["baseType"]].append(item)
    probabilities = defaultdict(dict)
    pools = {}
    idol_counts = Counter(frozen["uniqueIdolBaseTypeOccurrences"])
    for base, pool in sorted(unique_pools.items()):
        pools[str(base)] = [i["uniqueID"] for i in pool]
        for klass, mask in CLASSES.items():
            if 25 <= base <= 33:
                # Unique Idol first samples the cached list of base types, one
                # occurrence per random unique idol, then rolls within that type.
                factor = idol_counts[base] / sum(idol_counts.values())
                rates = dict(zip((i["uniqueID"] for i in pool), reroll_distribution([i["rerollChance"] for i in pool])))
                rates = {uid: p * factor for uid, p in rates.items()}
            else:
                rates = prophecy_distribution(pool, mask)
            for uid, probability in rates.items():
                probabilities[uid][klass] = probability
    named = defaultdict(list)
    for boss in frozen["bosses"]:
        grouped = defaultdict(list)
        for group in boss["groups"]:
            for target in group["targets"]:
                grouped[target["id"]].append(rate_from_group(group, target))
        for uid, rates in grouped.items():
            location = source_location("boss", boss.get("zh") or boss["name"], "https://lastepoch.tunklab.com/npc/" + boss["id"], rates)
            location["sourceNameEn"] = boss["name"]
            named[uid].append(location)
    tunklab_boss_ids = set(named)
    for echo in frozen["echoes"]:
        grouped = defaultdict(list)
        for group in echo["groups"]:
            for target in group["targets"]:
                grouped[target["id"]].append(rate_from_group(group, target))
        for uid, rates in grouped.items():
            location = source_location("special", "编织回响：" + (echo.get("zh") or echo["name"]), "https://lastepoch.tunklab.com/echo/" + echo["slug"], rates)
            location["conditions"].insert(0, "完成该回响的奖励")
            if echo.get("minPlacementCorruption"):
                location["conditions"].append(f"放置该回响需腐化≥{echo['minPlacementCorruption']}")
            named[uid].append(location)
    supplement = defaultdict(list)
    for index, row in enumerate(frozen["letoolsSupplementalDrops"]):
        if not row.get("monsterNameKey"):
            continue
        row = {**row, "sourceGroupIndex": f"letools:{index}"}
        en = row["monsterNameKey"].removeprefix("Actors.Actor_Name_")
        supplement[(row["uniqueId"], row.get("zh") or en)].append(row)
    for (uid, name), rows in supplement.items():
        # The cached LETools rows sometimes label a pinnacle/woven boss with
        # its non-pinnacle name. Current Tunklab owns the named boss groups;
        # use old rows only for IDs absent from those groups, retaining all
        # unmodified supplemental records in the frozen input for inspection.
        if uid in tunklab_boss_ids:
            continue
        rates = []
        for r in rows:
            rate = dict(r)
            if "chance" in r:
                rate["probability"] = min(r["chance"], 1)
                rate["maximumProbability"] = min(max(r["chance"], r.get("maxChance", 0)), 1)
            if "chancePerTier" in r:
                rate["tierProbabilities"] = [{"tier": n + 1, "probability": min(p, 1)} for n, p in enumerate(r["chancePerTier"])]
            if r.get("timelineInfo", {}).get("empoweredOnly"):
                rate["minLevel"] = 100
            rates.append(rate)
        kind = "special" if rows[0].get("soulGambler") or rows[0].get("nemesis") else "boss"
        location = source_location(kind, name, native[uid].get("slug") and "https://lastepoch.tunklab.com/unique/" + native[uid]["slug"] or "https://www.lastepochtools.com/db/", rates)
        if kind == "special":
            location["conditions"].insert(0, "涅墨西斯奖励选项，非普通地面掉落" if rows[0].get("nemesis") else "灵魂赌徒：每次购买对应部位，按副本T1–T4")
        named[uid].append(location)
    items = {}
    for uid, raw in sorted(native.items()):
        c = catalog["uniques"][str(uid)]
        source_url = "https://lastepoch.tunklab.com/unique/" + raw["slug"] if raw.get("slug") else "https://www.lastepochtools.com/db/"
        kind = "legacy" if raw["hideFromPlayers"] or c["hidden"] else "world" if raw["canDropRandomly"] else "boss" if raw["isPrimordialItem"] or named[uid] and any(l["kind"] == "boss" for l in named[uid]) else "special"
        row = {"kind": kind, "locations": [], "prophecyProbability": None, "probabilityText": "不由普通暗金预言产出", "sourceUrl": source_url,
               "set": bool(raw["isSetItem"]), "weaversWill": raw["legendaryType"] == 1, "primordial": bool(raw["isPrimordialItem"]), "cocooned": bool(raw["isCocoonedItem"])}
        if raw.get("image"):
            row["iconUrl"] = "https://lastepoch.tunklab.com/img/item/" + raw["image"]
        if kind == "world":
            conditions = []
            if raw["isSetItem"]:
                row["prophecyProbability"] = 0
                row["probabilityText"] = "0%（需套装预言）"
                conditions.append("普通暗金预言不产出套装；套装预言另有奖励池")
            else:
                row["prophecyByClass"] = probabilities[uid]
                values = list(probabilities[uid].values())
                row["probabilityText"] = range_text(values)
                if math.isclose(min(values), max(values), rel_tol=1e-10, abs_tol=1e-14):
                    row["prophecyProbability"] = values[0]
                else:
                    conditions.append("职业不同：" + "；".join(f"{CLASS_ZH[k]} {percentage(p)}" for k, p in probabilities[uid].items()))
                conditions.append("每件暗金神像预言奖励" if c["type"].startswith("IDOL_") else "100级、命运12；每件同类型暗金预言奖励")
            row["locations"].append({"kind": "world", "name": "世界掉落", "url": source_url, "probabilityText": row["probabilityText"], "conditions": conditions})
        elif kind == "legacy":
            row["locations"] = [{"kind": "legacy", "name": "旧／隐藏条目", "url": source_url, "probabilityText": "当前版本不进入随机掉落池", "conditions": ["已选ID保留；" + ("本机1.5.2.2标记为隐藏" if raw["hideFromPlayers"] else "原词库隐藏条目")]}]
        row["locations"].extend(named[uid])
        if raw["isPrimordialItem"]:
            row["locations"].append({"kind": "boss", "name": "裂隙野兽", "url": frozen["officialSources"]["primordial"], "probabilityText": "随进化／材料／腐化变化，无固定值", "conditions": ["先古暗金；命运Boss掉落加成生效"]})
            costs = [f"{name}×{raw[field]}" for field, name in [("primordialFeatherCost", "先古羽毛"), ("primordialFangCost", "先古尖牙"), ("primordialPetalCost", "先古花瓣"), ("primordialHornCost", "先古犄角"), ("crystallisedHeartCost", "结晶之心"), ("ancientBoneCost", "远古骨骼")] if raw[field]]
            if costs:
                row["locations"].append({"kind": "special", "name": "斯卡文·血角兑换", "url": source_url, "probabilityText": "兑换获得", "conditions": costs})
        if raw["isCocoonedItem"]:
            row["locations"].append({"kind": "special", "name": "编织回响：茧化物品目标", "url": frozen["officialSources"]["cocooned"], "probabilityText": "完成目标奖励；具体部位概率未公开", "conditions": ["击杀目标后获得；鉴定为该部位随机暗金，排除Boss专属"]})
        if uid == 131:
            row["locations"].append({"kind": "special", "name": "任务：埃尔扎的账本", "url": source_url, "probabilityText": "任务奖励", "conditions": ["完成任务后领取"]})
        if uid == 130:
            row["locations"].append({"kind": "special", "name": "第二章：阿尔特姆任务", "url": frozen["officialSources"]["gamblersFallacyQuest"], "probabilityText": "任务奖励（完成后领取）", "conditions": []})
        if str(uid) in frozen.get("specialRecipes", {}):
            recipe = frozen["specialRecipes"][str(uid)]
            base = catalog["bases"]["HELMET:" + str(recipe["subType"])]
            row["locations"].append({"kind": "special", "name": "制作：符文·升华", "url": source_url, "probabilityText": "符合配方时100%", "conditions": [base["zh"] + "（" + base["en"] + "）", "必须同时含魔力34、伤害由魔力优先承受53", "全部词缀总T≥21，含封印词缀"], "recipe": recipe})
        if uid == 444:
            row["locations"].append({"kind": "special", "name": "裂隙野兽：结束谱系", "url": frozen["officialSources"]["lineage"], "probabilityText": "结束谱系的奖励", "conditions": ["非世界随机掉落；奖励数量／分配概率未在该来源给出固定值"]})
        if not row["locations"]:
            row["locations"].append({"kind": "special", "name": "特殊获取", "url": source_url, "probabilityText": "当前来源／概率未核实", "conditions": ["非世界随机掉落"]})
        items[str(uid)] = row
    return {"version": 1, "gameVersion": frozen["gameVersion"], "asOf": frozen["retrievedOn"],
            "context": {"areaLevel": 100, "circleOfFortuneRank": 12, "lens": "none", "denominator": "每件同类型普通暗金预言奖励；神像使用暗金神像预言", "bossRateScope": "每次独立奖励的基础掉率及其稀有度范围，额外奖励次数不合并，未计命运Boss奖励加成；副本/腐化/开启者条件逐项保留", "classCompatibilityChance": frozen["nativeRoll"]["classCompatibilityChance"], "uniqueIdolBaseTypeOccurrences": frozen["uniqueIdolBaseTypeOccurrences"]},
            "sources": {**frozen["sources"], "frozenInput": {"path": INPUT.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest()}, "official": frozen["officialSources"]},
            "prophecyPools": pools, "items": items,
            "summary": {"items": len(items), "kinds": dict(Counter(i["kind"] for i in items.values())), "numericProphecy": sum(bool(i.get("prophecyByClass")) for i in items.values()), "icons": sum("iconUrl" in i for i in items.values()), "iconsVerified": len(frozen["iconValidation"]), "gameExecutionTested": False}}


if __name__ == "__main__":
    result = build()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], ensure_ascii=False))
