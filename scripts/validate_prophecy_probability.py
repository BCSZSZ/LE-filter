"""Independent finite enumeration; does not reuse production transition kernels.

Run with the bundled Python (NumPy is available there). Only the requested
validation JSON is written. This is a probability-model check, not game play.
"""
from collections import defaultdict
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "scripts/build_prophecy_probability.py"
OUTPUT = ROOT / "analysis/prophecy-model-validation.json"
spec = importlib.util.spec_from_file_location("prophecy_under_test", MODEL)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
LENSES = ("none", "quality", "origin", "finality")


def normal_t6_allowed(a, effect):
    return a["t6Compatibility"] == 0 or (
        a["t6Compatibility"] == 2
        and effect <= a["maximumAffixEffectModifierForT6"])


def affix(i, typ, weight, compatibility=0, maximum=0.0, effect=.125):
    result = {"id": i, "type": typ, "weight": weight,
              "t6Compatibility": compatibility,
              "maximumAffixEffectModifierForT6": maximum}
    result["naturalT6Eligible"] = normal_t6_allowed(result, effect)
    return result


FIXTURES = [
    {"name": "normal_distinct_weights_4", "effect": .125, "pool": [
        affix(1, 0, 1.), affix(2, 0, .37),
        affix(3, 1, .82), affix(4, 1, .13)]},
    {"name": "allowed_and_blocked_maximum_with_normal_6", "effect": .125,
     "pool": [affix(1, 0, .9, 2, .25), affix(2, 1, .1),
              affix(3, 0, .7, 2, .0), affix(4, 1, .5),
              affix(5, 0, .5), affix(6, 1, .2, 2, .25)]},
    {"name": "maximum_and_incompatible_without_normal_4", "effect": .125,
     "pool": [affix(1, 0, .7, 2, .25), affix(2, 0, .31, 2, .0),
              affix(3, 1, .44, 2, .25), affix(4, 1, .11, 1)]},
    {"name": "same_weight_distinct_ids_5", "effect": .125,
     "pool": [affix(1, 0, 1.), affix(2, 0, 1.),
              affix(3, 0, .5, 2, .0), affix(4, 1, .25),
              affix(5, 1, .25, 2, .25)]},
]


def ordered_identities(pool, n):
    """Enumerate each actual ID path: weighted, no replacement, max two/side."""
    paths = []

    def visit(order, probability):
        if len(order) == n:
            paths.append((order, probability))
            return
        used = {a["id"] for a in order}
        counts = [sum(a["type"] == typ for a in order) for typ in (0, 1)]
        choices = [a for a in pool if a["id"] not in used
                   and counts[a["type"]] < 2]
        denominator = sum(a["weight"] for a in choices)
        assert denominator > 0
        for chosen in choices:
            visit((*order, chosen), probability * chosen["weight"] / denominator)

    visit((), 1.)
    assert abs(sum(p for _, p in paths) - 1.) < 1e-12
    return paths


def rare_paths(a, ordinary, higher):
    r = min(1., max(0., 1. - a["weight"]))
    return ((1. - r, ordinary), (r, higher))


def natural_distribution(a, n, effect, multiplier, t7_multiplier):
    """Explicit base-tier, magic-prevention, rarity-arm and upgrade branches."""
    result = np.zeros(7)
    result[:4] = (.16, .28, .24, .18)
    if not normal_t6_allowed(a, effect):
        result[4] = .14
        return result
    magic_block = .95 if n < 3 else 0.
    result[4] += .14 * magic_block
    for arm6, chance6 in rare_paths(a, .045, .096):
        p6 = min(1., max(0., multiplier * chance6))
        active = .14 * (1. - magic_block) * arm6
        result[4] += active * (1. - p6)
        for arm7, chance7 in rare_paths(a, .066, .120):
            p7 = min(1., max(0., multiplier * t7_multiplier * chance7))
            result[5] += active * p6 * arm7 * (1. - p7)
            result[6] += active * p6 * arm7 * p7
    assert abs(result.sum() - 1.) < 1e-14
    return result


@lru_cache(maxsize=32)
def lens_branches(types):
    """All 7^n original states; every lens branch retains the identity order."""
    n = len(types)
    states = np.asarray(list(product(range(1, 8), repeat=n)), dtype=np.int8)
    branches = [states]
    for slot in range(n):
        for delta in (1, 2, 3):
            changed = states.copy()
            changed[:, slot] = np.minimum(7, changed[:, slot] + delta)
            branches.append(changed)
    post = np.stack(branches)
    probabilities = np.zeros((4, len(branches), len(states)))
    probabilities[0, 0] = 1.
    choose_weights = {1: .01, 2: .05, 3: .1, 4: .5, 5: 1., 6: 2., 7: 0.}
    for li, lens in enumerate(LENSES[1:], 1):
        side = None if lens == "quality" else 0 if lens == "origin" else 1
        weights = np.array([[choose_weights[int(t)]
                             if side is None or types[j] == side else 0.
                             for j, t in enumerate(state)] for state in states])
        total = weights.sum(axis=1)
        probabilities[li, 0] = np.where(total > 0, .8, 1.)
        for slot in range(n):
            selection = np.divide(weights[:, slot], total,
                                  out=np.zeros(len(states)), where=total > 0)
            for delta_index, increase_probability in enumerate((2/9, 1/3, 4/9)):
                probabilities[li, 1 + 3 * slot + delta_index] = (
                    .2 * selection * increase_probability)
    assert np.max(np.abs(probabilities.sum(axis=1) - 1.)) < 1e-14
    return states, post, probabilities


def native_fallback_slot(order, picked, effect):
    """Follow native registers, including the original-definition second arm."""
    original = order[picked]
    incompatible = original["t6Compatibility"] == 1 or (
        original["t6Compatibility"] == 2
        and effect > original["maximumAffixEffectModifierForT6"])
    if not incompatible:
        return picked
    for candidate, definition in enumerate(order):
        if candidate == picked:
            continue
        if definition["t6Compatibility"] == 0 or (
            original["t6Compatibility"] == 2
            and original["maximumAffixEffectModifierForT6"] >= effect):
            return candidate
    return picked


def explicit_force(states, order, effect, multiplier, t7_multiplier):
    """Enumerate stop positions, initial uniform pick, then both rarity arms."""
    size, n = states.shape
    out = np.zeros((size, 5))
    count = np.count_nonzero(states == 7, axis=1)
    rows = np.arange(size)
    remaining = np.ones(size)
    # Each possible earliest successful 70% roll is an explicit stop branch.
    for slot in range(n):
        stop = remaining * .7 * (states[:, slot] >= 6)
        out[rows, count] += stop
        remaining -= stop
    for picked in range(n):
        selected_mass = remaining / n
        already_exalted = states[:, picked] >= 6
        keep = rows[already_exalted]
        out[keep, count[already_exalted]] += selected_mass[already_exalted]
        active = rows[~already_exalted]
        target = native_fallback_slot(order, picked, effect)
        # This subtracts an existing T7 if first Normal is an already-T7 slot.
        before = count[active] - (states[active, target] == 7)
        for arm, chance in rare_paths(order[target], .066, .120):
            p7 = min(1., max(0., multiplier * t7_multiplier * chance))
            mass = selected_mass[active] * arm
            out[active, before] += mass * (1. - p7)
            out[active, before + 1] += mass * p7
    assert np.max(np.abs(out.sum(axis=1) - 1.)) < 1e-13
    return out


def explicit_all_stages(paths, n, effect, multiplier, t7_multiplier):
    answer = np.zeros((4, 5))
    state_evaluations = 0
    for order, identity_probability in paths:
        states, post, lens_probabilities = lens_branches(tuple(a["type"] for a in order))
        p_tiers = np.ones(len(states))
        for j, a in enumerate(order):
            p_tiers *= natural_distribution(a, n, effect, multiplier, t7_multiplier)[states[:, j] - 1]
        forced = explicit_force(post.reshape((-1, n)), order, effect,
                                multiplier, t7_multiplier).reshape((len(post), len(states), 5))
        for li in range(4):
            branch_mass = lens_probabilities[li] * p_tiers[None, :]
            answer[li] += identity_probability * np.einsum("bs,bsc->c", branch_mass, forced)
        state_evaluations += len(states)
    assert np.max(np.abs(answer.sum(axis=1) - 1.)) < 1e-12
    return answer, state_evaluations


def explicit_moments(paths, pool, n):
    result = defaultdict(lambda: np.zeros((4,) * n))
    has_blocked = any(not a["naturalT6Eligible"] for a in pool)
    for order, probability in paths:
        categories = tuple((a["type"], (0 if a["t6Compatibility"] == 0 else
                           1 if a["naturalT6Eligible"] else 2)
                           if has_blocked else 0) for a in order)
        tensor = np.asarray(probability)
        for a in order:
            r = min(1., max(0., 1. - a["weight"]))
            tensor = np.multiply.outer(tensor, np.array([1., r, r*r, r*r*r]))
        result[categories] += tensor
    return result


def input_audit():
    source_path = ROOT / "sources/t7-equipment-pools.json"
    source = json.loads(source_path.read_text(encoding="utf-8-sig"))
    native_path = ROOT / ".cache/t7-mining-assets/MasterAffixesList.json"
    native = json.loads(native_path.read_text(encoding="utf-8-sig")) if native_path.exists() else None
    native_by_id = ({a["affixId"]: a for a in
                     native["data"]["singleAffixes"] + native["data"]["multiAffixes"]}
                    if native else None)
    for profile in source["profiles"]:
        pool = profile["affixes"]
        assert len({a["id"] for a in pool}) == len(pool)
        assert all(a["type"] in (0, 1) and 0 < a["weight"] <= 1.
                   and a["t6Compatibility"] in (0, 1, 2) for a in pool)
        for a in pool:
            assert a["naturalT6Eligible"] == normal_t6_allowed(a, profile["affixEffectModifier"])
            if native_by_id is None:
                continue
            definition = native_by_id[a["id"]]
            assert a["t6Compatibility"] == definition["t6Compatibility"]
            assert a["type"] == definition["type"]
            assert a["naturalT6Eligible"] == normal_t6_allowed(
                definition, profile["affixEffectModifier"])
            overrides = [o for o in definition["specificRerollChances"]
                         if o["equipmentType"] == profile["typeID"]]
            weight = overrides[0]["weighting"] if overrides else definition["weighting"]
            assert abs(a["weight"] - weight) < 1e-12
        assert all(sum(a["type"] == typ for a in pool) >= 2 for typ in (0, 1))
    return {"path": "sources/t7-equipment-pools.json", "profilesAudited": len(source["profiles"]),
            "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
            "nativeDefinitionsPath": ".cache/t7-mining-assets/MasterAffixesList.json",
            "nativeDefinitionsSHA256": hashlib.sha256(native_path.read_bytes()).hexdigest() if native else None,
            "checks": ["unique IDs", "two selectable identities per affix type", "weight bounds",
                       "weight/default or per-type override equals native asset",
                       "type and T6 compatibility equal native asset",
                       "naturalT6Eligible recomputed from native Maximum threshold"],
            "status": "passed", "nativeAssetAuditPerformed": native is not None}


def main():
    started = time.monotonic()
    checks = []
    maximum = 0.
    moment_maximum = 0.
    identity_order_count = 0
    original_state_evaluations = 0
    for fixture in FIXTURES:
        pool, effect = fixture["pool"], fixture["effect"]
        for n in range(1, 5):
            paths = ordered_identities(pool, n)
            identity_order_count += len(paths)
            moments = model.selection_moments(pool, n)
            independent = explicit_moments(paths, pool, n)
            assert set(moments) == set(independent)
            moment_error = max(np.max(np.abs(moments[k] - independent[k])) for k in moments)
            moment_maximum = max(moment_maximum, float(moment_error))
            assert moment_error < 2e-12
            for multiplier, t7_multiplier in ((1.5, 1), (1.5, 2)):
                actual, evaluations = explicit_all_stages(paths, n, effect,
                                                        multiplier, t7_multiplier)
                expected = model.integrate(moments, multiplier, t7_multiplier)
                error = float(np.max(np.abs(actual - expected)))
                maximum = max(maximum, error)
                original_state_evaluations += evaluations
                checks.append({"fixture": fixture["name"], "poolSize": len(pool), "affixCount": n,
                               "multiplier": multiplier, "t7Multiplier": t7_multiplier,
                               "orderedIdentities": len(paths), "originalTierStatesPerIdentity": 7**n,
                               "maxAbsoluteDistributionError": error,
                               "maxJointMomentError": float(moment_error),
                               "explicitProbabilities": {lens: row.tolist() for lens, row in zip(LENSES, actual)}})
                print(f"{fixture['name']} n={n} M={multiplier} Q={t7_multiplier}: {error:.3g}", flush=True)
                assert error < 2e-12
    edge_order = FIXTURES[1]["pool"][:4]
    edge_state = np.asarray([[4, 7, 1, 4]], dtype=np.int8)
    edge = explicit_force(edge_state, edge_order, .125, 1.5, 2)[0]
    assert native_fallback_slot(edge_order, 2, .125) == 1
    assert abs(edge[0] - .049215) < 1e-14
    result = {"status": "passed", "scope": "independent finite identity/tier/lens/force enumeration; not client sampling",
              "modelPath": "scripts/build_prophecy_probability.py",
              "modelSHA256": hashlib.sha256(MODEL.read_bytes()).hexdigest(),
              "validationScriptSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "nativeMechanismSources": ["docs/T7_LENS_DATAMINING.md", "docs/T7_EQUIPMENT_POOLS.md"],
              "counts": {"fixtures": len(FIXTURES), "comparisonRuns": len(checks),
                         "lensDistributionsCompared": 4 * len(checks),
                         "orderedIdentityPathsBeforeRegimeExpansion": identity_order_count,
                         "originalTierStateEvaluations": original_state_evaluations},
              "maximumAbsoluteDistributionError": maximum, "maximumJointMomentError": moment_maximum,
              "momentIntegrationJustification": {
                  "naturalTierMaximumDegreePerIdentity": 2,
                  "forceExtraDegreeInAtMostOneIdentity": 1,
                  "retainedDegreesPerIdentity": [0, 1, 2, 3],
                  "selectionCorrelation": "Full ordered joint moments; not products of marginal moments",
                  "compatibilityAndFirstNormal": "Condition on ordered type/Normal/allowed-Maximum/blocked categories",
                  "lensIdentityDependence": "Lens weights and transitions depend on retained tier states and prefix/suffix type",
                  "declaredRegimeNoClipping": "M<=1.5,Q<=2 gives chance6<=0.144 and chance7<=0.36"},
              "firstNormalOverwriteCase": {"orderedTypes": [a["type"] for a in edge_order],
                                           "orderedT6Compatibility": [a["t6Compatibility"] for a in edge_order],
                                           "initialTiers": edge_state[0].tolist(),
                                           "blockedInitialPick": 2, "actualFallbackSlot": 1,
                                           "allowedMaximumBeforeNormalWasSkipped": True,
                                           "probabilitiesAfterForce": edge.tolist()},
              "inputAudit": input_audit(),
              "assumptions": ["Independent ideal RNG draws and nominal decimal probabilities",
                              "ilvl100 ordinary affixes, maximum two prefixes and two suffixes",
                              "No sealed/experimental/champion affixes or post-drop corruption",
                              "Input provenance is documented separately in docs/T7_EQUIPMENT_POOLS.md"],
              "elapsedSeconds": time.monotonic() - started, "checks": checks}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: max difference {maximum:.3g}; wrote {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
