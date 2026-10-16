"""Reproduce the 1.5.2.2 Ring/T7 investigation from mined parameters.

This is an analytic reconstruction, not a game-client drop experiment.
It models level-100 ordinary Rings, whose eligible affixes all permit T6/T7.
It does not model corruption, guaranteed special-affix T7, or other item pools.
"""

from collections import Counter, defaultdict
from itertools import product
from math import prod
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]


def tier_distribution(weight, params, *, magic, cof):
    rare_roll = min(1.0, max(0.0, 1.0 - weight))
    normal, rare = (params[k] for k in (
        "normal_uncraftable_upgrade_chances", "rare_uncraftable_upgrade_chances"))
    multiplier = params["max_cof_exalted_multiplier"] if cof else 1.0
    t7_multiplier = params["max_cof_t7_multiplier"] if cof else 1.0
    a = min(1.0, multiplier * (normal[0] + (rare[0] - normal[0]) * rare_roll))
    b = min(1.0, multiplier * t7_multiplier * (normal[1] + (rare[1] - normal[1]) * rare_roll))
    if magic:
        a *= 1.0 - params["magic_exalted_prevention_chance"]
    c5, c4, c3, c2 = params["craftable_tier_cumulative_cutoffs_T5_T4_T3_T2"]
    return (1-c2, c2-c3, c3-c4, c4-c5, c5*(1-a), c5*a*(1-b), c5*a*b), b


def pair_distribution(pool, params, cof):
    """Two affixes of one type, weighted sampling without replacement."""
    total = sum(a["weight"] for a in pool)
    mass = [[0.0]*7 for _ in range(7)]
    b0 = [[0.0]*7 for _ in range(7)]
    b1 = [[0.0]*7 for _ in range(7)]
    for i, first in enumerate(pool):
        p, b = tier_distribution(first["weight"], params, magic=False, cof=cof)
        for j, second in enumerate(pool):
            if i == j:
                continue
            q, c = tier_distribution(second["weight"], params, magic=False, cof=cof)
            pick = first["weight"]/total * second["weight"]/(total-first["weight"])
            for s, t in product(range(7), repeat=2):
                v = pick*p[s]*q[t]
                mass[s][t] += v
                b0[s][t] += v*b
                b1[s][t] += v*c
    assert abs(sum(map(sum, mass))-1) < 1e-10
    return mass, b0, b1


def joint_states(pool, n, params, cof):
    """Yield (prefix count, tiers, mass, E[force T7 chance | original tiers])."""
    if n == 4:
        # Both types necessarily fill their two slots. Their internal weighted
        # selections are independent; interleaving only schedules those draws.
        pre = pair_distribution([a for a in pool if a["type"] == 0], params, cof)
        suf = pair_distribution([a for a in pool if a["type"] == 1], params, cof)
        for a, b, c, d in product(range(7), repeat=4):
            p, q = pre[0][a][b], suf[0][c][d]
            if p*q:
                yield 2, (a+1, b+1, c+1, d+1), p*q, (
                    pre[1][a][b]/p, pre[2][a][b]/p,
                    suf[1][c][d]/q, suf[2][c][d]/q)
        return

    # For fewer than four affixes the type counts are random and correlated
    # with earlier choices. Preserve that correlation in the selection DP.
    grouped = Counter((a["type"], a["weight"]) for a in pool)
    groups = sorted(grouped)
    counts = [grouped[g] for g in groups]
    dp = {(0,)*len(groups): 1.0}
    for _ in range(n):
        following = defaultdict(float)
        for used, probability in dp.items():
            type_counts = [sum(u for u, g in zip(used, groups) if g[0] == typ) for typ in (0, 1)]
            valid = [(i, (counts[i]-used[i])*g[1]) for i, g in enumerate(groups)
                     if type_counts[g[0]] < 2 and used[i] < counts[i]]
            total = sum(w for _, w in valid)
            for i, w in valid:
                updated = list(used)
                updated[i] += 1
                following[tuple(updated)] += probability*w/total
        dp = following
    assert abs(sum(dp.values())-1) < 1e-10
    accum = {}
    for used, probability in dp.items():
        selected = [g for g, count in zip(groups, used) for _ in range(count)]
        prefixes = sum(g[0] == 0 for g in selected)
        distributions = [tier_distribution(g[1], params, magic=n < 3, cof=cof) for g in selected]
        for state in product(range(1, 8), repeat=n):
            p = probability*prod(distributions[i][0][t-1] for i, t in enumerate(state))
            values = accum.setdefault((prefixes, state), [0.0]*(n+1))
            values[0] += p
            for i in range(n):
                values[i+1] += p*distributions[i][1]
    assert abs(sum(v[0] for v in accum.values())-1) < 1e-10
    for (prefixes, state), values in accum.items():
        if values[0]:
            yield prefixes, state, values[0], tuple(v/values[0] for v in values[1:])


def lens_transitions(state, prefixes, lens, params):
    if lens is None:
        yield state, 1.0
        return
    slots = (range(len(state)) if lens == "quality" else
             range(prefixes) if lens == "origin" else range(prefixes, len(state)))
    weights = params["lens_candidate_weights_T1_to_T7"]
    candidates = [(i, weights[state[i]-1]) for i in slots if state[i] < 7]
    total = sum(w for _, w in candidates)
    if not total:
        yield state, 1.0
        return
    chance = params["lens_trigger_chance"]
    increases = params["lens_increase_weights"]
    denominator = sum(increases.values())
    yield state, 1-chance
    for i, w in candidates:
        for delta, increment_weight in increases.items():
            updated = list(state)
            updated[i] = min(7, state[i]+int(delta))
            yield tuple(updated), chance*w/total*increment_weight/denominator


def force_transitions(state, chances, force, params):
    m = sum(t >= 6 for t in state)
    attempt = force*(1-params["force_skip_chance_per_existing_exalted_affix"])**m
    yield state, 1-attempt
    for i, tier in enumerate(state):
        if tier >= 6:
            yield state, attempt/len(state)
        else:
            for target, probability in ((6, 1-chances[i]), (7, chances[i])):
                updated = list(state)
                updated[i] = target
                yield tuple(updated), attempt/len(state)*probability


def summarize(count, exalted, zero_exalted, prefix, suffix):
    assert abs(sum(count)-1) < 1e-10
    conditional = ([zero_exalted/exalted]+[p/exalted for p in count[1:]]
                   if exalted else None)
    return {"p_exalted": exalted, "p_T7_count": count,
            "p_T7_count_given_exalted": conditional,
            "p_exalted_without_T7": zero_exalted,
            "p_at_least_one_T7_prefix": prefix, "p_at_least_one_T7_suffix": suffix}


def evaluate(states, n, params, lens, force):
    count = [0.0]*5
    exalted = zero_exalted = prefix = suffix = 0.0
    for prefixes, state, probability, chances in states:
        for after_lens, lp in lens_transitions(state, prefixes, lens, params):
            for final, fp in force_transitions(after_lens, chances, force, params):
                p = probability*lp*fp
                n7 = final.count(7)
                count[n7] += p
                if max(final) >= 6:
                    exalted += p
                    if n7 == 0:
                        zero_exalted += p
                if 7 in final[:prefixes]:
                    prefix += p
                if 7 in final[prefixes:]:
                    suffix += p
    return {"raw_rarity": n, "lens": lens, "force_probability": force,
            **summarize(count, exalted, zero_exalted, prefix, suffix)}


def mix(rows, probabilities, label):
    count = [sum(p*row["p_T7_count"][i] for p, row in zip(probabilities, rows)) for i in range(5)]
    summed = [sum(p*row[key] for p, row in zip(probabilities, rows)) for key in (
        "p_exalted", "p_exalted_without_T7", "p_at_least_one_T7_prefix", "p_at_least_one_T7_suffix")]
    return {"label": label, "lens": rows[-1]["lens"], **summarize(count, *summed)}


def analyze(document):
    params, pool = document["parameters"], document["ring_pool"]
    assert len(pool) == len({a["id"] for a in pool}) == 42
    assert document["scope"]["item_level"] == 100
    states = {cof: {n: list(joint_states(pool, n, params, cof)) for n in range(1, 5)}
              for cof in (False, True)}
    components, prophecy = [], []
    for lens in (None, "quality", "origin", "finality"):
        rows = [evaluate(states[True][n], n, params, lens, 1) for n in range(1, 5)]
        components.extend(rows)
        prophecy.append(mix(rows, params["ordinary_exalted_prophecy_raw_rarity_probabilities_1_to_4"],
                            "ordinary_exalted_ring_prophecy_max_CoF"))
    natural = []
    for cof in (False, True):
        white = {"lens": None, **summarize([1, 0, 0, 0, 0], 0, 0, 0, 0)}
        rows = [white]+[evaluate(states[cof][n], n, params, None,
                                params["max_cof_rare_force_chance"] if cof and n >= 3 else 0)
                        for n in range(1, 5)]
        natural.append(mix(rows, params["normal_unmodified_raw_rarity_probabilities_0_to_4"],
                           "normal_unmodified_ring_max_CoF" if cof else "normal_unmodified_ring_no_CoF"))
    return {"scope": document["scope"], "ordinary_exalted_ring_prophecy": prophecy,
            "prophecy_components_by_raw_rarity": components,
            "normal_unmodified_ring_generation": natural,
            "four_affix_exalted_ring_prophecy": [r for r in components if r["raw_rarity"] == 4]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameters", type=Path, default=ROOT/"analysis/t7-lens-parameters.json")
    parser.add_argument("--output", type=Path, default=ROOT/"analysis/t7-lens-probability-results.json")
    args = parser.parse_args()
    result = analyze(json.loads(args.parameters.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
    for row in result["ordinary_exalted_ring_prophecy"]:
        p = row["p_T7_count"]
        print(f"{row['lens'] or 'none':8s} exact 1T7={p[1]*100:.6f}%  exact 2T7={p[2]*100:.6f}%  >=2T7={sum(p[2:])*100:.6f}%")


if __name__ == "__main__":
    main()
