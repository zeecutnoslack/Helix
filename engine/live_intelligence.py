"""Optional Gemini AI + Google Search grounded research layer for HELIX.

Requires a Gemini API key. Supply it at runtime or through GEMINI_API_KEY;
never commit keys to source control.
"""
from __future__ import annotations

from typing import Any

SYSTEM_INSTRUCTIONS = """You are HELIX, an evidence-aware decision intelligence analyst.
Your job is to help the user reason, not to pretend certainty.

For every investigation:
- Use Google Search grounding for current web research and cite sources where available.
- Prefer primary sources, official statistics, company filings, research papers, and reputable reporting.
- Separate verified sourced claims, user-provided information, model calculations, assumptions, interpretations, and unknowns.
- Never invent citations, data, quotes, prices, or market statistics. If evidence is unavailable, say so.
- Challenge the user's framing and identify the strongest counterargument, missing information, and what evidence could change the recommendation.
- For business comparisons, state criteria and trade-offs; don't claim a weighted score is objectively correct.
- Give a practical next-step plan and explain uncertainty.
- Do not provide legal, medical, investment, or other professional advice as a substitute for a qualified professional.
- Be clear, specific, analytical, and concise. Use Markdown headings.
"""

DEFAULT_MODEL = "gemini-3.8-flash"


def run_live_investigation(
    api_key: str,
    question: str,
    context: str = "",
    model: str = DEFAULT_MODEL,
    local_analysis: str = "",
) -> dict[str, Any]:
    """Run a Gemini investigation using the Interactions API and Google Search."""
    if not api_key or not api_key.strip():
        raise ValueError("Add your Gemini API key to run Live Intelligence.")
    if not question or not question.strip():
        raise ValueError("Enter a decision or question first.")

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "The Google Gen AI package is missing or outdated. Run: "
            "python -m pip install --upgrade google-genai"
        ) from exc

    # Remap the retired default in case an older UI/config still passes it in.
    if not model or model.strip() in {"gemini-2.5-flash", "models/gemini-2.5-flash"}:
        model = DEFAULT_MODEL
    model = model.strip().removeprefix("models/")

    user_input = f"""{SYSTEM_INSTRUCTIONS}

Investigate this decision using Google Search for current web research.

USER'S DECISION / QUESTION:
{question.strip()}

ADDITIONAL CONTEXT FROM USER:
{context.strip() or 'No additional context supplied.'}

CURRENT HELIX CALCULATIONS (if present; these are model outputs, not external facts):
{local_analysis.strip() or 'No local calculation snapshot supplied.'}

Required report structure:
1. Executive read (short, conditional recommendation if evidence permits)
2. What current research says (with visible citations and dates where available)
3. Options and trade-offs
4. Assumption challenge (at least 3 targeted questions)
5. Evidence ledger: sourced facts / user inputs / calculations / assumptions / unknowns
6. Risks and what could change the conclusion
7. A practical 3-step validation plan
8. Sources

Search the web before drawing conclusions. If sources conflict or are weak, disclose that. Do not fabricate numerical estimates; label any illustrative scenario as illustrative."""

    client = genai.Client(api_key=api_key.strip())
    try:
        interaction = client.interactions.create(
            model=model,
            input=user_input,
            tools=[{"type": "google_search"}],
        )
    except Exception as exc:
        message = str(exc)
        if "404" in message or "NOT_FOUND" in message:
            raise RuntimeError(
                f"Gemini model/API request failed for {model}. Confirm the model is available "
                "to your API key and that google-genai is up to date. Original error: "
                f"{message}"
            ) from exc
        raise

    answer_text = getattr(interaction, "output_text", "") or ""
    sources: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    # Interactions API returns citations as annotations on model-output text blocks.
    try:
        for step in (getattr(interaction, "steps", None) or []):
            if getattr(step, "type", "") != "model_output":
                continue
            for block in (getattr(step, "content", None) or []):
                for annotation in (getattr(block, "annotations", None) or []):
                    url = (
                        getattr(annotation, "url", None)
                        or getattr(annotation, "uri", None)
                    )
                    title = getattr(annotation, "title", None)
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        sources.append({"title": title or url, "url": url})
    except Exception:
        # Keep the answer usable even if the SDK's annotation shape changes.
        pass

    if not answer_text.strip():
        raise RuntimeError(
            "Gemini returned no text. Confirm the model is enabled for your API key "
            "and update google-genai with: python -m pip install --upgrade google-genai"
        )

    return {
        "text": answer_text,
        "sources": sources,
        "model": model,
        "response_id": getattr(interaction, "id", "") or "",
    }
