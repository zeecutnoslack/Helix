import pytest
from engine import decision_engine as de

ALTS = {"A": {"x": 10, "y": 2}, "B": {"x": 4, "y": 8}}


def test_normalise_weights():
    assert de.normalise_weights([30, 25, 20, 15, 10]) == pytest.approx([.3, .25, .2, .15, .1])
    assert de.normalise_weights([2, 2]) == pytest.approx([.5, .5])


def test_weighted_score():
    s = de.weighted_scores(ALTS, {"x": 75, "y": 25})
    assert s["A"] == pytest.approx(0.75 * 10 + 0.25 * 2)
    assert s["B"] == pytest.approx(0.75 * 4 + 0.25 * 8)


def test_ranking():
    assert de.rank_alternatives(ALTS, {"x": 75, "y": 25})[0][0] == "A"
    assert de.rank_alternatives(ALTS, {"x": 10, "y": 90})[0][0] == "B"


def test_zero_weights_safe():
    assert de.normalise_weights([0, 0]) == [0.5, 0.5]
    assert de.weighted_scores(ALTS, {"x": 0, "y": 0})["A"] == pytest.approx(6.0)


def test_invalid_inputs():
    with pytest.raises(ValueError):
        de.normalise_weights([-1, 2])
    with pytest.raises(ValueError):
        de.weighted_scores({"A": {"x": 11, "y": 2}}, {"x": 1, "y": 1})


def test_stability_detects_flip():
    assert not de.ranking_stability(ALTS, {"x": 50, "y": 50})["stable"]
