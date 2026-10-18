"""Decode equipped item identities and affix IDs from public character saves.

No rolls, skill trees, blessings or gameplay thresholds are imported. Layout is
checked against ItemData.RebuildID / setValuesFromSerialisation (1.5.2.2) and a
76-item LETools oracle; see docs/PROFILE_IMPORT.md.
"""

CONTAINERS = {2: "head", 3: "chest", 4: "weapon1", 5: "weapon2", 6: "hands",
              7: "waist", 8: "feet", 9: "ring2", 10: "ring1", 11: "amulet",
              12: "relic", 123: "idol_altar"}
# Versions 2 / 3–5 store shorter individual-ID headers. The item region is
# unchanged by the game's upgrade-to-v6 copy; unknown versions fail explicitly.
BASE_OFFSETS = {2: 1, 3: 3, 4: 3, 5: 3, 6: 5}


def decode_item(data):
    if (not isinstance(data, list) or not 10 <= len(data) <= 256
            or any(type(n) is not int or not 0 <= n <= 255 for n in data)):
        raise ValueError("角色物品字节格式不正确。")
    version = data[0]
    if version not in BASE_OFFSETS:
        raise ValueError(f"暂不支持物品序列化版本{version}，本次未导入。")
    base = BASE_OFFSETS[version]
    if len(data) <= base + 8:
        raise ValueError("角色物品数据不完整。")
    rarity = data[base + 2] & 15
    identity = {"type_id": data[base], "base": data[base + 1]}
    if rarity in (7, 8, 9):
        identity["unique_id"] = data[base + 7] * 256 + data[base + 8]
        position = base + 17
        if len(data) <= position:
            raise ValueError("暗金／传奇词缀数据不完整。")
        # Unique/set: high 3 bits = count, low 5 = LP/WW. Legendary: low 3
        # bits = count, higher bits = corruption/LP. Never scan trailing bytes.
        count = data[position] & 7 if rarity == 9 else data[position] >> 5
    elif rarity <= 4:
        position = base + 8
        count = data[position] & 63  # high bits carry sealed/corruption state
    else:
        raise ValueError(f"暂不支持物品稀有度编码{rarity}，本次未导入。")
    if count > 7 or len(data) < position + 1 + count * 3:
        raise ValueError("角色词缀数量或数据长度不正确。")
    affixes = []
    for index in range(count):
        first, second, _roll = data[position + 1 + index * 3:position + 4 + index * 3]
        tier = (first >> 4) + 1
        if tier > 8:
            raise ValueError("角色词缀阶数编码不正确。")
        affixes.append({"id": (first & 15) * 256 + second, "tier": tier})
    return {"id": identity, "affixes": affixes}


def decode_character(save, character):
    if (not isinstance(save, dict) or not isinstance(save.get("characterName"), str)
            or save["characterName"].lower() != character.lower()
            or not isinstance(save.get("savedItems"), list) or len(save["savedItems"]) > 2000):
        raise ValueError(f"{character}角色身份或装备数据不正确。")
    equipment, idols = {}, []
    for item in save["savedItems"]:
        if not isinstance(item, dict) or type(item.get("containerID")) is not int:
            raise ValueError("角色物品位置格式不正确。")
        container = item["containerID"]
        if container not in CONTAINERS and container != 29:
            continue
        decoded = decode_item(item.get("data"))
        if container == 29:
            idols.append(decoded)
        else:
            slot = CONTAINERS[container]
            if slot in equipment:
                raise ValueError(f"角色装备位置{slot}重复，本次未导入。")
            equipment[slot] = decoded
    if len(idols) > 25:
        raise ValueError("角色神像数量不正确。")
    return {"equipment": equipment, "idols": idols}
