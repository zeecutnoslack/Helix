"""Simplified monthly financial scenarios and one-at-a-time sensitivity analysis."""
import numpy as np
import pandas as pd

VARS = {"customers": "Monthly customers", "aov": "Average order value (INR)",
        "margin": "Gross margin (%)", "opex": "Monthly operating expenses (INR)"}


def calculate_scenario(customers, aov, margin, opex):
    """Return revenue, gross profit, estimated operating profit and margin (simplified estimates)."""
    if min(customers, aov, opex) < 0 or not 0 <= margin <= 100:
        raise ValueError("Customers, order value, expenses must be >= 0 and margin within 0-100.")
    revenue = customers * aov
    gross = revenue * margin / 100
    op = gross - opex
    return {"revenue": revenue, "gross_profit": gross, "operating_profit": op,
            "operating_margin": op / revenue * 100 if revenue else 0.0}


def compare_scenarios(scenarios):
    """scenarios: {name: {customers, aov, margin, opex}} -> DataFrame."""
    rows = [{"Scenario": n, **p, **calculate_scenario(**p)} for n, p in scenarios.items()]
    return pd.DataFrame(rows)


def sensitivity_analysis(base, pct=0.30, steps=7):
    """Vary each input alone across base*(1±pct); others fixed. Returns (long DataFrame, swing DataFrame)."""
    calculate_scenario(**base)
    rows = []
    for v in VARS:
        for f in np.linspace(1 - pct, 1 + pct, steps):
            p = dict(base)
            p[v] = min(100.0, base[v] * f) if v == "margin" else base[v] * f
            rows.append({"variable": VARS[v], "change_pct": round((f - 1) * 100, 1), "value": p[v],
                         "operating_profit": calculate_scenario(**p)["operating_profit"]})
    df = pd.DataFrame(rows)
    swing = (df.groupby("variable")["operating_profit"].agg(lambda s: s.max() - s.min())
             .rename("profit_swing").sort_values(ascending=False).reset_index())
    return df, swing
