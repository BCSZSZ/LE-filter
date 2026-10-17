"""Finite native-branch enumeration for the proposed natural-drop formulas.

Writes the tracked natural model validation JSON. This validates probability mathematics at
ilvl100 with ideal independent draws; it does not simulate a game client.
"""
from importlib.util import spec_from_file_location, module_from_spec
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "scripts/build_prophecy_probability.py"
MODEL_SHA256 = hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()
HELPER_PATH = ROOT / "scripts/validate_prophecy_probability.py"
spec = spec_from_file_location("independent_prophecy_helper", HELPER_PATH)
helper = module_from_spec(spec)
spec.loader.exec_module(helper)
model = helper.model
TOLERANCE = 3e-12


def explicit_joint_force(states, order, effect, multiplier, t7_multiplier):
    """Return P(E,K) for every input state, enumerating native force branches."""
    rows = np.arange(len(states))
    n = len(order)
    tier7 = np.count_nonzero(states == 7, axis=1)
    tier6plus = np.count_nonzero(states >= 6, axis=1)
    result = np.zeros((len(states), 2, 5))
    remaining = np.ones(len(states))
    for slot in range(n):
        mass = remaining * .7 * (states[:, slot] >= 6)
        result[rows, (tier6plus > 0).astype(int), tier7] += mass
        remaining -= mass
    for picked in range(n):
        mass = remaining / n
        stop = states[:, picked] >= 6
        result[rows[stop], (tier6plus[stop] > 0).astype(int), tier7[stop]] += mass[stop]
        active = rows[~stop]
        target = helper.native_fallback_slot(order, picked, effect)
        previous7 = tier7[active] - (states[active, target] == 7)
        previous6plus = tier6plus[active] - (states[active, target] >= 6)
        for rarity_arm, chance in helper.rare_paths(order[target], .066, .12):
            p7 = min(1., max(0., multiplier * t7_multiplier * chance))
            for new_tier, probability in ((6, 1. - p7), (7, p7)):
                final_e = (previous6plus + (new_tier >= 6) > 0).astype(int)
                final_k = previous7 + (new_tier == 7)
                result[active, final_e, final_k] += mass[active] * rarity_arm * probability
    assert np.max(np.abs(result.sum(axis=(1, 2)) - 1.)) < 1e-13
    return result


def enumerate_natural(pool, effect, n, multiplier, t7_multiplier):
    """Actual ordered identities, all 7^n tiers, no-force and force E/K joint."""
    states = np.asarray(list(product(range(1, 8), repeat=n)), dtype=np.int8)
    k = np.count_nonzero(states == 7, axis=1)
    e = np.any(states >= 6, axis=1).astype(int)
    plain = np.zeros((2, 5))
    forced = np.zeros((2, 5))
    paths = helper.ordered_identities(pool, n)
    for order, p_identity in paths:
        probabilities = np.ones(len(states)) * p_identity
        for slot, definition in enumerate(order):
            probabilities *= helper.natural_distribution(
                definition, n, effect, multiplier, t7_multiplier)[states[:, slot] - 1]
        np.add.at(plain, (e, k), probabilities)
        transition = explicit_joint_force(states, order, effect, multiplier, t7_multiplier)
        forced += np.einsum("s,sek->ek", probabilities, transition)
    assert abs(plain.sum() - 1.) < 1e-12
    assert abs(forced.sum() - 1.) < 1e-12
    assert forced[0].sum() < 1e-13
    return plain, forced, len(paths), len(paths) * len(states)


def moment_plain_and_non_exalted(moments, n, multiplier, t7_multiplier):
    """Independent contraction proposed for no-force K and P(no T6+)."""
    probabilities = np.zeros(5)
    non_exalted = 0.
    for categories, joint_moment in moments.items():
        tiers = [model.tier_polynomials(c, n, multiplier, t7_multiplier)[0]
                 for c in categories]
        non_e_poly = np.asarray(1.)
        for tier in tiers:
            non_e_poly = np.multiply.outer(non_e_poly, tier[:5].sum(axis=0))
        non_exalted += np.sum(non_e_poly * joint_moment)
        for is7 in product((False, True), repeat=n):
            polynomial = np.asarray(1.)
            for tier, selected in zip(tiers, is7):
                factor = tier[6] if selected else np.array([1., 0., 0., 0.]) - tier[6]
                polynomial = np.multiply.outer(polynomial, factor)
            probabilities[sum(is7)] += np.sum(polynomial * joint_moment)
    return probabilities, float(non_exalted)


def final_conditional(counts, p_exalted):
    if p_exalted == 0:
        return None
    result = counts.copy()
    result[0] -= 1. - p_exalted
    return result / p_exalted


def raw_mix(corruption):
    """Nominal native CDF, conditional on not returning unique/set first."""
    power = (.6 * corruption if corruption <= 100 else
             .002 * corruption ** 1.52 + 1.055 * corruption - 47.692955017089844)
    iir = .01 * power
    unique_set_cut = (.00156 + .00730) * (1. + .6 * math.log1p(iir))
    x = .36 * iir
    whole = math.floor(x)
    frac = x - whole

    def cdf(t):
        if t < unique_set_cut:
            return 0.
        return ((t - unique_set_cut) / (1. - unique_set_cut)
                * ((1. - frac) * t ** whole + frac * t ** (whole + 1)))

    cdfs = np.array([0., *[cdf(t) for t in (.13, .35, .84, .93, 1.)]])
    probabilities = np.diff(cdfs)
    assert abs(probabilities.sum() - 1.) < 1e-13
    return probabilities


def main():
    started = time.monotonic()
    checks = []
    mixed_checks = []
    profile_checks = []
    type_checks = []
    maximum = 0.
    identity_paths = 0
    tier_states = 0
    regimes = ((1., 1.), (1.5, 1.), (1.5, 2.))
    for fixture in helper.FIXTURES:
        pool, effect = fixture["pool"], fixture["effect"]
        explicit_by_regime = {}
        for multiplier, q in regimes:
            raw = {}
            for n in range(1, 5):
                plain, forced, paths, evaluations = enumerate_natural(pool, effect, n, multiplier, q)
                identity_paths += paths
                tier_states += evaluations
                moments = model.selection_moments(pool, n)
                plain_formula, non_e_formula = moment_plain_and_non_exalted(moments, n, multiplier, q)
                production_count, production_exalted = model.natural_outcomes(moments, multiplier, q)
                forced_formula = model.integrate(moments, multiplier, q)[0]
                errors = [np.max(np.abs(plain_formula - plain.sum(axis=0))),
                          abs(non_e_formula - plain[0].sum()),
                          np.max(np.abs(production_count - plain.sum(axis=0))),
                          abs(production_exalted - plain[1].sum()),
                          np.max(np.abs(forced_formula - forced.sum(axis=0)))]
                for f in (0., .25, 1.):
                    joint = (1. - f) * plain + f * forced
                    counts = (1. - f) * production_count + f * forced_formula
                    p_e = (1. - f) * production_exalted + f
                    conditional = final_conditional(counts, p_e)
                    errors.append(abs(p_e - joint[1].sum()))
                    errors.append(np.max(np.abs(conditional - joint[1] / joint[1].sum())))
                error = float(max(errors))
                maximum = max(maximum, error)
                assert error < TOLERANCE, (fixture["name"], n, multiplier, q, error)
                raw[n] = {"plain": plain, "forced": forced,
                          "plainFormula": production_count, "forcedFormula": forced_formula,
                          "nonExaltedFormula": 1. - production_exalted}
                checks.append({"fixture": fixture["name"], "n": n, "M": multiplier, "Q": q,
                               "identityPaths": paths, "tierStates": evaluations,
                               "maxError": error, "plainExaltedProbability": float(plain[1].sum()),
                               "productionCountMaxError": float(np.max(np.abs(production_count - plain.sum(axis=0)))),
                               "productionExaltedError": float(abs(production_exalted - plain[1].sum()))})
            explicit_by_regime[(multiplier, q)] = raw
            for corruption in (0, 100, 300, 1000):
                weights = raw_mix(corruption)
                for cof11 in (False, True):
                    direct = np.zeros((2, 5))
                    direct[0, 0] = weights[0]
                    counts = np.zeros(5)
                    counts[0] = weights[0]
                    p_exalted = 0.
                    for n, value in raw.items():
                        f = .25 if cof11 and n >= 3 else 0.
                        direct += weights[n] * ((1. - f) * value["plain"] + f * value["forced"])
                        counts += weights[n] * ((1. - f) * value["plainFormula"] + f * value["forcedFormula"])
                        p_exalted += weights[n] * (1. - (1. - f) * value["nonExaltedFormula"])
                    conditional = final_conditional(counts, p_exalted)
                    error = float(max(abs(p_exalted - direct[1].sum()),
                                      np.max(np.abs(counts - direct.sum(axis=0))),
                                      np.max(np.abs(conditional - direct[1] / direct[1].sum()))))
                    maximum = max(maximum, error)
                    assert error < TOLERANCE
                    assert np.min(conditional) > -1e-12
                    assert abs(conditional.sum() - 1.) < 1e-12
                    mixed_checks.append({"fixture": fixture["name"], "M": multiplier, "Q": q,
                                         "corruption": corruption, "CoF11": cof11,
                                         "maxError": error, "PExalted": p_exalted,
                                         "countDistribution": counts.tolist(),
                                         "conditionalExaltedDistribution": conditional.tolist()})
        # Check the actual production composition, including raw0 and CoF11 mix.
        _, components = model.evaluate_profile({"affixes": pool})
        for rank, rows in components.items():
            assert rows[0] == {"p_T7_count": [1., 0., 0., 0., 0.], "p_exalted": 0.}
            regime = model.NATURAL_REGIMES["9" if rank == "11" else rank]
            for n in range(1, 5):
                explicit = explicit_by_regime[regime][n]
                f = .25 if rank == "11" and n >= 3 else 0.
                joint = (1. - f) * explicit["plain"] + f * explicit["forced"]
                error = float(max(np.max(np.abs(np.array(rows[n]["p_T7_count"]) - joint.sum(axis=0))),
                                  abs(rows[n]["p_exalted"] - joint[1].sum())))
                maximum = max(maximum, error)
                assert error < TOLERANCE
                profile_checks.append({"fixture": fixture["name"], "rank": rank, "n": n, "maxError": error})
    # Reachable mechanism edge, even though a particular fixture's natural mass can be zero.
    order = helper.FIXTURES[1]["pool"][:4]
    state = np.array([[4, 7, 1, 4]], dtype=np.int8)
    edge = explicit_joint_force(state, order, .125, 1.5, 2.)[0]
    assert abs(edge[1, 0] - .049215) < 1e-14
    assert edge[0].sum() == 0.
    assert final_conditional(np.array([1., 0., 0., 0., 0.]), 0.) is None
    # Compare the production CDF/Bayes path with independent initial raw weights
    # and directly reconstructed finite rejection probabilities from frozen inputs.
    snapshot_path = ROOT / "analysis/prophecy-probabilities.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    for player in snapshot["naturalRarity"]["typeSelection"]["players"]:
        gear = player["modes"]["ordinaryRaw0_1_3_4"]
        idols = player["modes"]["ordinaryRaw2"]

        def returned(mode, type_id):
            a = mode["acceptWeightsByTypeID"][type_id]
            total = sum(mode["acceptWeightsByTypeID"])
            tail = (1. - total / 42) ** 1000
            return a / total * (1. - tail) + tail / 42

        for type_id in range(24):
            if type_id == 11:
                continue
            factor = returned(idols, type_id) / returned(gear, type_id)
            for corruption in (0, 100, 300, 1000, 100000):
                expected = raw_mix(corruption)
                expected[2] *= factor
                expected /= expected.sum()
                actual = model.natural_rarity_weights(snapshot["naturalRarity"], corruption,
                                                     player["id"], type_id)
                error = float(np.max(np.abs(expected - actual)))
                maximum = max(maximum, error)
                assert error < TOLERANCE
                type_checks.append({"playerClass": player["id"], "typeID": type_id,
                                    "corruption": corruption, "maxError": error})
    result = {"status": "passed", "scope": "ordinary ilvl100; full identity and 7^n tier/force enumeration, no lenses; ideal independent RNG; not client test",
              "modelSHA256": MODEL_SHA256,
              "productionFunctionsTested": ["natural_outcomes", "integrate", "evaluate_profile naturalComponents"],
              "helperSHA256": hashlib.sha256(HELPER_PATH.read_bytes()).hexdigest(),
              "scriptSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "fixtures": len(helper.FIXTURES), "rawRegimeChecks": len(checks),
              "rawMixedConditionalChecks": len(mixed_checks), "orderedIdentityPaths": identity_paths,
              "productionProfileComponentChecks": len(profile_checks),
              "rawTypeConditionalChecks": len(type_checks),
              "snapshotSHA256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
              "tierStateEvaluations": tier_states, "maximumAbsoluteError": maximum,
              "elapsedSeconds": time.monotonic() - started,
              "forceFallbackOverwriteT7": {"inputTiers": state[0].tolist(),
                                           "P_E_K": edge.tolist(), "forcedExaltedPreserved": True},
              "formulaRequirements": ["raw3/4 f=.25 only if CoF11 and area>=45 and incoming force=false",
                                      "magic suppression applies to natural T6 entry only",
                                      "P(nonExalted) integrates ordered identity correlations",
                                      "no-force state must include any pre-force post-processing",
                                      "zero P(E) returns no conditional result"],
              "checks": checks, "mixedChecks": mixed_checks, "profileComponentChecks": profile_checks,
              "rawTypeChecks": type_checks}
    assert hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest() == MODEL_SHA256, "Production changed during validation; rerun"
    output = ROOT / "analysis/natural-drop-model-validation.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("status", "rawRegimeChecks", "rawMixedConditionalChecks",
                                           "tierStateEvaluations", "maximumAbsoluteError", "elapsedSeconds")}), flush=True)


if __name__ == "__main__":
    main()
