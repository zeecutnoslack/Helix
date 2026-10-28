# HELIX — The Intelligence Lab

An editorial decision-support prototype combining weighted multi-criteria analysis, scenario modelling, sensitivity analysis, assumption challenges, and optional Gemini-powered live AI-assisted web research.

## Run locally

1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Launch the app:
   ```bash
   python -m streamlit run app.py
   ```
5. Open the local URL printed in the terminal, usually `http://localhost:8501`.

## Live Intelligence

The **Live Intelligence** page uses the Gemini API with Google Search grounding. It requires a Gemini API key. Availability, free quota, and any billing depend on your Google AI Studio account and selected model. You can enter a key at runtime or set `GEMINI_API_KEY` as an environment variable. Never commit keys to GitHub. Avoid sending private or sensitive information.

The available models and usage limits depend on your Google AI Studio account. If a selected model is unavailable, choose another model in the app. Live research results can be wrong; verify important claims at original sources.

## Features

- Decision Studio: criteria weights, subjective scores, ranking, contribution charts, and stability checks.
- Decision Map: visual map of decision inputs, criteria, alternatives, and outcomes.
- Scenario Lab: estimated revenue, gross profit, operating profit, and one-variable-at-a-time sensitivity analysis.
- Assumption Challenger: observed, assumed, inferred, and unknown information.
- Decision Report: downloadable report generated from calculated results.
- Live Intelligence: optional web research, AI synthesis, source register, and follow-up investigation.

## Tests

```bash
python -m pytest -q
```

The decision scores and scenario outputs are decision-support estimates, not objectively correct answers. Financial modelling is simplified and excludes tax, working capital, and cash timing. HELIX is a prototype, not professional advice.
