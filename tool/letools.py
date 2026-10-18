"""Target-only LETools character imports; network access stays outside Python."""
from copy import deepcopy
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit, quote

from engine import CATALOG, MANIFEST, empty_profile, validate_profile
from requirements import read_document
from character_save import decode_character

# Numeric order copied from the frozen sources/game-reference.json equipment_enum.
TYPES = ("HELMET BODY_ARMOR BELT BOOTS GLOVES ONE_HANDED_AXE ONE_HANDED_DAGGER "
         "ONE_HANDED_MACES ONE_HANDED_SCEPTRE ONE_HANDED_SWORD WAND ONE_HANDED_FIST "
         "TWO_HANDED_AXE TWO_HANDED_MACE TWO_HANDED_SPEAR TWO_HANDED_STAFF TWO_HANDED_SWORD "
         "QUIVER SHIELD CATALYST AMULET RING RELIC BOW CROSSBOW IDOL_1x1_ETERRA IDOL_1x1_LAGON "
         "IDOL_2x1 IDOL_1x2 IDOL_3x1 IDOL_1x3 IDOL_4x1 IDOL_1x4 IDOL_2x2 BLESSING "
         "GREATER_LENS ARCTUS_LENS MESEMBRIA_LENS EOS_LENS DYSIS_LENS UNUSED IDOL_ALTAR").split()
SLOTS = {"head": "HELMET", "chest": "BODY_ARMOR", "waist": "BELT", "hands": "GLOVES",
         "feet": "BOOTS", "relic": "RELIC", "amulet": "AMULET", "ring1": "RING",
         "ring2": "RING", "idol_altar": "IDOL_ALTAR"}


def profile_url(value):
    if not isinstance(value, str):
        raise ValueError("角色链接必须是文字。")
    url = urlsplit(value.strip())
    if (url.scheme != "https" or url.netloc not in {"www.lastepochtools.com", "lastepochtools.com"}
            or url.query or url.fragment):
        raise ValueError("请使用 https://www.lastepochtools.com/profile/账号/character/角色 链接。")
    match = re.fullmatch(r"/profile/(?:[a-z]{2}/)?([^/]+)/character/([^/]+)/?", url.path)
    if not match:
        raise ValueError("需要具体角色的profile链接，不支持账号主页、攻略或快照链接。")
    account, character = (unquote(s, errors="strict") for s in match.groups())
    if any(not s or any(ord(c) < 32 or c in "/\\?#" for c in s) for s in (account, character)):
        raise ValueError("角色链接中的账号或角色名不正确。")
    canonical = f"https://www.lastepochtools.com/profile/{quote(account, safe='')}/character/{quote(character, safe='')}"
    return canonical, account, character


def decode_key(key):
    """LETools category-prefixed LZ-String decompressFromEncodedURIComponent."""
    if not isinstance(key, str) or not 2 <= len(key) <= 160:
        raise ValueError("LETools物品／词缀标识格式不正确。")
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$"
    try:
        values = [alphabet.index(c) for c in key[1:].replace(" ", "+")]
    except ValueError:
        raise ValueError("LETools标识含未知字符。") from None
    index, mask = 0, 32

    def bits(count):
        nonlocal index, mask
        result = 0
        for offset in range(count):
            if index >= len(values):
                raise ValueError("LETools压缩标识不完整。")
            result |= bool(values[index] & mask) << offset
            mask >>= 1
            if not mask:
                index += 1
                mask = 32
        return result

    code = bits(2)
    if code == 2:
        return ""
    if code not in (0, 1):
        raise ValueError("LETools压缩标识无效。")
    previous = chr(bits(8 if code == 0 else 16))
    dictionary = {0: "", 1: "", 2: "", 3: previous}
    output = [previous]
    width, enlarge, size = 3, 4, 4
    while len(output) <= 128:
        code = bits(width)
        if code in (0, 1):
            dictionary[size] = chr(bits(8 if code == 0 else 16))
            code = size
            size += 1
            enlarge -= 1
        elif code == 2:
            result = "".join(output)
            if len(result) > 128:
                break
            return result
        if enlarge == 0:
            enlarge = 1 << width
            width += 1
        if code in dictionary:
            current = dictionary[code]
        elif code == size:
            current = previous + previous[0]
        else:
            raise ValueError("LETools压缩字典无效。")
        output.append(current)
        dictionary[size] = previous + current[0]
        size += 1
        enlarge -= 1
        previous = current
        if enlarge == 0:
            enlarge = 1 << width
            width += 1
    raise ValueError("LETools标识过长。")


def append_ids(target, values):
    for value in values:
        if value not in target:
            target.append(value)


def merge_targets(*profiles):
    """Union candidates only within the same type and base scope; retain order."""
    result = empty_profile()
    for profile in profiles:
        validate_profile(profile)
        append_ids(result["uniques"], profile["uniques"])
        for category in ("equipment", "altars", "idols", "bases"):
            for incoming in profile[category]:
                key = (incoming["type"], tuple(sorted(incoming["bases"])),
                       tuple(sorted(incoming.get("pair_bases", incoming["bases"]))))
                group = next((g for g in result[category] if
                              (g["type"], tuple(sorted(g["bases"])),
                               tuple(sorted(g.get("pair_bases", g["bases"])))) == key), None)
                if group is None:
                    result[category].append(deepcopy(incoming))
                else:
                    for field in ("affixes", "corrupted", "enchanted"):
                        if incoming.get(field):
                            append_ids(group.setdefault(field, []), incoming[field])
    for category in ("equipment", "altars", "idols", "bases"):
        for group in result[category]:
            for field in ("corrupted", "enchanted"):
                if not group.get(field):
                    group.pop(field, None)
    validate_profile(result)
    return result


def item_identity(key):
    if isinstance(key, dict):
        tid, base, uid = key.get("type_id"), key.get("base"), key.get("unique_id")
        if (type(tid) is not int or not 0 <= tid < len(TYPES) or type(base) is not int
                or f"{TYPES[tid]}:{base}" not in CATALOG["bases"]):
            raise ValueError(f"未知角色物品／底材编码：{key}。")
        typ = TYPES[tid]
        if uid is not None and (type(uid) is not int or CATALOG["uniques"].get(str(uid), {}).get("type") != typ):
            raise ValueError(f"未知暗金ID或类型不一致：{uid}，请更新词库。")
        return typ, base, uid
    decoded = decode_key(key)
    if not decoded.isascii() or not decoded.isdecimal():
        raise ValueError("LETools物品标识不是数字编码。")
    if key.startswith("U") and len(decoded) == 6:
        base, uid = int(decoded[:3]), int(decoded[3:])
        data = CATALOG["uniques"].get(str(uid))
        if data is None or not data.get("type"):
            raise ValueError(f"未知暗金ID {uid}，请更新词库。")
        return data["type"], base, uid
    if key.startswith("I") and len(decoded) == 10 and decoded[0] == "1":
        tid, base = int(decoded[1:4]), int(decoded[4:7])
        if tid < len(TYPES) and f"{TYPES[tid]}:{base}" in CATALOG["bases"]:
            return TYPES[tid], base, None
    raise ValueError(f"未知物品／底材编码：{key}。")


def extract_character(entry):
    if not isinstance(entry, dict):
        raise ValueError("角色数据必须为对象。")
    url, account, character = profile_url(entry.get("url"))
    provider = entry.get("provider", "LETools")
    if "save" in entry:
        if provider != "Maxroll":
            raise ValueError("未知角色数据来源。")
        data = decode_character(entry["save"], character)
    else:
        data = entry.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("equipment"), dict) or not isinstance(data.get("idols"), list):
        raise ValueError(f"{character}缺少装备或神像数据，请重新读取。")
    if len(data["equipment"]) > 20 or len(data["idols"]) > 25:
        raise ValueError("角色数据的物品数量不正确。")
    targets = empty_profile()
    fixed, unique_idols, records = [], [], []

    def add_item(item, slot):
        if not isinstance(item, dict):
            raise ValueError(f"{character}/{slot}物品数据不正确。")
        if not item.get("id"):
            return
        typ, base, uid = item_identity(item["id"])
        if slot in SLOTS and typ != SLOTS[slot] or slot.startswith("idol-") and (not typ.startswith("IDOL_") or typ == "IDOL_ALTAR"):
            raise ValueError(f"{character}/{slot}物品类型与位置不符。")
        if typ not in MANIFEST["scope_types"] and not typ.startswith("IDOL_"):
            raise ValueError(f"暂不支持物品类型{typ}。")
        pools = {key: [] for key in ("affixes", "corrupted", "enchanted", "fixed")}
        affixes = item.get("affixes", [])
        if not isinstance(affixes, list) or len(affixes) > 12:
            raise ValueError("物品词缀列表不正确。")
        affixes = affixes + [item[key] for key in ("sealedAffix", "primordialAffix", "corruptedAffix") if item.get(key)]
        for affix in affixes:
            if not isinstance(affix, dict):
                raise ValueError("物品词缀数据不正确。")
            key = affix.get("id")
            if type(key) is int:
                aid = key
            else:
                decoded = decode_key(key)
                if not key.startswith("A") or not decoded.isascii() or not decoded.isdecimal():
                    raise ValueError("LETools词缀编码不正确。")
                aid = int(decoded)
            catalog = CATALOG["affixes"].get(str(aid))
            if catalog is None:
                raise ValueError(f"未知词缀ID {aid}，请更新词库；未将其猜成普通词缀。")
            special = catalog["special"]
            field = {0: "affixes", 2: "affixes", 5: "affixes", 4: "enchanted", 6: "corrupted", 7: "fixed"}.get(special)
            if field is None:
                raise ValueError(f"词缀{aid}的特殊类别{special}暂未支持。")
            if typ.startswith("IDOL_") and typ != "IDOL_ALTAR" and field == "affixes" and special not in {0, 5}:
                raise ValueError(f"神像词缀{aid}不属于普通0／5类。")
            append_ids(pools[field], [aid])
        records.append({"slot": slot, "item_key": item["id"], "type": typ, "base": base,
                        "unique_id": uid, **deepcopy(pools)})
        if uid is not None:
            append_ids(targets["uniques"], [uid])
        if pools["fixed"]:
            fixed.append({"slot": slot, "type": typ, "ids": pools.pop("fixed")})
        else:
            pools.pop("fixed")
        if uid is not None and typ.startswith("IDOL_") and typ != "IDOL_ALTAR":
            unique_idols.append({"slot": slot, "unique_id": uid, **pools})
            return
        if typ == "IDOL_ALTAR":
            append_ids(pools["affixes"], pools.pop("corrupted"))
            append_ids(pools["affixes"], pools.pop("enchanted"))
            category, bases = "altars", [base]
        elif typ.startswith("IDOL_"):
            category, bases = "idols", [base]
        else:
            category, bases = "equipment", []
            if uid is None:
                group = next((g for g in targets["bases"] if g["type"] == typ), None)
                if group is None:
                    group = {"type": typ, "bases": [], "preferred_bases": []}
                    targets["bases"].append(group)
                append_ids(group["bases"], [base])
        if any(pools.values()):
            group = {"type": typ, "bases": bases, **{k: v for k, v in pools.items() if v or k == "affixes"}}
            partial = empty_profile()
            partial[category] = [group]
            merged = merge_targets(targets, partial)
            targets.clear()
            targets.update(merged)

    for slot, item in data["equipment"].items():
        if slot not in SLOTS and slot not in {"weapon1", "weapon2"}:
            raise ValueError(f"未知装备位置{slot}。")
        add_item(item, slot)
    for index, item in enumerate(data["idols"]):
        add_item(item, f"idol-{index + 1}")
    if not records:
        raise ValueError(f"{character}没有可读取的装备，未创建空BD。")
    return targets, {"url": url, "account": account, "character": character,
                     **({"provider": provider} if "provider" in entry else {}),
                     **({"api_url": f"https://planners.maxroll.gg/lastepoch/characters/{quote(account, safe='')}/{quote(character, safe='')}"} if provider == "Maxroll" else {}),
                     **({"last_updated": entry["last_updated"]} if "last_updated" in entry else {}),
                     "data_version": entry.get("data_version"), "items": records,
                     "fixed_affix_references": fixed, "unique_idol_references": unique_idols}


def import_profiles(bundle):
    if (not isinstance(bundle, dict) or bundle.get("format") != "letools-profile-bundle" or bundle.get("version") != 1
            or not isinstance(bundle.get("profiles"), list) or not 1 <= len(bundle["profiles"]) <= 12):
        raise ValueError("请读取1–12个角色，或选择已有角色JSON。")
    targets, sources, seen = empty_profile(), [], set()
    for entry in bundle["profiles"]:
        profile, source = extract_character(entry)
        if source["url"] in seen:
            continue
        seen.add(source["url"])
        sources.append(source)
        targets = merge_targets(targets, profile)
    digest = hashlib.sha256(json.dumps(sorted(seen), ensure_ascii=False).encode()).hexdigest()[:16]
    if not isinstance(bundle.get("name", ""), str):
        raise ValueError("个人BD名称必须为文字。")
    name = bundle.get("name", "").strip() or " ＋ ".join(s["character"] for s in sources)
    warnings = ["角色当前配装按部位取并集，包含低阶及传奇后加词缀；角色词缀顺序不代表推荐优先级。",
                "按冻结ID类别分类：普通神像只计0／5类，腐化6、附魔4另存参考；祭坛附加词缀作为实际目标。",
                "暗金固定随机词缀7另存参考；不添加暗金固有属性、技能、祝福或练级目标。"]
    document = {"format": "le-filter-requirements", "version": 1, "id": "profile-union-" + digest,
                "name": name, "stage": "endgame", "targets": targets,
                "source": {"name": (f"角色并集 · {len(sources)}个（{'／'.join(dict.fromkeys(s.get('provider', 'LETools') for s in sources))}）"
                                    if any(s.get("provider") == "Maxroll" for s in sources) else f"LETools · {len(sources)}个角色并集"),
                           "profiles": sources, "warnings": warnings}}
    result = read_document(document)
    result["document"] = document
    return result
