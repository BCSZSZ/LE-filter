"""Each BD gets at most one rule per idol shape and target-count tier."""
import unittest
from copy import deepcopy

import engine as e
from browser_runtime import browser_bootstrap
from test_engine import first


class IdolShapeTests(unittest.TestCase):
    def config(self, groups):
        profile = e.empty_profile()
        profile["idols"] = groups
        return {"version": 1, "main_id": "audit", "extra_t7": False, "builds": [
            {"id": "audit", "name": "追心手里剑", "enabled": True,
             "profiles": {"endgame": profile, "leveling": e.empty_leveling()}}]}

    def idol_rows(self, output):
        return [r for r in output["rules"] if r["category"].startswith("神像")]

    def test_reported_57_59_merge_once_in_each_target_count_tier(self):
        config = self.config([
            {"type": "IDOL_1x4", "bases": [4, 9], "affixes": [470, 763]},
            {"type": "IDOL_1x4", "bases": [9], "affixes": [470, 480, 763]},
        ])
        before = deepcopy(config)
        output = e.generate(config)
        rows = self.idol_rows(output)
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["tier"] for r in rows], [3, 2])
        for row in rows:
            self.assertEqual(row["types"], ["IDOL_1x4"])
            self.assertEqual(row["bases"], [4, 9])
            self.assertEqual(row["affixes"], [[470, 480, 763]])
        for base, affixes, tier in ((4, {480: 1}, 2), (9, {470: 1}, 2),
                                    (4, {763: 1, 480: 1}, 3), (9, {763: 1, 470: 1}, 3)):
            self.assertEqual(first(output, "IDOL_1x4", affixes, base=base, rarity="RARE")["tier"], tier)
        self.assertEqual(config, before)

    def test_separate_source_pools_can_supply_the_two_targets_within_one_bd(self):
        output = e.generate(self.config([
            {"type": "IDOL_1x4", "bases": [4], "affixes": [763]},
            {"type": "IDOL_1x4", "bases": [9], "affixes": [470]},
        ]))
        self.assertEqual(len(self.idol_rows(output)), 2)
        row = first(output, "IDOL_1x4", {763: 1, 470: 1}, base=9, rarity="RARE")
        self.assertEqual((row["category"], row["tier"]), ("神像两普通目标", 3))

    def test_different_bds_do_not_combine_targets(self):
        config = self.config([{"type": "IDOL_1x4", "bases": [9], "affixes": [763]}])
        other = deepcopy(config["builds"][0])
        other.update(id="other", name="另一个BD")
        other["profiles"]["endgame"]["idols"][0]["affixes"] = [470]
        config["builds"].append(other)
        output = e.generate(config)
        self.assertFalse(any(r["category"] == "神像两普通目标" for r in self.idol_rows(output)))
        row = first(output, "IDOL_1x4", {763: 1, 470: 1}, base=9, rarity="RARE")
        self.assertEqual((row["tier"], row["role"], row["owners"]), (2, "主", ["追心手里剑"]))

    def test_candidate_and_pair_base_unions_stay_independent(self):
        output = e.generate(self.config([
            {"type": "IDOL_1x4", "bases": [9], "pair_bases": [4, 9], "affixes": [470, 763]},
            {"type": "IDOL_1x4", "bases": [9], "pair_bases": [9], "affixes": [480]},
        ]))
        rows = {r["category"]: r for r in self.idol_rows(output)}
        self.assertEqual(len(self.idol_rows(output)), 2)
        self.assertEqual(rows["神像一普通目标"]["bases"], [9])
        self.assertEqual(rows["神像两普通目标"]["bases"], [4, 9])
        for row in rows.values():
            self.assertEqual(row["affixes"], [[470, 480, 763]])

    def test_empty_target_group_does_not_add_an_unrestricted_scope_or_references(self):
        output = e.generate(self.config([
            {"type": "IDOL_1x4", "bases": [9], "affixes": [470], "enchanted": [894], "corrupted": [1037]},
            {"type": "IDOL_1x4", "bases": [], "affixes": [], "enchanted": [892]},
            {"type": "IDOL_1x3", "bases": [9], "affixes": []},
        ]))
        rows = self.idol_rows(output)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["types"], rows[0]["bases"], rows[0]["affixes"]),
                         (["IDOL_1x4"], [9], [[470]]))

    def test_explicit_unrestricted_scope_wins_over_finite_scopes(self):
        output = e.generate(self.config([
            {"type": "IDOL_1x4", "bases": [9], "affixes": [763]},
            {"type": "IDOL_1x4", "bases": [], "affixes": [470]},
        ]))
        rows = self.idol_rows(output)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["bases"] == [] and r["affixes"] == [[470, 763]] for r in rows))

    def test_only_suffix_targets_do_not_create_an_unmatchable_two_target_layer(self):
        output = e.generate(self.config([
            {"type": "IDOL_1x4", "bases": [4], "affixes": [470]},
            {"type": "IDOL_1x4", "bases": [9], "affixes": [480]},
        ]))
        rows = self.idol_rows(output)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["category"], rows[0]["bases"], rows[0]["affixes"]),
                         ("神像一普通目标", [4, 9], [[470, 480]]))

    def test_missing_shapes_are_omitted_and_frozen_presets_are_not_mutated(self):
        self.assertEqual(self.idol_rows(e.generate(self.config([]))), [])
        original = deepcopy(browser_bootstrap()["config"])
        config = deepcopy(original)
        for build in config["builds"]:
            build["enabled"] = build["id"] == "heartseeker-shuriken-marksman"
        config["main_id"] = "heartseeker-shuriken-marksman"
        output = e.generate(config)
        rows = self.idol_rows(output)
        keys = [(r["category"], tuple(r["types"])) for r in rows]
        self.assertEqual(len(keys), len(set(keys)))
        expected = {g["type"] for b in config["builds"] if b["enabled"]
                    for g in b["profiles"]["endgame"]["idols"] if g["affixes"]}
        self.assertEqual({r["types"][0] for r in rows}, expected)
        self.assertEqual(browser_bootstrap()["config"], original)


if __name__ == "__main__":
    unittest.main()
