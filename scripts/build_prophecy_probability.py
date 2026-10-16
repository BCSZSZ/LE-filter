"""Exact ordinary Exalted prophecy probabilities from frozen, mined affix pools.

Development dependency: NumPy. The published calculator only reads the resulting
JSON; neither the browser nor the filter workbench needs NumPy. Probabilities
use independent ideal RNG draws, rather than a simulation of a client session.
"""

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LENSES = ("none", "quality", "origin", "finality")
RARITY_MIX = np.array([.005, .00995, .39402, .59103])
COF_REGIMES = {"4": (1.5, 1), "9": (1.5, 2)}


def affix_category(affix, has_incompatible):
    """type plus Normal / allowed Maximum / blocked T6 compatibility."""
    if not has_incompatible:
        return affix["type"], 0
    compatibility = (0 if affix["t6Compatibility"] == 0 else
                     1 if affix["naturalT6Eligible"] else 2)
    return affix["type"], compatibility


def selection_moments(pool, n):
    """Joint moments of ordered draws, retaining caps and unique affix IDs.

    Natural tier probabilities have degree two in r=1-weight. The force stage
    introduces at most one further factor of r in one slot. Thus powers 0..3
    are sufficient to integrate the full tier/lens/force process exactly.
    """
    has_incompatible = any(not a["naturalT6Eligible"] for a in pool)
    grouped = Counter((*affix_category(a, has_incompatible), a["weight"])
                      for a in pool)
    groups = sorted(grouped)
    counts = [grouped[g] for g in groups]
    used = [0] * len(groups)
    paths = defaultdict(list)

    def draw(sequence, probability, type_counts):
        if len(sequence) == n:
            categories = tuple(groups[i][:2] for i in sequence)
            rare = [min(1., max(0., 1. - groups[i][2])) for i in sequence]
            paths[categories].append([probability, *rare])
            return
        candidates = [(i, (counts[i] - used[i]) * g[2])
                      for i, g in enumerate(groups)
                      if type_counts[g[0]] < 2 and used[i] < counts[i]]
        total = sum(w for _, w in candidates)
        for i, weight in candidates:
            typ = groups[i][0]
            used[i] += 1
            type_counts[typ] += 1
            draw((*sequence, i), probability * weight / total, type_counts)
            type_counts[typ] -= 1
            used[i] -= 1

    draw((), 1., [0, 0])
    moments = {}
    axes = "abcd"[:n]
    expression = "p," + ",".join("p" + a for a in axes) + "->" + axes
    for categories, values in paths.items():
        values = np.asarray(values)
        powers = [values[:, i + 1, None] ** np.arange(4) for i in range(n)]
        moments[categories] = np.einsum(expression, values[:, 0], *powers,
                                        optimize="greedy")
    total = sum(m[(0,) * n] for m in moments.values())
    assert abs(total - 1) < 1e-10, total
    return moments


def force_kernel(states, categories):
    """P(final T7 count) = H0 + sum(Hi * force_T7_probability_i).

    The native fallback scans original list order for the first Normal affix;
    it may overwrite an existing T7, and does not retry an already-exalted
    initial pick. Both otherwise easily missed cases remain in this kernel.
    """
    size, n = states.shape
    rows = np.arange(size)
    count = np.count_nonzero(states == 7, axis=1)
    attempt = .3 ** np.count_nonzero(states >= 6, axis=1)
    out = np.zeros((size, n + 1, 5))
    out[rows, 0, count] += 1 - attempt
    for j in range(n):
        existing = states[:, j] >= 6
        out[rows[existing], 0, count[existing]] += attempt[existing] / n
        active = ~existing
        target = j
        if categories[j][1] == 2:
            target = next((i for i in range(n) if categories[i][1] == 0), j)
        selected = rows[active]
        low_count = count[active] - (states[active, target] == 7)
        mass = attempt[active] / n
        out[selected, 0, low_count] += mass
        out[selected, target + 1, low_count] -= mass
        out[selected, target + 1, low_count + 1] += mass
    return out


@lru_cache(maxsize=128)
def process_kernel(categories):
    """Lens transitions followed by force, for every original tier tuple."""
    n = len(categories)
    states = np.array(list(product(range(1, 8), repeat=n)))
    base = force_kernel(states, categories)
    results = [base]
    weights = np.array([0., .01, .05, .1, .5, 1., 2., 0.])
    for lens in LENSES[1:]:
        eligible_types = ({0, 1} if lens == "quality" else
                          {0} if lens == "origin" else {1})
        candidate = np.array([weights[states[:, i]] if cat[0] in eligible_types
                              else np.zeros(len(states))
                              for i, cat in enumerate(categories)]).T
        total = candidate.sum(axis=1)
        trigger = np.where(total > 0, .2, 0.)
        result = base * (1 - trigger[:, None, None])
        for i in range(n):
            chance = np.divide(candidate[:, i], total,
                               out=np.zeros_like(total), where=total > 0) * .2
            if not np.any(chance):
                continue
            for delta, probability in ((1, 2 / 9), (2, 1 / 3), (3, 4 / 9)):
                updated = states.copy()
                updated[:, i] = np.minimum(7, updated[:, i] + delta)
                result += force_kernel(updated, categories) * (
                    chance[:, None, None] * probability)
        results.append(result)
    # lens, force coefficient, count, original tier1, tier2, ...
    return np.stack(results).transpose(0, 2, 3, 1).reshape(
        (4, n + 1, 5) + (7,) * n)


def tier_polynomials(category, n, multiplier, t7_multiplier):
    """Coefficients of P(T=t | r) and P(T=t | r)*b(r)."""
    a = np.array([.045, .051]) * multiplier * (.05 if n < 3 else 1)
    b = np.array([.066, .054]) * multiplier * t7_multiplier
    tiers = np.zeros((7, 4))
    tiers[:5, 0] = [.16, .28, .24, .18, .14]
    if category[1] != 2:
        tiers[4, :2] -= .14 * a
        tiers[5, :2] += .14 * a
        ab = np.convolve(a, b) * .14
        tiers[5, :3] -= ab
        tiers[6, :3] += ab
    times_b = np.array([np.convolve(row[:3], b) for row in tiers])
    return tiers, times_b


def integrate(moments, multiplier, t7_multiplier):
    n = len(next(iter(moments)))
    result = np.zeros((4, 5))
    tier_axes, degree_axes = "tuvw"[:n], "abcd"[:n]
    expression = ("lk" + tier_axes + "," +
                  ",".join(t + d for t, d in zip(tier_axes, degree_axes)) +
                  "->lk" + degree_axes)
    for categories, moment in moments.items():
        kernel = process_kernel(categories)
        polynomials = [tier_polynomials(c, n, multiplier, t7_multiplier)
                       for c in categories]
        for coefficient in range(n + 1):
            factors = [p[1 if coefficient == i + 1 else 0]
                       for i, p in enumerate(polynomials)]
            polynomial = np.einsum(expression, kernel[:, coefficient], *factors,
                                   optimize="greedy")
            result += np.tensordot(polynomial, moment,
                                   axes=(tuple(range(2, 2 + n)), tuple(range(n))))
    assert np.max(np.abs(result.sum(axis=1) - 1)) < 1e-10, result
    assert result.min() > -1e-12
    return result


def evaluate_profile(profile):
    result = {rank: np.zeros((4, 5)) for rank in COF_REGIMES}
    for n, probability in enumerate(RARITY_MIX, 1):
        moments = selection_moments(profile["affixes"], n)
        for rank, (multiplier, t7_multiplier) in COF_REGIMES.items():
            result[rank] += probability * integrate(moments, multiplier, t7_multiplier)
    return {rank: {lens: distribution.tolist()
                   for lens, distribution in zip(LENSES, probabilities)}
            for rank, probabilities in result.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pools", type=Path, default=ROOT / "sources/t7-equipment-pools.json")
    parser.add_argument("--output", type=Path, default=ROOT / "analysis/prophecy-probabilities.json")
    parser.add_argument("--profile", help="Compute only this profile, for development checks")
    args = parser.parse_args()
    source = json.loads(args.pools.read_text(encoding="utf-8-sig"))
    results = []
    started = time.monotonic()
    for profile in source["profiles"]:
        if args.profile and profile["id"] != args.profile:
            continue
        computed = evaluate_profile(profile)
        results.append({k: profile[k] for k in (
            "id", "typeID", "typeKey", "nameEn", "classRequirement",
            "classRequirementName", "affixEffectModifier")}
                       | {"probabilities": computed})
        print(f"{profile['id']}: {100 * computed['9']['none'][1]:.6f}% / "
              f"{100 * computed['9']['none'][2]:.6f}% ({time.monotonic()-started:.1f}s)",
              flush=True)
    result = {"version": 1, "gameVersion": source["gameVersion"],
              "sourceSHA256": hashlib.sha256(args.pools.read_bytes()).hexdigest(),
              "scope": "ordinary_exalted_prophecy_per_generated_item",
              "itemLevel": 100, "areaLevelAffectsProbability": False,
              "corruptionAffectsProbability": False,
              "classCondition": "generated_equipment_class_requirement",
              "cofRegimes": COF_REGIMES,
              "rawRarityProbabilities": RARITY_MIX.tolist(),
              "equipmentTypes": [{k: e[k] for k in ("typeID", "typeKey", "name", "nameEn")}
                                 for e in source["equipmentTypes"]],
              "classes": [{"id": p["classRequirement"],
                           "name": p["classRequirementNameZh"]}
                          for p in source["profiles"] if p["typeID"] == 22],
              "profiles": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
