"""Check the frozen selector data and its independent probability models."""
import hashlib
import json
import unittest
from collections import Counter

import engine
from browser_runtime import browser_bootstrap
from scripts.build_unique_drop_catalog import (
    CLASSES, CURIOSITY_EXPONENT, INPUT, build, independent_reward_scenarios, prophecy_distribution,
    reference_display, reroll_distribution, single_reward_probability,
)


class UniqueDropMathTests(unittest.TestCase):
    def test_fixed_display_chooses_highest_tier_host_upper_rate(self):
        row = {"kind": "boss", "primordial": False, "cocooned": False, "locations": [{"kind": "boss", "name": "Boss", "probabilityText": "0%–100%", "scenarios": [
            {"tier": 1, "hostOnly": True, "maximumProbability": 1.},
            {"tier": 4, "hostOnly": False, "maximumProbability": .9},
            {"tier": 4, "hostOnly": True, "maximumProbability": .3}]}]}
        display = reference_display(row)
        self.assertEqual(display["source"], "Boss")
        self.assertEqual(display["probability"], .3)
        self.assertEqual(display["probabilityText"], "30%")

    def test_finite_rerolls_match_probability_tree(self):
        rejected = [.2, .7, 1.]
        expected = [0.] * len(rejected)

        def visit(mass, remaining):
            for index, rejection in enumerate(rejected):
                branch = mass / len(rejected)
                if not remaining:
                    expected[index] += branch
                else:
                    expected[index] += branch * (1 - rejection)
                    visit(branch * rejection, remaining - 1)

        visit(1., 3)
        for actual, probability in zip(reroll_distribution(rejected, 3), expected):
            self.assertAlmostEqual(actual, probability, places=14)
        self.assertAlmostEqual(sum(expected), 1., places=14)

    def test_reroll_limits(self):
        self.assertEqual(reroll_distribution([]), [])
        self.assertEqual(reroll_distribution([1., 1.]), [.5, .5])
        self.assertEqual(reroll_distribution([0., .9], 0), [.5, .5])
        self.assertAlmostEqual(reroll_distribution([0., 1.])[0], 1., places=14)
        for invalid in ([-.1], [1.1]):
            with self.assertRaises(ValueError):
                reroll_distribution(invalid)

    def test_curiosity_compresses_all_pool_weights_before_finite_rerolls(self):
        # sqrt([1, .25]) gives acceptance [1, .5]. Enumerating two rejection
        # rounds then one forced draw gives these exact probabilities.
        self.assertEqual(reroll_distribution([0., .75], 2, weight_exponent=.5), [.65625, .34375])
        self.assertEqual(reroll_distribution([1., 1.], weight_exponent=CURIOSITY_EXPONENT), [.5, .5])
        with self.assertRaises(ValueError):
            reroll_distribution([.5], weight_exponent=0)

    def test_class_bias_includes_neutral_items_and_falls_back_when_empty(self):
        pool = [{"uniqueID": uid, "rerollChance": 0.,
                 "subTypeRequirements": [{"classRequirement": mask}]}
                for uid, mask in ((1, 4), (2, 8), (3, 0))]
        actual = prophecy_distribution(pool, 4, compatibility_chance=.8)
        self.assertAlmostEqual(actual[1], .2 / 3 + .8 / 2)
        self.assertAlmostEqual(actual[2], .2 / 3)
        self.assertAlmostEqual(actual[3], actual[1])
        fallback = prophecy_distribution(pool[:2], 2)
        self.assertEqual(fallback, {1: .5, 2: .5})

    def test_boss_probability_is_per_independent_reward(self):
        # Extra draws change reward counts, not the reported single-draw rate.
        self.assertAlmostEqual(single_reward_probability(2.5, 2, 5), .4)
        self.assertAlmostEqual(single_reward_probability(3, 2, 5), .4)
        self.assertAlmostEqual(single_reward_probability(.1, 1, 4), .025)
        self.assertEqual(single_reward_probability(1, 1, 1), 1.)
        self.assertEqual(single_reward_probability(0, 1, 1), 0.)

    def test_separate_rewards_keep_their_rates_and_equal_duplicates_share_display(self):
        rates = [{"probability": .1, "hostOnly": True, "sourceGroupIndex": "first"},
                 {"probability": .02, "hostOnly": False, "sourceGroupIndex": "everyone"},
                 {"probability": .1, "hostOnly": True, "sourceGroupIndex": "repeat"}]
        scenarios = independent_reward_scenarios(rates)
        self.assertEqual(len(scenarios), 2)
        host = next(s for s in scenarios if s["hostOnly"])
        self.assertEqual(host["probability"], .1)
        self.assertEqual(host["sourceGroups"], ["first", "repeat"])
        self.assertEqual(next(s for s in scenarios if not s["hostOnly"])["probability"], .02)


class UniqueDropSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((engine.ROOT / "sources/unique-drop-catalog.json").read_text(encoding="utf-8"))
        cls.inputs = json.loads(INPUT.read_text(encoding="utf-8"))
        cls.catalog = json.loads((engine.ROOT / "sources/tool-catalog.json").read_text(encoding="utf-8"))

    def test_complete_attributed_and_reproducible_snapshot(self):
        self.assertEqual(self.snapshot, build())
        self.assertEqual(set(self.snapshot["items"]), set(self.catalog["uniques"]))
        self.assertEqual(len(self.snapshot["items"]), 489)
        self.assertEqual(self.snapshot["gameVersion"], self.inputs["gameVersion"])
        self.assertEqual(self.snapshot["sources"]["frozenInput"]["sha256"],
                         hashlib.sha256(INPUT.read_bytes()).hexdigest())
        self.assertFalse(self.snapshot["summary"]["gameExecutionTested"])
        for row in self.snapshot["items"].values():
            expected = {"kind", "source", "probability", "probabilityText"}
            if "curiosityProbability" in row["display"]:
                expected |= {"curiosityProbability", "curiosityProbabilityText"}
            self.assertEqual(set(row["display"]), expected)
            self.assertTrue(row["display"]["source"])
            self.assertTrue(row["display"]["probabilityText"])
            self.assertIn(row["kind"], {"world", "boss", "special", "legacy"})
            self.assertTrue(row["locations"])
            self.assertTrue(row["sourceUrl"].startswith("https://"))
            if "iconUrl" in row:
                self.assertTrue(row["iconUrl"].startswith("https://"))
            for location in row["locations"]:
                self.assertTrue(location["name"])
                self.assertTrue(location["probabilityText"])
                self.assertTrue(location["url"].startswith("https://"))
                for rate in location.get("rates", []):
                    if "probability" in rate:
                        self.assertTrue(0 <= rate["probability"] <= 1)

    def test_world_prophecy_pools_normalize_by_class_and_idol_type_selection(self):
        items = self.snapshot["items"]
        idol_totals = {klass: 0. for klass in CLASSES}
        occurrences = Counter(self.inputs["uniqueIdolBaseTypeOccurrences"])
        for base, pool in self.snapshot["prophecyPools"].items():
            base = int(base)
            for uid in pool:
                self.assertFalse(items[str(uid)]["set"])
                self.assertEqual(set(items[str(uid)]["prophecyByClass"]), set(CLASSES))
            for klass in CLASSES:
                probability = sum(items[str(uid)]["prophecyByClass"][klass] for uid in pool)
                expected = occurrences[base] / sum(occurrences.values()) if 25 <= base <= 33 else 1.
                self.assertAlmostEqual(probability, expected, places=12)
                if 25 <= base <= 33:
                    idol_totals[klass] += probability
        for probability in idol_totals.values():
            self.assertAlmostEqual(probability, 1., places=12)

    def test_sets_bosses_and_legacy_do_not_gain_unique_prophecy_chance(self):
        items = self.snapshot["items"]
        for row in items.values():
            if row["kind"] == "world" and row["set"]:
                self.assertEqual(row["prophecyProbability"], 0)
                self.assertNotIn("prophecyByClass", row)
            elif row["kind"] != "world":
                self.assertIsNone(row["prophecyProbability"])
                self.assertNotIn("prophecyByClass", row)
        for uid in (46, 69, 248, 343):
            self.assertEqual(items[str(uid)]["kind"], "legacy")
        self.assertEqual(items["1"]["kind"], "special")
        self.assertTrue(any("100%" in loc["probabilityText"] for loc in items["1"]["locations"]))
        self.assertTrue(any("任务" in loc["name"] for loc in items["130"]["locations"]))
        self.assertTrue(any("T1" in condition for loc in items["253"]["locations"]
                            for condition in loc["conditions"]))

    def test_runtime_attaches_display_data_without_changing_filter_catalog(self):
        boot = browser_bootstrap()
        self.assertEqual(boot["catalog"]["unique_drops"], self.snapshot)
        self.assertEqual({key: value for key, value in boot["catalog"].items() if key != "unique_drops"},
                         engine.bootstrap()["catalog"])

    def test_fixed_reference_uses_unbiased_pool_and_one_boss_rate(self):
        items = self.snapshot["items"]
        for pool in self.snapshot["prophecyPools"].values():
            native = {i["uniqueID"]: i for i in self.inputs["uniques"]}
            base = native[pool[0]]["baseType"]
            factor = self.inputs["uniqueIdolBaseTypeOccurrences"].count(base) / 7 if 25 <= base <= 33 else 1
            total_weight = sum(1 - native[uid]["rerollChance"] for uid in pool)
            for uid in pool:
                # All current pools have a negligible 60-rejection tail.
                expected = factor * (1 - native[uid]["rerollChance"]) / total_weight
                self.assertAlmostEqual(items[str(uid)]["display"]["probability"], expected, places=10)
        self.assertEqual(items["355"]["display"]["probability"], .1)
        self.assertAlmostEqual(items["238"]["display"]["probability"], 10 / 27)
        self.assertEqual(items["253"]["display"]["probability"], .45)
        self.assertEqual(items["153"]["display"]["probability"], .45)

    def test_curiosity_covers_every_eligible_positive_reroll_and_matches_independent_examples(self):
        native = {str(i["uniqueID"]): i for i in self.inputs["uniques"]}
        eligible = {uid for uid, row in self.snapshot["items"].items()
                    if row["kind"] == "world" and not row["set"] and native[uid]["rerollChance"] > 0}
        actual = {uid for uid, row in self.snapshot["items"].items() if "curiosityProbability" in row["display"]}
        self.assertEqual(actual, eligible)
        self.assertEqual(len(actual), 100)
        for pool in self.snapshot["prophecyPools"].values():
            base = native[str(pool[0])]["baseType"]
            factor = self.inputs["uniqueIdolBaseTypeOccurrences"].count(base) / 7 if 25 <= base <= 33 else 1
            weights = {uid: (1 - native[str(uid)]["rerollChance"]) ** CURIOSITY_EXPONENT for uid in pool}
            for uid in pool:
                if str(uid) in eligible:
                    expected = factor * weights[uid] / sum(weights.values())
                    self.assertAlmostEqual(self.snapshot["items"][str(uid)]["display"]["curiosityProbability"], expected, places=12)
        death = self.snapshot["items"]["476"]["display"]
        self.assertAlmostEqual(death["probability"], .00006848757830072423, places=15)
        self.assertAlmostEqual(death["curiosityProbability"], .00025947122102598636, places=15)
        self.assertEqual(death["curiosityProbabilityText"], "0.026%")
        self.assertAlmostEqual(self.snapshot["items"]["277"]["display"]["curiosityProbability"], .003516431526165029, places=15)
        for uid in ("246", "485"):
            display = self.snapshot["items"][uid]["display"]
            self.assertAlmostEqual(display["curiosityProbability"], display["probability"], places=15)
        self.assertIn("暂未计算", self.snapshot["items"]["449"]["display"]["probabilityText"])

    def test_native_boss_and_echo_examples_use_single_reward_rates(self):
        items = self.snapshot["items"]

        def location(uid, suffix):
            return next(loc for loc in items[str(uid)]["locations"] if loc["url"].endswith(suffix))

        aberroth = location(355, "/Aterroth")["scenarios"]
        self.assertEqual({s["hostOnly"]: s["probability"] for s in aberroth}, {True: .1, False: .02})
        uber = location(358, "/UberAterroth")["scenarios"]
        self.assertEqual(len(uber), 1)
        self.assertAlmostEqual(uber[0]["probability"], 20 / 42)
        self.assertEqual(len(uber[0]["sourceGroups"]), 2)
        brink = location(344, "/the_fading_brink")["scenarios"]
        self.assertEqual(len(brink), 1)
        self.assertEqual(brink[0]["probability"], .15)
        self.assertEqual(brink[0]["maximumProbability"], .55)
        self.assertEqual(len(brink[0]["sourceGroups"]), 10)
        julra = next(loc for loc in items["238"]["locations"] if loc["kind"] == "boss")
        self.assertEqual([s["tier"] for s in julra["scenarios"]], [1, 2, 3, 4])
        for scenario, expected in zip(julra["scenarios"], [1., .5, 10 / 24, 10 / 27]):
            self.assertAlmostEqual(scenario["probability"], expected)


if __name__ == "__main__":
    unittest.main()
