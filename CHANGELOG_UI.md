# HELIX UI/UX update

This update focuses on clearer interaction and a more usable Live Intelligence workflow while preserving the existing decision and scenario engines.

## Changes
- Fixed primary-button text contrast so labels remain visible on dark buttons.
- Added clearer focus states, input styling, hover feedback, and reduced-motion support remains in place.
- Reworked Live Intelligence into three visible stages: Investigate, Interrogate, Decide.
- Added three starter prompts that populate the question field for quick experimentation.
- Moved API access/privacy notes into an expandable panel.
- Made optional context collapsible to reduce initial visual clutter.
- Added a visible investigation progress/status sequence.
- Organized results into Decision Brief, Source Register, and Ask a Follow-up tabs.
- Added more explicit privacy, source verification, and API billing guidance.

## Run
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The live investigation feature requires an OpenAI API key and API account access. A successful live API call and visual browser rendering must be verified on the user's machine.
