"""Weighted-sum multi-criteria decision analysis (MCDA)."""
import math

DEFAULT_CRITERIA = {"Market demand": 30, "Profit potential": 25, "Ease of execution": 20,
                    "Competitive advantage": 15, "Capital affordability": 10}
SAMPLE_ALTERNATIVES = {
    "A. AI-assisted tutoring": [8, 7, 6, 6, 7],
    "B. Sustainable packaging": [7, 6, 4, 5, 3],
    "C. Workflow automation consultancy": [7, 8, 7, 7, 8],
}


def normalise_weights(weights):
    """Return weights summing to 1. All-zero input falls back to equal weights."""
    w = [float(x) for x in weights]
    if any((not math.isfinite(x)) or x < 0 for x in w):
        raise ValueError("Weights must be finite and non-negative.")
    if not w:
        return []
    total = sum(w)
    return [1 / len(w)] * len(w) if total == 0 else [x / total for x in w]


def _validate(alts, criteria):
    for name, scores in alts.items():
        for c in criteria:
            v = scores.get(c)
            if v is None or not math.isfinite(float(v)) or not 1 <= float(v) <= 10:
                raise ValueError(f"Score for '{name}' / '{c}' must be between 1 and 10.")


def normalised_weight_map(weights):
    """dict criterion -> normalised weight."""
    return dict(zip(weights.keys(), normalise_weights(weights.values())))


def weighted_scores(alts, weights):
    """score(a) = sum_j w_j * s_aj. alts: {alt: {criterion: score}}; weights: {criterion: raw}."""
    nw = normalised_weight_map(weights)
    _validate(alts, nw)
    return {a: sum(nw[c] * float(s[c]) for c in nw) for a, s in alts.items()}


def rank_alternatives(alts, weights):
    """List of (alternative, score), best first (stable for ties)."""
    ws = weighted_scores(alts, weights)
    return sorted(ws.items(), key=lambda kv: -kv[1])


def contributions(alts, weights):
    """{alt: {criterion: weight*score}} - how each criterion builds each total."""
    nw = normalised_weight_map(weights)
    return {a: {c: nw[c] * float(s[c]) for c in nw} for a, s in alts.items()}


def top_drivers(alts, weights):
    """Criteria ranked by how much they separate the top two alternatives (positive favours leader)."""
    r = rank_alternatives(alts, weights)
    if len(r) < 2:
        return []
    con = contributions(alts, weights)
    lead, second = r[0][0], r[1][0]
    d = {c: con[lead][c] - con[second][c] for c in con[lead]}
    return sorted(d.items(), key=lambda kv: -abs(kv[1]))


def ranking_stability(alts, weights, shift=0.10):
    """Shift each normalised weight by +/-shift (renormalised); report cases where the winner changes."""
    base = rank_alternatives(alts, weights)[0][0]
    nw = normalised_weight_map(weights)
    changes = []
    for c in nw:
        for sign in (1, -1):
            w = dict(nw)
            w[c] = max(0.0, w[c] + sign * shift)
            winner = rank_alternatives(alts, w)[0][0]
            if winner != base:
                changes.append({"criterion": c, "shift": sign * shift, "new_winner": winner})
    return {"base_winner": base, "stable": not changes, "changes": changes, "shift": shift}
