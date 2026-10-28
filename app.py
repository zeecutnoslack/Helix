"""HELIX - The Intelligence Lab. Run: streamlit run app.py"""
import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from engine import decision_engine as de
from engine import insight_engine as ie
from engine import scenario_engine as se
from engine.live_intelligence import run_live_investigation
import os

st.set_page_config(page_title="HELIX - The Intelligence Lab", layout="wide")
INK, SURF, LILAC, CYAN, IVORY, GREY, LINE = "#24231f", "#e7e1d6", "#c4472d", "#66858a", "#f5f0e6", "#77736a", "#cfc7b9"
PAL = [LILAC, CYAN, "#858b69", "#d59a58", "#8d7b9d", "#53635d"]
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600&family=IBM+Plex+Mono:wght@400;500;600&family=Manrope:wght@400;500;600;700&display=swap');
:root {{ --paper:#f1eee6; --ink:{INK}; --muted:{GREY}; --rule:{LINE}; --signal:{LILAC}; --blue:{CYAN}; }}
html, body, [class*="css"] {{ font-family:'Manrope',sans-serif; color:var(--ink); }}
.stApp {{ background:var(--paper); }}
[data-testid="stHeader"] {{ background:rgba(241,238,230,.92); }}
section[data-testid="stSidebar"] {{ display:none !important; }}
[data-testid="stAppViewContainer"] > .main {{ margin-left:0 !important; }}
[data-testid="stMainBlockContainer"] {{ max-width:1440px; }}
.topnav-label {{font-family:'IBM Plex Mono',monospace;font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;color:#77736a;}}
.nav-current {{font-family:'IBM Plex Mono',monospace;font-size:.72rem;letter-spacing:.04em;color:#c4472d;font-weight:600;}}

.block-container {{ max-width:1380px; padding-top:2.2rem; padding-bottom:4rem; animation:appear .45s ease both; }}
@keyframes appear {{ from {{opacity:0; transform:translateY(7px)}} to {{opacity:1;transform:translateY(0)}} }}
h1,h2,h3 {{ font-family:'Bodoni Moda',Georgia,serif!important; color:var(--ink)!important; font-weight:400!important; letter-spacing:-.035em!important; }}
h1 {{ font-size:clamp(2.5rem,5vw,4.4rem)!important; line-height:1.02!important; }}
h2 {{ font-size:2.1rem!important; }}
h3 {{ font-size:1.45rem!important; }}
p, label, .stMarkdown {{ color:var(--ink); }}
.mono {{ font-family:'IBM Plex Mono',monospace; font-size:.7rem; color:{GREY}; letter-spacing:.12em; text-transform:uppercase; }}
.hero {{ font-family:'Bodoni Moda',Georgia,serif; font-size:clamp(5rem,12vw,10.5rem); line-height:.78; letter-spacing:-.075em; color:{INK}; margin:.3rem 0 1.1rem; }}
.quote {{ font-family:'Bodoni Moda',Georgia,serif; font-size:clamp(1.45rem,2.5vw,2.3rem); line-height:1.18; font-style:italic; color:{INK}; border-left:3px solid {LILAC}; padding:.25rem 0 .25rem 1.15rem; margin:1.4rem 0; max-width:680px; }}
.big {{ font-family:'IBM Plex Mono',monospace; font-size:2.5rem; color:{LILAC}; letter-spacing:-.06em; }}
.card {{ border:0; border-top:1px solid {LINE}; border-radius:0; padding:.9rem .15rem 1rem; background:transparent; margin-bottom:.35rem; transition:padding-left .18s ease,border-color .18s ease; }}
.card:hover {{ border-color:{LILAC}; padding-left:.45rem; }}
.tag {{ font-family:'IBM Plex Mono',monospace; font-size:.66rem; letter-spacing:.1em; padding:3px 7px; border-radius:0; border:1px solid; display:inline-block; }}
.OBSERVED {{color:{CYAN};border-color:{CYAN}}} .ASSUMED {{color:{LILAC};border-color:{LILAC}}}
.INFERRED {{color:#9a6c37;border-color:#9a6c37}} .UNKNOWN {{color:{GREY};border-color:{GREY};border-style:dashed}}
.dot {{display:inline-block;width:7px;height:7px;border-radius:50%;background:{CYAN};margin-right:7px;animation:pulse 2.4s ease-in-out infinite}}
@keyframes pulse {{50% {{opacity:.3}}}}
.stButton>button,.stDownloadButton>button {{ border:1px solid {INK}; border-radius:0; background:transparent; color:{INK}; padding:.65rem 1rem; font-family:'IBM Plex Mono',monospace; font-size:.75rem; letter-spacing:.03em; transition:all .18s ease; min-height:2.8rem; }}
.stButton>button[kind="primary"] {{ background:{INK} !important; color:{IVORY} !important; border-color:{INK} !important; }}
.stButton>button[kind="primary"] p, .stButton>button[kind="primary"] span {{ color:{IVORY} !important; }}
.stButton>button:focus-visible, .stDownloadButton>button:focus-visible {{ outline:2px solid {CYAN}!important; outline-offset:3px; }}
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {{ border-radius:0!important; border-color:{LINE}!important; background:rgba(255,255,255,.32)!important; }}
.stTextInput input:focus, .stTextArea textarea:focus {{ border-color:{LILAC}!important; box-shadow:0 0 0 1px {LILAC}!important; }}
[data-testid="stExpander"] {{ border:1px solid {LINE}; border-radius:0; background:rgba(255,255,255,.18); }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius:0!important; }}
.eyebrow {{font-family:'IBM Plex Mono',monospace;font-size:.68rem;letter-spacing:.13em;text-transform:uppercase;color:{GREY};}}
.featureline {{display:flex;align-items:flex-start;gap:.8rem;padding:.85rem 0;border-top:1px solid {LINE};}}
.featureline .num {{font-family:'IBM Plex Mono',monospace;color:{LILAC};font-size:.72rem;min-width:2rem;padding-top:.2rem;}}
.featureline .label {{font-family:'Bodoni Moda',Georgia,serif;font-size:1.2rem;line-height:1.15;}}
.featureline .detail {{font-size:.86rem;color:{GREY};margin-top:.2rem;}}
[data-testid="stTabs"] [data-baseweb="tab-list"] {{flex-wrap:wrap;}}
/* Navigation as a readable editorial index */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {{
  border-color:transparent!important; border-bottom:1px solid {LINE}!important;
  text-align:left!important; background:rgba(255,255,255,.12)!important;
}}
div[data-testid="stHorizontalBlock"] button[kind="primary"] {{
  text-align:left!important; border-bottom:2px solid {LILAC}!important;
  box-shadow:inset 0 -2px 0 {LILAC};
}}
div[data-testid="stHorizontalBlock"] button p {{
  white-space:normal!important; line-height:1.25!important;
}}

.stProgress > div > div {{background-color:{LILAC}!important;}}
.stButton>button:hover,.stDownloadButton>button:hover {{ background:{LILAC}; color:#fff; border-color:{LILAC}; transform:translateY(-1px); }}
.stButton>button {{ overflow-wrap:anywhere; }}
@media (max-width:900px) {{ [data-testid="stHorizontalBlock"] {{flex-wrap:wrap;}} }}
[data-testid="stMetric"] {{ background:transparent; border-top:1px solid {LINE}; border-radius:0; padding:1rem .2rem; }}
[data-testid="stMetricLabel"] {{ font-family:'IBM Plex Mono',monospace; text-transform:uppercase; letter-spacing:.08em; font-size:.68rem; }}
[data-testid="stMetricValue"] {{ font-family:'Bodoni Moda',Georgia,serif; color:{INK}; }}
[data-testid="stSlider"] [role="slider"] {{ accent-color:{LILAC}; }}
[data-baseweb="tab-list"] {{ gap:1rem; border-bottom:1px solid {LINE}; }}
button[data-baseweb="tab"] {{ background:transparent; border-radius:0; }}
[data-testid="stDataFrame"] {{ border:1px solid {LINE}; }}
[data-testid="stAlert"] {{ border-radius:0 !important; box-shadow:none !important; }}
[data-testid="stAlert"][kind="success"] {{ background:#e1e7d8 !important; border-left:3px solid #858b69 !important; color:{INK} !important; }}
[data-testid="stAlert"][kind="warning"] {{ background:#f0e4d2 !important; border-left:3px solid #b47a39 !important; color:{INK} !important; }}
hr {{ border-color:{LINE}; margin:2rem 0; }}
:focus-visible {{outline:2px solid {CYAN}!important;outline-offset:3px}}
@media (prefers-reduced-motion:reduce) {{ * {{animation:none!important;transition:none!important}} }}
@media (max-width:700px) {{ .hero {{font-size:4.7rem}} .quote {{font-size:1.3rem}} .block-container {{padding-top:1rem}} }}
</style>""", unsafe_allow_html=True)

SCEN = {"Baseline": (120, 1500, 60, 60000), "Optimistic": (180, 1700, 65, 65000), "Downside": (70, 1200, 50, 60000)}
SF = ["customers", "aov", "margin", "opex"]
inr = lambda x: f"-₹{abs(x):,.0f}" if x < 0 else f"₹{x:,.0f}"


def style(fig, h=380):
    fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=h,
                      font=dict(family="Manrope", color=INK), margin=dict(l=10, r=10, t=45, b=10), transition_duration=300,
                      xaxis=dict(gridcolor=LINE, zerolinecolor=LINE), yaxis=dict(gridcolor=LINE, zerolinecolor=LINE))
    return fig


def load_sample():
    ss = st.session_state
    for k in [k for k in ss if k.startswith(("w|", "s|", "sc|"))]:
        del ss[k]
    ss.crits, ss.alts = list(de.DEFAULT_CRITERIA), list(de.SAMPLE_ALTERNATIVES)
    for c, w in de.DEFAULT_CRITERIA.items():
        ss[f"w|{c}"] = w
    for a, sc in de.SAMPLE_ALTERNATIVES.items():
        for c, v in zip(ss.crits, sc):
            ss[f"s|{a}|{c}"] = v
    for n, vals in SCEN.items():
        for f, v in zip(SF, vals):
            ss[f"sc|{n}|{f}"] = v
    ss.title = "Which business opportunity should the founder pursue?"
    ss.desc = "A fictional founder compares three illustrative opportunities. Not investment advice."


if "crits" not in st.session_state:
    load_sample()
ss = st.session_state


def model():
    w = {c: float(ss.get(f"w|{c}", 0)) for c in ss.crits}
    a = {n: {c: float(ss.get(f"s|{n}|{c}", 5)) for c in ss.crits} for n in ss.alts}
    return a, w


def ranking():
    a, w = model()
    if len(a) < 2 or not w:
        return None, None, None
    return a, w, de.rank_alternatives(a, w)


def scen_dict():
    return {n: {f: float(ss.get(f"sc|{n}|{f}", 0)) for f in SF} for n in SCEN}


def go_to(p):
    ss.page = p


PAGES = ["Home", "Live Intelligence", "Decision Map", "Decision Studio", "Scenario Lab", "Assumption Challenger", "Decision Report", "Methodology"]
# Full-width editorial navigation: no permanent sidebar or radio-button stack.
brand, navstatus, resetcol = st.columns([2.2, 1.2, 1])
with brand:
    st.markdown("""<div style="display:flex;align-items:baseline;gap:.75rem;flex-wrap:wrap"><span style="font-family:'Bodoni Moda',Georgia,serif;font-size:2.15rem;letter-spacing:-.07em;line-height:1">HELIX<span style="color:#c4472d">.</span></span><span class="mono">The Intelligence Lab</span></div>""", unsafe_allow_html=True)
with navstatus:
    st.markdown("<div style='padding-top:.55rem'><span class='dot'></span><span class='mono'>research workspace</span></div>", unsafe_allow_html=True)
with resetcol:
    if st.button("Reset sample ↺", key="top_reset", use_container_width=True):
        load_sample(); st.rerun()
st.markdown("<hr style='margin:.8rem 0 .65rem'>", unsafe_allow_html=True)
nav_labels = {
    "Home": "01  HOME", "Live Intelligence": "02  LIVE INTELLIGENCE",
    "Decision Map": "03  DECISION MAP", "Decision Studio": "04  DECISION STUDIO",
    "Scenario Lab": "05  SCENARIO LAB", "Assumption Challenger": "06  ASSUMPTIONS",
    "Decision Report": "07  FIELD REPORT", "Methodology": "08  METHOD"
}
# Two rows keep navigation readable instead of compressing eight tiny controls.
for targets in [PAGES[:4], PAGES[4:]]:
    nav_cols = st.columns(4, gap="small")
    for col, target in zip(nav_cols, targets):
        with col:
            active = ss.get("page", "Home") == target
            if st.button(nav_labels[target], key=f"nav_{target}",
                         type="primary" if active else "secondary",
                         use_container_width=True):
                ss.page = target
                st.rerun()
st.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)
page = ss.get("page", "Home")

a, w, rk = ranking()
sdf = se.compare_scenarios(scen_dict())
swing_df = se.sensitivity_analysis(scen_dict()["Baseline"])[1]


def questions():
    q = [f"What evidence supports the '{max(w, key=w.get)}' weight?" if w else "Which criteria matter most?",
         f"How could '{swing_df.iloc[0]['variable']}' be validated with real data (pilot, quotes, interviews)?",
         "What budget, time or regulatory constraints apply? None have been supplied.",
         "What do competitors charge and how many customers do they win?", "What are tax, cash-timing and working-capital effects?"]
    return q


if page == "Home":
    st.markdown("""
    <div class="mono">Independent decision research &nbsp; / &nbsp; Field note 001</div>
    <div style="height:1.2rem"></div>
    <div class="hero">HELIX<span style="color:#c4472d">.</span></div>
    <div class="mono" style="font-size:.78rem">The Intelligence Lab &nbsp;—&nbsp; A tool for thinking in public</div>
    <div style="height:1.8rem"></div>
    """, unsafe_allow_html=True)
    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.markdown("<div class='quote'>Every decision has a structure.<br>Every assumption has consequences.</div>", unsafe_allow_html=True)
        st.markdown("HELIX is a place to slow a decision down. Pull it apart, weigh what matters, test a few possible futures, and see which parts of your reasoning are evidence — and which are still a guess.")
        st.markdown("<div style='height:.7rem'></div><div class='mono'>Compare / interrogate / simulate / explain</div>", unsafe_allow_html=True)
        b1, b2 = st.columns([1, 1])
        b1.button("Enter the lab  ↗", type="primary", on_click=go_to, args=("Decision Studio",), use_container_width=True)
        b2.button("Read the decision map", on_click=go_to, args=("Decision Map",), use_container_width=True)
    with right:
        st.markdown("""
        <div style="position:relative; min-height:300px; padding:1.1rem 0 1rem 1.2rem; border-left:1px solid #cfc7b9; overflow:hidden">
          <div class="mono">A note on uncertainty</div>
          <svg viewBox="0 0 420 230" role="img" aria-label="Loose hand-drawn ink paths representing a decision unfolding" style="width:100%;height:auto;display:block;margin:.7rem 0">
            <path d="M18 156 C65 112, 79 180, 124 128 S187 48, 222 106 S284 192, 326 112 S375 69, 405 86" fill="none" stroke="#c4472d" stroke-width="2.2" stroke-linecap="round"/>
            <path d="M15 178 C59 145, 86 207, 133 154 S188 78, 227 128 S282 210, 333 135 S377 94, 407 109" fill="none" stroke="#66858a" stroke-width="1.2" stroke-linecap="round" opacity=".85"/>
            <path d="M26 86 C70 57, 91 101, 132 82 S184 19, 224 66 S292 144, 337 76 S380 39, 400 48" fill="none" stroke="#858b69" stroke-width="1.1" stroke-linecap="round" opacity=".8"/>
            <path d="M65 30 C83 39, 79 58, 95 62 M260 23 C246 38, 254 49, 269 56 M348 176 C363 166, 376 174, 382 190" fill="none" stroke="#77736a" stroke-width="1" stroke-linecap="round" stroke-dasharray="2 5"/>
          </svg>
          <div style="display:flex;justify-content:space-between;gap:1rem;border-top:1px solid #cfc7b9;padding-top:.8rem">
            <div><div class="mono">01 / The model</div><div style="font-family:'Bodoni Moda',serif;font-size:1.25rem">What do we know?</div></div>
            <div><div class="mono">02 / The tension</div><div style="font-family:'Bodoni Moda',serif;font-size:1.25rem">What could change?</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div><hr><div class='mono'>Inside this edition</div>", unsafe_allow_html=True)
    tiles = st.columns(4)
    sections = [
        ("01", "Decision Studio", "Make the trade-offs visible.", "Decision Studio"),
        ("02", "Scenario Lab", "Stress-test the numbers.", "Scenario Lab"),
        ("03", "Assumption Challenger", "Separate evidence from belief.", "Assumption Challenger"),
        ("04", "Decision Report", "Leave with a record of your reasoning.", "Decision Report"),
    ]
    for col, (num, title, desc, target) in zip(tiles, sections):
        with col:
            st.markdown(f"<div class='mono'>{num} &nbsp; / &nbsp; MODULE</div><div style='font-family:Bodoni Moda,serif;font-size:1.35rem;line-height:1.1;margin:.55rem 0'>{title}</div><div style='font-size:.9rem;color:{GREY};min-height:3rem'>{desc}</div>", unsafe_allow_html=True)
            st.button("Open ↗", key=f"home_{num}", on_click=go_to, args=(target,), use_container_width=True)
    st.markdown("<hr><div class='mono'>Live case file / illustrative data only</div>", unsafe_allow_html=True)
    st.subheader(ss.title)
    m = st.columns(3)
    if rk:
        m[0].metric("Current model leader", rk[0][0])
        m[1].metric("Weighted score", f"{rk[0][1]:.2f} / 10")
    m[2].metric("Scenarios with negative estimated operating profit", int((sdf.operating_profit < 0).sum()))
    st.caption("The sample case is fictional. Rankings reflect the entered scores and weights; they are not objectively correct answers.")

elif page == "Live Intelligence":
    st.markdown("<div class='mono'>Field notes / live research + AI analysis</div>", unsafe_allow_html=True)
    st.title("Live Intelligence")
    st.markdown("Bring a real question. HELIX researches current sources, weighs trade-offs, challenges assumptions, and turns the findings into a decision brief.")

    # A compact, actionable orientation panel instead of a wall of setup text.
    intro = st.columns([1.15, 1, 1])
    with intro[0]:
        st.markdown("<div class='featureline'><div class='num'>01</div><div><div class='label'>Investigate</div><div class='detail'>Search current web sources.</div></div></div>", unsafe_allow_html=True)
    with intro[1]:
        st.markdown("<div class='featureline'><div class='num'>02</div><div><div class='label'>Interrogate</div><div class='detail'>Stress-test the assumptions.</div></div></div>", unsafe_allow_html=True)
    with intro[2]:
        st.markdown("<div class='featureline'><div class='num'>03</div><div><div class='label'>Decide</div><div class='detail'>Leave with a validation plan.</div></div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    with st.expander("Before you begin — API access and privacy", expanded=not bool(os.environ.get("GEMINI_API_KEY"))):
        st.warning("Live research requires a Gemini API key. Availability and usage limits depend on your Google AI Studio account. For safety, the key is used at runtime and should never be pasted into source code or committed to GitHub.")
        st.caption("Your question and context are sent to the selected model for analysis. Avoid including passwords, private customer data, or other sensitive information.")

    env_key = os.environ.get("GEMINI_API_KEY", "")
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = ""
    default_key = env_key or secret_key
    api_key = st.text_input("Gemini API key", type="password", value=default_key,
                            help="For repeat use, set GEMINI_API_KEY as an environment variable or Streamlit secret.")
    model_name = st.selectbox("AI model", ["gemini-2.5-flash", "gemini-2.5-pro"], index=0,
                              help="Model availability depends on your API account. If the selected model is unavailable, try the other option.")

    st.markdown("### What are we investigating?")
    st.caption("Start with one of these, or write your own question. The sample prompts are editable starting points, not recommendations.")
    prompt_cols = st.columns(3)
    presets = [
        ("01 / STARTUP", "Compare three business ideas", "I have limited starting capital and an interest in AI automation. Compare starting an AI automation agency, building a digital product, and launching a niche e-commerce business. Research current market conditions, entry barriers, startup costs, risks, and low-cost validation experiments."),
        ("02 / MARKET", "Understand a market", "Research the current market for AI automation services for small businesses in India. Identify credible demand signals, common use cases, competitors, pricing evidence where available, barriers to entry, and what remains uncertain."),
        ("03 / DECISION", "Challenge my plan", "Critically evaluate a business plan I am considering. Identify its strongest case, strongest counterargument, hidden assumptions, missing evidence, key risks, and the cheapest experiment that could disprove the idea."),
    ]
    for col, (label, title, prompt) in zip(prompt_cols, presets):
        with col:
            st.markdown(f"<div class='card'><div class='mono'>{label}</div><div style='font-family:Bodoni Moda,serif;font-size:1.25rem;margin:.35rem 0'>{title}</div><div style='font-size:.84rem;color:{GREY}'>Use as a starting point</div></div>", unsafe_allow_html=True)
            if st.button("Use prompt ↗", key=f"live_preset_{label}", use_container_width=True):
                ss.live_question_input = prompt
                st.rerun()

    ss.setdefault("live_question_input", ss.get("live_question", ""))
    question = st.text_area("Decision or research question", key="live_question_input", height=135,
                            placeholder="Example: With ₹2 lakh and 10 hours per week, should I start an AI automation agency, sell a digital product, or build a niche online store?")
    with st.expander("Add context (optional, but improves the analysis)", expanded=bool(ss.get("live_context_input", ""))):
        context = st.text_area("Your situation, constraints, and priorities", key="live_context_input", height=105,
                               placeholder="Budget, location, timeline, experience, risk tolerance, time available, what success means…")
    local_snapshot = ""
    if rk:
        local_snapshot = (
            f"Decision title: {ss.title}\nDescription: {ss.desc}\n"
            f"Current weighted ranking: {rk}\nCriteria weights: {w}\n"
            f"Scenario outputs (calculated by HELIX): {sdf[['Scenario','revenue','gross_profit','operating_profit']].to_dict(orient='records')}"
        )
    run_col, hint_col = st.columns([1, 2.4])
    with run_col:
        run_clicked = st.button("Run investigation  ↗", type="primary", use_container_width=True)
    with hint_col:
        st.caption("The investigation can take a little while. It uses Google Search grounding and may incur API charges.")

    if run_clicked:
        if not api_key.strip():
            st.error("Add your Gemini API key above first.")
        elif not question.strip():
            st.error("Write a decision or choose a starter prompt first.")
        else:
            ss.live_question, ss.live_context = question, context
            with st.status("HELIX is investigating…", expanded=True) as status:
                st.write("Searching for current sources")
                st.write("Comparing trade-offs and counterarguments")
                st.write("Building an evidence-aware decision brief")
                try:
                    result = run_live_investigation(api_key, question, context, model_name, local_snapshot)
                    ss.live_result = result
                    ss.live_followup_result = None
                    status.update(label="Investigation complete", state="complete", expanded=False)
                except Exception as exc:
                    status.update(label="Investigation could not be completed", state="error", expanded=True)
                    st.error(f"HELIX could not complete the investigation: {exc}")
                    st.caption("Check that your Gemini API key is valid, your account has access to the model, and your usage limits allow requests.")

    result = ss.get("live_result")
    if result:
        st.markdown("---")
        st.markdown("<div class='mono'>Investigation file / latest result</div>", unsafe_allow_html=True)
        meta = st.columns(3)
        meta[0].metric("Status", "Complete")
        meta[1].metric("Model", result.get("model", "Unknown"))
        meta[2].metric("Sources captured", len(result.get("sources", [])))
        result_tabs = st.tabs(["Decision brief", "Source register", "Ask a follow-up"])
        with result_tabs[0]:
            st.markdown(result.get("text", ""))
            st.download_button("Download decision brief (.md)", result.get("text", ""), file_name="helix_live_investigation.md", mime="text/markdown", use_container_width=True)
        with result_tabs[1]:
            sources = result.get("sources", [])
            if sources:
                for i, source in enumerate(sources, 1):
                    st.markdown(f"**{i:02d} / {source['title']}**  ")
                    st.markdown(f"{source['url']}")
                    st.markdown("<hr style='margin:.7rem 0'>", unsafe_allow_html=True)
            else:
                st.info("No structured source links were captured from this response. Check the citations in the decision brief and verify important claims at the original sources.")
        with result_tabs[2]:
            followup = st.text_area("What should HELIX investigate next?", key="live_followup_input", height=90,
                                    placeholder="What evidence would most likely change the recommendation?")
            if st.button("Investigate follow-up ↗", key="live_followup_button", type="primary"):
                if not followup.strip():
                    st.info("Write a follow-up question first.")
                else:
                    with st.spinner("Investigating the follow-up against current sources…"):
                        try:
                            follow_result = run_live_investigation(
                                api_key, followup,
                                context=(context + "\n\nFollow-up to the previous HELIX investigation. Use this previous brief as context:\n" + result.get("text", ""))[:18000],
                                model=model_name, local_analysis=local_snapshot)
                            ss.live_followup_result = follow_result
                        except Exception as exc:
                            st.error(f"Follow-up failed: {exc}")
            if ss.get("live_followup_result"):
                st.markdown(ss.live_followup_result.get("text", ""))
                st.download_button("Download follow-up (.md)", ss.live_followup_result.get("text", ""), file_name="helix_follow_up.md", mime="text/markdown")
        st.caption("Research is a snapshot, not a guarantee. Verify important claims at original sources. AI can be wrong; citations do not guarantee that every claim is supported.")

elif page == "Decision Map":
    st.title("Decision Map")
    st.caption("Solid links are supplied by you. Dotted links are derived from calculations or formulas. "
               "Nothing is inferred beyond this; any proposed relationship would be labelled a hypothesis.")
    if not rk:
        st.info("Add at least two alternatives and one criterion in Decision Studio to draw the map.")
        st.stop()
    N = {"D": dict(label="Decision", x=0, y=0, g="Decision", d=ss.title)}
    def ring(ids, labels, g, ang, spread, r, details):
        for i, (k, lab, d) in enumerate(zip(ids, labels, details)):
            t = math.radians(ang + (i - (len(ids) - 1) / 2) * spread)
            N[k] = dict(label=lab, x=r * math.cos(t), y=r * math.sin(t), g=g, d=d)
    nw = de.normalised_weight_map(w)
    ring([f"O{c}" for c in w], list(w), "Objective", 180, 30, 1.0, [f"Weight {nw[c]*100:.0f}% (your assumption)" for c in w])
    ring([f"A{n}" for n in a], [n[:22] for n in a], "Alternative", 0, 30, 1.0, [f"Weighted score {s:.2f}/10" for n, s in rk for _ in [0]] if False else [f"Weighted score {dict(rk)[n]:.2f}/10" for n in a])
    ring(["K"], ["Constraints"], "Constraint", 90, 0, 1.0, ["UNKNOWN: no constraints supplied yet."])
    ring([f"F{f}" for f in SF], ["Customers", "Order value", "Margin", "Opex"], "Financial variable", 270, 22, 1.0, [f"Baseline input: {scen_dict()['Baseline'][f]:,.0f}" for f in SF])
    ring([f"P{n}" for n in SCEN], list(SCEN), "Outcome", 270, 30, 1.9, [f"Est. operating profit {inr(sdf.set_index('Scenario').operating_profit[n])}/month" for n in SCEN])
    solid = [("D", k) for k in N if k[0] in "OAK" and k != "D"]
    dotted = [(f"A{n}", f"O{c}") for n in a for c in w] + [(f"F{f}", f"P{n}") for f in SF for n in SCEN]
    fig = go.Figure()
    for edges, dash, col, wd in [(dotted, "dot", "#4a443b", 1), (solid, "solid", LILAC, 1.5)]:
        xs, ys = [], []
        for u, v in edges:
            xs += [N[u]["x"], N[v]["x"], None]; ys += [N[u]["y"], N[v]["y"], None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=col, width=wd, dash=dash), hoverinfo="skip", showlegend=False))
    gcol = {"Decision": INK, "Objective": LILAC, "Alternative": CYAN, "Constraint": GREY, "Financial variable": "#d59a58", "Outcome": "#858b69"}
    for g, col in gcol.items():
        ks = [k for k in N if N[k]["g"] == g]
        fig.add_trace(go.Scatter(x=[N[k]["x"] for k in ks], y=[N[k]["y"] for k in ks], mode="markers+text", name=g,
                                 text=[N[k]["label"] for k in ks], textposition="top center", textfont=dict(size=11),
                                 marker=dict(size=26 if g == "Decision" else 16, color=col, symbol="circle-open" if g == "Constraint" else "circle"),
                                 hovertext=[N[k]["d"] for k in ks], hoverinfo="text"))
    fig.update_xaxes(visible=False, range=[-2, 2]); fig.update_yaxes(visible=False, range=[-2.4, 1.5])
    st.plotly_chart(style(fig, 560), width="stretch")
    pick = st.selectbox("Inspect a node", [k for k in N], format_func=lambda k: f"{N[k]['g']}: {N[k]['label']}")
    st.markdown(f"<div class='card'><span class='mono'>{N[pick]['g']}</span><br><b>{N[pick]['label']}</b><br>{N[pick]['d']}</div>", unsafe_allow_html=True)

elif page == "Decision Studio":
    st.title("Decision Studio")
    st.caption("Weighted-sum multi-criteria analysis. The ranking reflects your weights and subjective scores, not an objectively correct answer.")
    ss.title = st.text_input("Decision title", ss.title)
    ss.desc = st.text_area("Description", ss.desc, height=68)
    l, r_ = st.columns([2, 3])
    with l:
        st.markdown("<div class='mono'>Criteria weights</div>", unsafe_allow_html=True)
        for c in ss.crits:
            st.slider(c, 0, 100, key=f"w|{c}")
        nc = st.text_input("Add criterion")
        if st.button("Add criterion") and nc.strip() and nc not in ss.crits:
            ss.crits.append(nc.strip()); ss[f"w|{nc.strip()}"] = 10
            for n in ss.alts: ss[f"s|{n}|{nc.strip()}"] = 5
            st.rerun()
        if len(ss.crits) > 1:
            rc = st.selectbox("Remove criterion", ss.crits, index=None, placeholder="Choose")
            if rc and st.button("Remove criterion"):
                ss.crits.remove(rc); st.rerun()
    with r_:
        st.markdown("<div class='mono'>Scores by alternative (1-10)</div>", unsafe_allow_html=True)
        tabs = st.tabs(ss.alts)
        for t, n in zip(tabs, ss.alts):
            with t:
                for c in ss.crits:
                    ss.setdefault(f"s|{n}|{c}", 5)
                    st.slider(c, 1, 10, key=f"s|{n}|{c}")
        na = st.text_input("Add alternative")
        cc = st.columns(2)
        if cc[0].button("Add alternative") and na.strip() and na not in ss.alts:
            ss.alts.append(na.strip()); st.rerun()
        if len(ss.alts) > 2:
            ra = cc[1].selectbox("Remove alternative", ss.alts, index=None, placeholder="Choose")
            if ra and cc[1].button("Remove alternative"):
                ss.alts.remove(ra); st.rerun()
    a, w, rk = ranking()
    if not rk:
        st.info("Add at least two alternatives and one criterion.")
        st.stop()
    if sum(w.values()) == 0:
        st.warning("All weights are zero; equal weights are used.")
    st.markdown("---")
    cols = st.columns(len(rk))
    for col, (n, s) in zip(cols, rk):
        col.markdown(f"<div class='card'><span class='mono'>rank {rk.index((n, s)) + 1}</span><br>{n}<div class='big' style='font-size:1.8rem'>{s:.2f}</div></div>", unsafe_allow_html=True)
    con = de.contributions(a, w)
    long = pd.DataFrame([{"Alternative": n, "Criterion": c, "Contribution": v} for n, d in con.items() for c, v in d.items()])
    c1, c2 = st.columns([3, 2])
    c1.plotly_chart(style(px.bar(long, x="Contribution", y="Alternative", color="Criterion", orientation="h",
                                 title="What builds each score", color_discrete_sequence=PAL)), width="stretch")
    heat = pd.DataFrame(con).T
    c2.plotly_chart(style(px.imshow(heat, color_continuous_scale=[[0, SURF], [1, LILAC]], aspect="auto", title="Criterion influence")), width="stretch")
    st.markdown("<div class='mono'>Why the leader leads</div>", unsafe_allow_html=True)
    for c, d in de.top_drivers(a, w)[:3]:
        st.write(f"- **{c}**: {d:+.2f} points vs runner-up")
    stab = de.ranking_stability(a, w)
    (st.success if stab["stable"] else st.warning)("Leader unchanged under ±10-point weight shifts." if stab["stable"]
                                                    else f"Leader changes under {len(stab['changes'])} tested weight shift(s).")

elif page == "Scenario Lab":
    st.title("Scenario Lab")
    st.caption("Simplified monthly estimates in INR. Operating profit is not net profit or cash flow.")
    cols = st.columns(3)
    rng = dict(customers=(0, 1000, 10), aov=(0, 10000, 50), margin=(0, 100, 1), opex=(0, 500000, 5000))
    lab = dict(customers="Monthly customers", aov="Avg order value (₹)", margin="Gross margin %", opex="Monthly opex (₹)")
    for col, n in zip(cols, SCEN):
        with col:
            st.markdown(f"<div class='mono'>{n}</div>", unsafe_allow_html=True)
            for f in SF:
                lo, hi, stp = rng[f]
                st.slider(lab[f], lo, hi, step=stp, key=f"sc|{n}|{f}")
    sdf = se.compare_scenarios(scen_dict())
    sel = st.radio("Headline scenario", list(SCEN), horizontal=True)
    row = sdf.set_index("Scenario").loc[sel]
    h = st.columns([2, 3])
    h[0].markdown(f"<div class='mono'>Estimated operating profit / month</div><div class='big'>{inr(row.operating_profit)}</div>", unsafe_allow_html=True)
    h[1].write(f"Revenue {inr(row.revenue)} = {row.customers:,.0f} customers × {inr(row.aov)}. Gross profit {inr(row.gross_profit)} at "
               f"{row.margin:.0f}% margin, less {inr(row.opex)} operating expenses. Operating margin {row.operating_margin:.1f}%. "
               "All inputs are your assumptions; a positive figure does not show viability.")
    fig = go.Figure()
    for col, name, colr in [("revenue", "Revenue", CYAN), ("gross_profit", "Gross profit", "#d8c9ff"), ("operating_profit", "Est. operating profit", LILAC)]:
        fig.add_bar(x=sdf.Scenario, y=sdf[col], name=name, marker_color=colr)
    st.plotly_chart(style(fig.update_layout(barmode="group", title="Scenario comparison (₹ per month)")), width="stretch")
    diffs = [lab[f] for f in SF if sdf[f].nunique() > 1]
    st.write("Assumptions differing across scenarios: " + (", ".join(diffs) or "none") + ".")
    st.markdown("---")
    st.subheader("Sensitivity")
    c = st.columns(2)
    pick = c[0].selectbox("Base scenario", list(SCEN))
    pct = c[1].slider("Range around base (±%)", 10, 50, 30, step=5) / 100
    with st.spinner("Recomputing"):
        df, swing = se.sensitivity_analysis(scen_dict()[pick], pct=pct)
    st.plotly_chart(style(px.line(df, x="change_pct", y="operating_profit", color="variable", markers=True,
                                  labels={"change_pct": "Change in input (%)", "operating_profit": "Est. operating profit (₹)"},
                                  color_discrete_sequence=PAL)), width="stretch")
    st.dataframe(swing.assign(profit_swing=swing.profit_swing.map(inr)).rename(columns={"variable": "Input", "profit_swing": "Profit swing"}), hide_index=True)
    st.caption("Each input varied alone, others fixed (margin capped at 100%). This is sensitivity analysis, not Monte Carlo, and ignores input correlation.")

elif page == "Assumption Challenger":
    st.title("Assumption Challenger")
    st.caption("Separates what was calculated from what was assumed, inferred or is still unknown.")
    if not rk:
        st.info("Complete the decision setup first.")
        st.stop()
    stab = de.ranking_stability(a, w)
    top_w = max(w, key=w.get)
    items = {
        "OBSERVED": [f"Model ranks {rk[0][0]} first ({rk[0][1]:.2f}/10).", *[f"{r.Scenario}: est. operating profit {inr(r.operating_profit)}/month." for r in sdf.itertuples()]],
        "ASSUMED": [f"Weight on '{top_w}' is {de.normalised_weight_map(w)[top_w]*100:.0f}%.", "All 1-10 scores are subjective judgements.",
                    *[f"{r.Scenario}: {r.customers:,.0f} customers at {inr(r.aov)}, {r.margin:.0f}% margin, opex {inr(r.opex)}." for r in sdf.itertuples()]],
        "INFERRED": ["Leader is robust to ±10-point weight shifts." if stab["stable"] else f"Leader may depend on weights (hypothesis): {len(stab['changes'])} shifts change it.",
                     f"'{swing_df.iloc[0]['variable']}' appears most influential on profit within the tested range (hypothesis)."],
        "UNKNOWN": ["Budget and other constraints.", "Evidence behind scores and inputs.", "Customer acquisition cost and churn.", "Taxes, cash timing, working capital.", "Competitor behaviour."]}
    cols = st.columns(4)
    for col, (k, v) in zip(cols, items.items()):
        col.markdown(f"<span class='tag {k}'>{k}</span>", unsafe_allow_html=True)
        for t in v:
            col.markdown(f"<div class='card' style='font-size:.88rem'>{t}</div>", unsafe_allow_html=True)
    st.subheader("Questions to ask yourself")
    for q in questions():
        st.write(f"- {q}")

elif page == "Decision Report":
    if not rk:
        st.info("Complete the decision setup first.")
        st.stop()
    fs = ie.generate_findings(a, w, sdf, swing_df)
    md = ie.full_report(ss.title, ss.desc, rk, sdf, swing_df, fs, questions())
    st.markdown("<div class='mono'>HELIX decision report</div>", unsafe_allow_html=True)
    st.title(ss.title)
    st.write(ss.desc)
    st.caption("Built only from the calculations in this session. Deterministic; no external AI used.")
    st.header("Ranked alternatives")
    st.plotly_chart(style(px.bar(x=[s for _, s in rk], y=[n for n, _ in rk], orientation="h", color_discrete_sequence=[LILAC],
                                 labels={"x": "Weighted score (/10)", "y": ""}), 220), width="stretch")
    st.header("Scenario results")
    st.dataframe(sdf[["Scenario", "revenue", "gross_profit", "operating_profit"]].set_index("Scenario").map(inr))
    st.header("Findings")
    for f in fs:
        st.markdown(f"<span class='tag {'OBSERVED' if f['category']=='Calculated' else 'INFERRED' if f['category']=='Interpretation' else 'ASSUMED'}'>{f['category'].upper()}</span> **{f['title']}**", unsafe_allow_html=True)
        st.write(f"{f['observation']} {f['interpretation']} *Next:* {f['next_step']}")
    st.header("Questions requiring investigation")
    for q in questions():
        st.write(f"- {q}")
    st.header("Limitations")
    st.write("Scores, weights and inputs are user assumptions. Operating profit is a simplified estimate. Sensitivity ignores correlation. Not financial, legal or investment advice.")
    d = st.columns(2)
    d[0].download_button("Download report (.md)", md, "helix_report.md", "text/markdown")
    d[1].download_button("Download report (.txt)", md, "helix_report.txt", "text/plain")

else:
    st.title("Methodology")
    st.markdown("""
**Weighted-sum MCDA.** Scores (1-10) × normalised weights, summed. All-zero weights fall back to equal weights.

**Scenario model.** Revenue = customers × order value; gross profit = revenue × margin; estimated operating profit = gross profit − operating expenses.
Excludes tax, interest, working capital and cash timing.

**Sensitivity.** One input varied at a time across a stated range; the swing in profit ranks influence. Not Monte Carlo.

**Observed / Assumed / Inferred / Unknown.** Calculated results are observed; user inputs are assumptions; derived explanations are hypotheses; gaps are listed as unknown.

**Live Intelligence.** Optional Gemini API integration with Google Search grounding. Requires the user's API key and may incur API charges. It produces research-assisted analysis; verify citations and claims.

**Limitations.** Rankings are model outputs, not objectively correct decisions. The sample case is fictional. HELIX is a prototype, not professional advice.
""")
