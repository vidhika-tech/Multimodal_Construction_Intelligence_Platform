# Multimodal Construction Intelligence Platform

A Streamlit capstone prototype with four modules:
1. Site Safety & PPE Audit
2. Crack Diagnostics & Structural Integrity
3. Planning & Real Estate Valuation
4. Daily Site Assistant & Weather-Aware Advisory

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run `pip install -r requirements.txt`
4. Run `streamlit run app.py`
5. Open the local URL shown in the terminal.

## Gemini API key
The sidebar accepts a Google Gemini API key as a password field. The key is used only for the current session and is not written to a file by this app. Without a key, the app runs in demo mode. Never commit API keys to GitHub.

## Deploy
Push `app.py`, `requirements.txt`, and `README.md` to a GitHub repository. On Streamlit Community Cloud, choose the repository and `app.py` as the main file. Add secrets only through the platform's secrets settings if you later change the app to use persistent secrets.

## Important limitations
- Demo outputs are illustrative and do not represent actual image analysis.
- AI outputs may be wrong and require professional verification.
- The safety module is not an OSHA/IS compliance certification.
- Crack image analysis cannot establish structural integrity; consult a qualified structural engineer.
- Planning and material calculations use simplified assumptions, not a formal valuation, bill of quantities, or engineering design.
- Weather is selected manually; there is no live weather API or database.
