"""Game-list labels expose the actual merged scope of each idol target tier."""
import unittest
from copy import deepcopy

import engine as e
from test_engine import first, parsed


class IdolLabelTests(unittest.TestCase):
    def config(self, groups):
        profile = e.empty_profile()
        profile["idols"] = groups
        return {"version": 1, "main_id": "audit", "extra_t7": False, "builds": [
            {"id": "audit", "name": "追心手里剑", "enabled": True,
             "profiles": {"endgame": profile, "leveling": e.empty_leveling()}}]}

    def test_reported_57_59_merge_and_labels_show_the_union_scope(self):
        config = self.config([
            {"type": "IDOL_1x4", "bases": [4, 9], "affixes": [470, 763]},
            {"type": "IDOL_1x4", "bases": [9], "affixes": [470, 480, 763]},
        ])
        before = deepcopy(config)
        output = e.generate(config)
        self.assertEqual(config, before)
        rows = [r for r in output["rules"] if r["category"].startswith("神像")]
        self.assertEqual(len(rows), 2)
        self.assertEqual(len({r["name"] for r in rows}), 2)
        for row in rows:
            self.assertIn("异端巨型暗影神像", row["name"])
            if row["bases"] == [4, 9]:
                self.assertIn("巨型暗影神像、异端巨型暗影神像", row["name"])
            self.assertEqual(parsed(output)[row["number"] - 1].findtext("nameOverride"), row["name"])
        categories = {"神像一普通目标", "神像两普通目标"}
        for base, affixes, tier in ((4, {470: 1}, 2), (9, {480: 1}, 2),
                                    (4, {763: 1, 480: 1}, 3), (9, {763: 1, 480: 1}, 3)):
            row = first(output, "IDOL_1x4", affixes, base=base, rarity="RARE", categories=categories)
            self.assertEqual(row["tier"], tier)
        self.assertEqual(first(output, "IDOL_1x4", {480: 1}, base=4, rarity="RARE",
                               categories=categories)["tier"], 2)

    def test_pair_label_uses_pair_scope_rather_than_candidate_scope(self):
        output = e.generate(self.config([
            {"type": "IDOL_1x4", "bases": [9], "pair_bases": [4, 9], "affixes": [470, 763]},
        ]))
        rows = {r["category"]: r for r in output["rules"] if r["category"].startswith("神像")}
        pair, single = rows["神像两普通目标"], rows["神像一普通目标"]
        self.assertEqual(pair["bases"], [4, 9])
        self.assertIn("巨型暗影神像、异端巨型暗影神像", pair["name"])
        self.assertEqual(single["bases"], [9])
        self.assertTrue(single["name"].endswith("异端巨型暗影神像"))

    def test_unrestricted_scope_is_explicit_in_exported_label(self):
        output = e.generate(self.config([
            {"type": "IDOL_1x4", "bases": [], "affixes": [470]},
        ]))
        row = next(r for r in output["rules"] if r["category"] == "神像一普通目标")
        self.assertIn("巨型神像（底材不限）", row["name"])

    def test_same_base_source_pools_use_one_label_per_tier(self):
        output = e.generate(self.config([
            {"type": "IDOL_1x4", "bases": [9], "affixes": [763, 470]},
            {"type": "IDOL_1x4", "bases": [9], "affixes": [480, 462]},
        ]))
        rows = [r for r in output["rules"] if r["category"].startswith("神像")]
        self.assertEqual(len(rows), 2)
        self.assertEqual(len({r["name"] for r in rows}), 2)
        for row in rows:
            self.assertEqual(row["affixes"], [[462, 470, 480, 763]])
        mixed = first(output, "IDOL_1x4", {763: 1, 480: 1}, base=9, rarity="RARE",
                      categories={"神像一普通目标", "神像两普通目标"})
        self.assertEqual(mixed["tier"], 3)


if __name__ == "__main__":
    unittest.main()
