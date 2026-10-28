import pytest
from engine import scenario_engine as se

BASE = dict(customers=100, aov=500, margin=40, opex=10000)


def test_known_values():
    r = se.calculate_scenario(**BASE)
    assert r["revenue"] == 50000
    assert r["gross_profit"] == 20000
    assert r["operating_profit"] == 10000
    assert r["operating_margin"] == pytest.approx(20.0)


def test_zero_revenue():
    r = se.calculate_scenario(0, 500, 40, 10000)
    assert r["operating_margin"] == 0.0 and r["operating_profit"] == -10000


def test_invalid():
    with pytest.raises(ValueError):
        se.calculate_scenario(-1, 500, 40, 0)
    with pytest.raises(ValueError):
        se.calculate_scenario(1, 500, 140, 0)


def test_sensitivity():
    df, swing = se.sensitivity_analysis(BASE, pct=0.2, steps=5)
    c = df[df.variable == se.VARS["customers"]]
    assert c.operating_profit.min() == pytest.approx(80 * 500 * .4 - 10000)
    assert c.operating_profit.max() == pytest.approx(120 * 500 * .4 - 10000)
    o = df[df.variable == se.VARS["opex"]]
    assert o.operating_profit.max() - o.operating_profit.min() == pytest.approx(4000)
    assert swing.iloc[0].profit_swing >= swing.iloc[-1].profit_swing
    assert (df[df.variable == se.VARS["margin"]].value <= 100).all()


def test_compare():
    df = se.compare_scenarios({"Base": BASE})
    assert df.loc[0, "operating_profit"] == 10000
