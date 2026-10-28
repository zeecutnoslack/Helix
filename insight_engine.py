"""Deterministic findings. Each is tagged: Calculated, Assumption, Interpretation, or Action."""
from . import decision_engine as de


def _f(title, category, obs, calc, interp, step, limit=""):
    return {"title": title, "category": category, "observation": obs, "calculation": calc,
            "interpretation": interp, "next_step": step, "limitations": limit}


def generate_findings(alts, weights, scenario_df=None, swing_df=None):
    out = []
    r = de.rank_alternatives(alts, weights)
    nw = de.normalised_weight_map(weights)
    lead, ls = r[0]
    if len(r) > 1:
        gap = ls - r[-1][1]
        out.append(_f("Highest-ranked alternative", "Calculated",
                      f"{lead} ranks first with a weighted score of {ls:.2f}/10.",
                      "Ranking: " + "; ".join(f"{a} {s:.2f}" for a, s in r) + f". Gap between first and last: {gap:.2f}.",
                      "A small gap means the ranking is weak evidence; a large gap is more robust to scoring noise.",
                      "Check the scores behind the top two options with evidence.",
                      "Scores are subjective judgements, not measurements."))
        drv = de.top_drivers(alts, weights)[:2]
        out.append(_f("What separates the leaders", "Calculated",
                      f"Largest contribution gaps between {r[0][0]} and {r[1][0]}: " + ", ".join(f"{c} ({d:+.2f})" for c, d in drv) + ".",
                      "Gap = weight x score difference per criterion.",
                      "These criteria drive the ranking, so the weights placed on them matter most.",
                      "Ask whether these weights reflect your true priorities."))
    top_w = sorted(nw.items(), key=lambda kv: -kv[1])[0]
    out.append(_f("Most influential weight", "Assumption",
                  f"'{top_w[0]}' carries {top_w[1]*100:.0f}% of the total weight.",
                  "Normalised weight = raw weight / sum of raw weights.",
                  "If this one priority is mistaken, the ranking may change materially.",
                  "Justify this weight explicitly, or test lower values."))
    st = de.ranking_stability(alts, weights)
    if st["stable"]:
        out.append(_f("Ranking stability", "Calculated",
                      f"The leader did not change when any single weight moved by ±{st['shift']*100:.0f} points.",
                      "Tested each criterion up and down, renormalising.",
                      "Ranking looks reasonably stable to modest weight changes.",
                      "Also test larger changes and different scores.",
                      "Only single-weight shifts tested; score uncertainty not tested."))
    else:
        ch = st["changes"][0]
        out.append(_f("Ranking is sensitive to weights", "Calculated",
                      f"{len(st['changes'])} weight shift(s) change the winner, e.g. {ch['criterion']} {ch['shift']*100:+.0f} points makes {ch['new_winner']} first.",
                      f"Baseline winner: {st['base_winner']}.",
                      "The preferred option depends on a priority you may not be sure about (hypothesis).",
                      "Clarify priorities before committing; gather evidence on the contested criteria."))
    if scenario_df is not None and len(scenario_df):
        neg = scenario_df[scenario_df["operating_profit"] < 0]
        rng = scenario_df["operating_profit"]
        out.append(_f("Scenario outcomes", "Calculated",
                      (f"Negative estimated operating profit in: {', '.join(neg['Scenario'])}." if len(neg)
                       else "No scenario shows negative estimated operating profit.") +
                      f" Range: INR {rng.min():,.0f} to INR {rng.max():,.0f} per month.",
                      "Operating profit = revenue x margin - operating expenses.",
                      "A positive estimate does not show viability; inputs are user assumptions.",
                      "Validate customer volume and expenses with pilots or quotes.",
                      "Excludes tax, interest, depreciation, working capital and cash timing."))
    if swing_df is not None and len(swing_df):
        t = swing_df.iloc[0]
        out.append(_f("Most influential financial input", "Calculated",
                      f"'{t['variable']}' moves estimated operating profit most (swing INR {t['profit_swing']:,.0f}).",
                      "Each input varied alone over the tested range, others fixed.",
                      "Assumptions with the largest swing deserve validation first.",
                      f"Collect real data on {t['variable'].lower()}.",
                      "Inputs vary independently; real-world inputs are often correlated."))
    out.append(_f("Reasoning risk: single estimates", "Interpretation",
                  "All inputs are point estimates entered by the user.",
                  "No ranges or evidence sources were recorded.",
                  "Untested optimism is possible; this is a risk, not a detected bias.",
                  "Record evidence or a confidence level for each score and input."))
    return out


def report_markdown(title, findings):
    lines = [f"# HELIX Insight Report: {title}", "",
             "_Decision-support prototype; not financial, legal or investment advice._", ""]
    for f in findings:
        lines += [f"## {f['title']} [{f['category']}]", f"- **Observation:** {f['observation']}",
                  f"- **Calculation/input:** {f['calculation']}", f"- **Interpretation:** {f['interpretation']}",
                  f"- **Suggested next step:** {f['next_step']}"]
        if f["limitations"]:
            lines.append(f"- **Limitations:** {f['limitations']}")
        lines.append("")
    return "\n".join(lines)


def full_report(title, desc, ranking, scen_df, swing_df, findings, questions):
    """Editorial Markdown report built only from computed results."""
    L = [f"# {title}", "", f"_{desc}_", "", "_HELIX decision-support prototype. Not financial, legal or investment advice._", "",
         "## Ranked alternatives (weighted-sum model)"]
    L += [f"{i+1}. **{n}**: {s:.2f} / 10" for i, (n, s) in enumerate(ranking)]
    L += ["", "The ranking reflects your weights and subjective scores; it is not an objectively correct decision.", "",
          "## Scenario results (simplified monthly estimates, INR)", "",
          "| Scenario | Customers | AOV | Margin % | Opex | Revenue | Est. operating profit |", "|---|---|---|---|---|---|---|"]
    for r in scen_df.itertuples():
        L.append(f"| {r.Scenario} | {r.customers:,.0f} | {r.aov:,.0f} | {r.margin:.0f} | {r.opex:,.0f} | {r.revenue:,.0f} | {r.operating_profit:,.0f} |")
    L += ["", "## Sensitivity findings (one input varied at a time, baseline scenario)"]
    L += [f"- {r.variable}: profit swing INR {r.profit_swing:,.0f}" for r in swing_df.itertuples()]
    L += ["", "## Key findings"]
    for f in findings:
        L += [f"### {f['title']} [{f['category']}]", f"- Observation: {f['observation']}", f"- Interpretation: {f['interpretation']}",
              f"- Next step: {f['next_step']}"] + ([f"- Limitations: {f['limitations']}"] if f["limitations"] else [])
    L += ["", "## Questions requiring investigation"] + [f"- {q}" for q in questions]
    L += ["", "## Limitations", "- Scores, weights and financial inputs are user assumptions, not verified facts.",
          "- Operating profit is a simplified estimate, not net profit or cash flow.",
          "- Sensitivity ignores correlation between inputs. No evidence beyond the supplied inputs was analysed."]
    return "\n".join(L)
