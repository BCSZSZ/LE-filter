"""Save decoder boundaries and an independent LETools oracle for all 76 items."""
from copy import deepcopy
import json
import unittest

from engine import ROOT
from character_save import decode_item, decode_character
from letools import extract_character, import_profiles
from profile_proxy import compact_character


class CharacterSaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT / "sources/builds/maxroll-character-api-2026-10-18.json").read_text(encoding="utf-8"))["responses"]
        cls.oracle = json.loads((ROOT / "sources/builds/letools-character-api-2026-10-18.json").read_text(encoding="utf-8"))["responses"]

    def test_all_76_identities_and_classified_affix_pools_equal_independent_api(self):
        count = 0
        for row, oracle in zip(self.rows, self.oracle):
            _, actual = extract_character(compact_character(row["response"], row["url"]))
            _, expected = extract_character({"url": oracle["url"], "data": oracle["response"]["buildInfo"]["data"]})
            byslot = {r["slot"]: r for r in expected["items"]}
            for item in actual["items"]:
                for key in ("type", "base", "unique_id", "affixes", "corrupted", "enchanted", "fixed"):
                    a, b = item[key], byslot[item["slot"]][key]
                    self.assertEqual(sorted(a) if isinstance(a, list) else a,
                                     sorted(b) if isinstance(b, list) else b, (row["url"], item["slot"], key))
                count += 1
        self.assertEqual(count, 76)

    def test_count_flags_dont_read_trailing_roll_or_weaver_payload(self):
        data = self.rows[0]["response"]["savedItems"][0]["data"]
        expected = decode_item(data)
        self.assertEqual([a["id"] for a in expected["affixes"]], [611, 52, 13, 503])
        # A valid-looking affix in the unrelated suffix must never be imported.
        self.assertEqual(decode_item(data[:35] + [0x60, 1, 255] * 4), expected)
        altar = next(x["data"] for x in self.rows[0]["response"]["savedItems"] if x["containerID"] == 123)
        self.assertEqual(len(decode_item(altar)["affixes"]), 4)  # 0x45 = four ordinary plus one corrupted
        self.assertIn("corruptedAffix", decode_item(altar))
        ordinary = [6, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0x81, 0x70, 52, 0]
        self.assertEqual(decode_item(ordinary)["sealedAffix"], {"id": 52, "tier": 8})
        unique = data[:23] + [0x60, 52, 255]
        unique[7], unique[22] = 7, 0x24  # one affix + 4 LP; count is HIGH bits
        self.assertEqual(decode_item(unique)["affixes"], [{"id": 52, "tier": 7}])

    def test_old_headers_have_the_same_target_region_and_unknown_versions_fail(self):
        current = self.rows[0]["response"]["savedItems"][0]["data"]
        for version, prefix in ((2, [2]), (3, [3, 0, 0]), (4, [4, 0, 0]), (5, [5, 0, 0])):
            self.assertEqual(decode_item(prefix + current[5:]), decode_item(current))
        for data in ([7] + current[1:], current[:22], current[:23], [True] + current[1:]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                decode_item(data)

    def test_duplicate_slots_mismatched_identity_and_unknown_ids_fail_entire_import(self):
        good = compact_character(self.rows[0]["response"], self.rows[0]["url"])
        for kind in ("duplicate", "identity", "unknown", "version"):
            bad = deepcopy(good)
            if kind == "duplicate":
                bad["save"]["savedItems"].append(deepcopy(bad["save"]["savedItems"][0]))
            elif kind == "identity":
                bad["save"]["characterName"] = "wrong"
            elif kind == "unknown":
                bad["save"]["savedItems"][0]["data"][23:26] = [0x6F, 255, 255]
            else:
                bad["save"]["savedItems"][0]["data"][0] = 99
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                import_profiles({"format": "letools-profile-bundle", "version": 1, "profiles": [good, bad]})

    def test_inventory_blessings_and_other_save_state_are_excluded(self):
        save = deepcopy(self.rows[0]["response"])
        expected = decode_character(save, save["characterName"])
        save["savedItems"] += [{"containerID": x, "data": []} for x in (0, 1, 33, 91, 93)]
        self.assertEqual(decode_character(save, save["characterName"]), expected)

    def test_legendary_corruption_slot_is_separate_from_regular_slams(self):
        gloves = next(x["data"] for x in self.rows[-1]["response"]["savedItems"] if x["containerID"] == 6)
        decoded = decode_item(gloves)
        self.assertEqual(decoded["affixes"], [{"id": 88, "tier": 7}])
        self.assertEqual(decoded["corruptedAffix"], {"id": 503, "tier": 5})
        # The same high bit encodes remaining WW on uncorrupted legendaries.
        uncorrupted = list(gloves)
        uncorrupted[8] &= ~0x10
        self.assertEqual(decode_item(uncorrupted)["affixes"], [{"id": 88, "tier": 7}, {"id": 503, "tier": 5}])
        self.assertNotIn("corruptedAffix", decode_item(uncorrupted))

    def test_ordinary_sealed_and_corrupted_slots_precede_regular_affixes(self):
        raw = [6, 0, 0, 0, 0, 0, 2, 3, 16, 0, 0, 0, 0, 0xC3,
               0x30, 52, 255, 0x61, 247, 255, 0x60, 88, 255]
        decoded = decode_item(raw)
        self.assertEqual(decoded["sealedAffix"], {"id": 52, "tier": 4})
        self.assertEqual(decoded["corruptedAffix"], {"id": 503, "tier": 7})
        self.assertEqual(decoded["affixes"], [{"id": 88, "tier": 7}])
        with self.assertRaisesRegex(ValueError, "词缀槽位"):
            decode_item(raw[:13] + [0xC1] + raw[14:17])
