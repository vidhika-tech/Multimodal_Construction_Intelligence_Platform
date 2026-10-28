import json
import os
from datetime import datetime
from typing import Any

import streamlit as st

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .stApp { background: linear-gradient(135deg, #f6f8fc 0%, #eef3f8 100%); }
  [data-testid="stSidebar"] { background: #122238; }
  [data-testid="stSidebar"] * { color: #f5f7fb !important; }
  .hero { padding: 1.4rem 1.6rem; border-radius: 18px; color: white;
          background: linear-gradient(115deg,#142b45,#176b75); margin-bottom: 1rem; }
  .hero h1 { margin: 0 0 .3rem 0; font-size: 2rem; }
  .hero p { margin: 0; opacity: .9; }
  .small-note { color: #64748b; font-size: .88rem; }
  div[data-testid="stMetric"] { background: white; border: 1px solid #e3eaf2;
      padding: 14px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🏗️ Construction AI")
st.sidebar.caption("Skill Wallet · Capstone Project 1")
api_key = st.sidebar.text_input(
    "Google Gemini API key",
    type="password",
    help="Key is used only for this session. Do not paste it into source code or upload it to GitHub.",
)
demo_mode = not bool(api_key.strip())
st.sidebar.info("Demo mode is active." if demo_mode else "Gemini mode is selected.")
st.sidebar.markdown("---")
st.sidebar.subheader("Architecture overview")
st.sidebar.markdown(
    "• Streamlit UI\n\n"
    "• Gemini multimodal analysis (optional)\n\n"
    "• Rule-based demo fallback\n\n"
    "• Session-only state; no external database"
)
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Site Safety & PPE Audit", "Crack Diagnostics",
     "Planning & Valuation", "Daily Site Assistant"],
)

def gemini_analyze(prompt: str, uploaded_file=None) -> str | None:
    """Call Gemini when configured; return None if unavailable or request fails."""
    if not api_key.strip() or genai is None:
        return None
    try:
        client = genai.Client(api_key=api_key.strip())
        contents: list[Any] = [prompt]
        if uploaded_file is not None:
            contents.append(types.Part.from_bytes(
                data=uploaded_file.getvalue(),
                mime_type=uploaded_file.type or "image/jpeg"
            ))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )
        return getattr(response, "text", None) or None
    except Exception as exc:
        st.warning(f"Gemini analysis could not run, so the app will use demo output. Details: {exc}")
        return None

def try_json(text: str):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return None

def show_json_download(data: dict, filename: str):
    st.download_button(
        "⬇️ Download JSON report",
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name=filename,
        mime="application/json",
    )

def metric_status(status: str):
    if status.lower() in ("pass", "safe", "normal", "low"):
        st.success(status)
    elif status.lower() in ("review", "medium", "caution"):
        st.warning(status)
    else:
        st.error(status)

st.markdown(
    '<div class="hero"><h1>Multimodal Construction Intelligence Platform</h1>'
    '<p>AI-assisted site safety, structural observations, project planning, and daily guidance.</p></div>',
    unsafe_allow_html=True,
)
if demo_mode:
    st.caption("Demo mode: outputs are illustrative rules-based examples, not certified inspections.")
else:
    st.caption("Gemini mode: AI-generated outputs require professional verification.")

if page == "Overview":
    st.subheader("Project dashboard")
    st.write("A single workspace for early-stage construction insights. Upload images in the audit tools, "
             "estimate project inputs, and generate practical safety guidance.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Modules", "4")
    c2.metric("AI provider", "Gemini optional")
    c3.metric("Database", "None")
    c4.metric("Mode", "Demo" if demo_mode else "Gemini")
    st.markdown("### What you can do")
    cols = st.columns(2)
    with cols[0]:
        st.markdown("**🦺 Site Safety & PPE Audit**")
        st.write("Review a site photo for visible PPE and potential hazards.")
        st.markdown("**🧱 Crack Diagnostics**")
        st.write("Record visible surface defects and get suggested next steps.")
    with cols[1]:
        st.markdown("**📐 Planning & Valuation**")
        st.write("Estimate construction budget, spend-to-date, and indicative asset value.")
        st.markdown("**🌦️ Daily Site Assistant**")
        st.write("Use weather conditions to review precautions and ask construction questions.")
    st.warning("This educational capstone is not a substitute for a qualified safety officer, structural engineer, "
               "local code review, or professional valuation.")

elif page == "Site Safety & PPE Audit":
    st.subheader("🦺 Site Safety & PPE Audit")
    st.write("Upload a JPG/PNG site photo. The app looks for visible PPE and potential hazards.")
    image_file = st.file_uploader("Construction site photo", type=["jpg", "jpeg", "png"], key="safety_image")
    if image_file:
        st.image(image_file, caption="Uploaded site photo", use_container_width=True)
    if st.button("Analyze safety", type="primary", disabled=image_file is None):
        prompt = (
            "Review this construction-site photo for visible personal protective equipment and obvious hazards. "
            "Return ONLY valid JSON with keys safety_score (integer 0-100), overall_status, "
            "ppe_detection_checklist (array of objects with item, status, evidence), "
            "hazards (array of objects with hazard, severity [Low, Medium, High, Critical], "
            "corrective_remedy). Check helmet, high-visibility vest, steel-toe boots, safety harness where relevant. "
            "Do not claim unseen items are absent; use 'Not visible/uncertain'. This is preliminary screening, not certification."
        )
        result = gemini_analyze(prompt, image_file)
        data = try_json(result) if result else None
        if not data:
            data = {
                "safety_score": 70,
                "overall_status": "Review required",
                "ppe_detection_checklist": [
                    {"item": "Safety helmet", "status": "Not verified in demo mode", "evidence": "Manual review required"},
                    {"item": "High-visibility vest", "status": "Not verified in demo mode", "evidence": "Manual review required"},
                    {"item": "Steel-toe boots", "status": "Not visible/uncertain", "evidence": "Footwear may not be clear in image"},
                    {"item": "Safety harness", "status": "If working at height", "evidence": "Assess task and anchorage"}
                ],
                "hazards": [
                    {"hazard": "Unprotected work area or trip hazards may be present", "severity": "Medium",
                     "corrective_remedy": "Have the site supervisor inspect access routes, edge protection, and housekeeping."}
                ],
                "notice": "Demo output only; no image AI analysis was available."
            }
        score = max(0, min(100, int(data.get("safety_score", 0))))
        a, b = st.columns([1, 2])
        a.metric("Preliminary safety score", f"{score}/100")
        with b:
            metric_status(str(data.get("overall_status", "Review required")))
            st.progress(score / 100)
        st.markdown("### PPE checklist")
        checklist = data.get("ppe_detection_checklist", [])
        if checklist:
            st.dataframe(checklist, use_container_width=True, hide_index=True)
        st.markdown("### Potential hazards")
        hazards = data.get("hazards", [])
        if hazards:
            st.dataframe(hazards, use_container_width=True, hide_index=True)
        if data.get("notice"):
            st.info(data["notice"])
        st.caption("OSHA/IS 456 references are not a compliance certification. Verify current applicable rules with a competent safety professional.")
        show_json_download(data, "site_safety_report.json")

elif page == "Crack Diagnostics":
    st.subheader("🧱 Crack Diagnostics & Structural Integrity")
    st.write("Upload a wall or concrete surface photo for a preliminary visual review.")
    image_file = st.file_uploader("Wall/concrete photo", type=["jpg", "jpeg", "png"], key="crack_image")
    if image_file:
        st.image(image_file, caption="Uploaded surface photo", use_container_width=True)
    crack_width = st.number_input("Measured crack width (mm), if known", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    context = st.selectbox("Surface / location", ["Interior wall", "Exterior wall", "Concrete slab", "Beam or column", "Foundation", "Unknown"])
    if st.button("Review surface", type="primary", disabled=image_file is None):
        prompt = (
            "Inspect this surface photo for visible cracks or defects. Return ONLY valid JSON with keys "
            "defect_type (choose Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling, No clear defect, Uncertain), "
            "estimated_crack_width_mm (number or null), possible_causes (array), recommended_actions (array), "
            "urgency (Low, Medium, High, Urgent), limitations (array). Do not diagnose structural safety from an image alone. "
            f"User measured width: {crack_width} mm; location: {context}. If uncertain, say so."
        )
        result = gemini_analyze(prompt, image_file)
        data = try_json(result) if result else None
        if not data:
            data = {
                "defect_type": "Uncertain — manual inspection required",
                "estimated_crack_width_mm": crack_width if crack_width > 0 else None,
                "possible_causes": ["Cannot reliably determine cause from demo mode or a single image."],
                "recommended_actions": [
                    "Photograph the defect with a ruler for scale and record its location/date.",
                    "Monitor whether the crack changes over time.",
                    "Ask a qualified structural engineer to inspect before repair, especially for beams, columns, foundations, or widening cracks."
                ],
                "urgency": "Medium",
                "limitations": ["Demo mode does not analyze the image.", "Image-based review cannot establish structural integrity."]
            }
        st.markdown(f"**Observed classification:** {data.get('defect_type', 'Uncertain')}")
        st.markdown(f"**Urgency:** {data.get('urgency', 'Uncertain')}")
        st.markdown("### Possible causes")
        for item in data.get("possible_causes", []):
            st.write(f"• {item}")
        st.markdown("### Recommended next steps")
        for item in data.get("recommended_actions", []):
            st.write(f"• {item}")
        if data.get("limitations"):
            st.info("Limitations: " + " ".join(data["limitations"]))
        show_json_download(data, "crack_diagnostics_report.json")

elif page == "Planning & Valuation":
    st.subheader("📐 Planning & Real Estate Valuation")
    st.write("Indicative planning calculations. All values are estimates, not a formal quotation or valuation.")
    left, right = st.columns(2)
    with left:
        structure = st.selectbox("Structure type", ["Residential house", "Apartment", "Commercial building", "Warehouse", "Institutional"])
        area = st.number_input("Built-up area (sq ft)", min_value=100, max_value=10000000, value=1200, step=100)
        tier = st.selectbox("Location tier", ["Tier 1 city", "Tier 2 city", "Tier 3 city"])
        completion = st.slider("Completion percentage", 0, 100, 25)
    with right:
        rate = st.number_input("Construction cost per sq ft (₹)", min_value=500, max_value=20000, value=2200, step=100)
        land_value_lakh = st.number_input("Estimated land value (₹ lakh)", min_value=0.0, value=20.0, step=1.0)
        incurred_pct = st.slider("Budget already incurred (%)", 0, 100, completion)
        market_multiplier = st.number_input("Indicative asset value multiplier", min_value=0.5, max_value=5.0, value=1.35, step=0.05)
    total_budget = area * rate
    capex = total_budget * incurred_pct / 100
    tier_factor = {"Tier 1 city": 1.35, "Tier 2 city": 1.0, "Tier 3 city": 0.8}[tier]
    asset_value = (land_value_lakh * 100000 + total_budget * completion / 100) * market_multiplier * tier_factor
    steel_kg = area * 3.5
    cement_bags = area * 0.4
    st.markdown("### Estimate")
    m1, m2, m3 = st.columns(3)
    m1.metric("Indicative total budget", f"₹{total_budget/100000:.2f} lakh")
    m2.metric("Capital expenditure incurred", f"₹{capex/100000:.2f} lakh")
    m3.metric("Indicative asset value", f"₹{asset_value/100000:.2f} lakh")
    m4, m5 = st.columns(2)
    m4.metric("Indicative steel quantity", f"{steel_kg/1000:.2f} tonnes")
    m5.metric("Indicative cement", f"{cement_bags:,.0f} bags")
    st.progress(completion / 100)
    st.caption("Material quantities use simplified thumb rules and vary widely by design, structural system, soil, and local codes. Confirm with an engineer/quantity surveyor.")
    report = {
        "structure_type": structure, "built_up_area_sqft": area, "location_tier": tier,
        "completion_percent": completion, "construction_rate_inr_per_sqft": rate,
        "total_project_budget_inr": round(total_budget, 2),
        "capital_expenditure_incurred_inr": round(capex, 2),
        "indicative_asset_value_inr": round(asset_value, 2),
        "indicative_steel_kg": round(steel_kg, 2),
        "indicative_cement_bags": round(cement_bags, 2),
        "assumptions": "Simplified illustrative calculation; not a professional valuation or bill of quantities."
    }
    show_json_download(report, "planning_valuation_report.json")
    st.markdown("### Conceptual 3D design prompt")
    design_prompt = st.text_area("Describe the building", value=f"A modern {structure.lower()} with {area} sq ft built-up area, practical circulation, daylight, ventilation, and climate-responsive materials.")
    st.code("Create a conceptual architectural visualization: " + design_prompt, language="text")
    st.caption("Paste this prompt into an image-generation tool if you want a concept image; this app does not create a certified architectural drawing.")

elif page == "Daily Site Assistant":
    st.subheader("🌦️ Daily Site Assistant & Weather-Aware Advisory")
    weather = st.selectbox("Current site condition", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    task = st.selectbox("Main site activity", ["General work", "Crane / lifting operations", "Electrical work", "Concrete pouring / curing", "Work at height"])
    advisory = {
        ("High Wind", "Crane / lifting operations"): ("High", "Pause lifting if wind exceeds the crane/load/site limit. Secure loose materials and follow the lift supervisor's plan."),
        ("Heavy Rain", "Electrical work"): ("High", "Stop exposed electrical work where unsafe, isolate affected circuits as appropriate, and have a qualified electrician inspect wet equipment."),
        ("Extreme Heat", "General work"): ("Medium", "Provide water, shade, rest breaks, acclimatization, and buddy checks for heat illness."),
        ("Heavy Rain", "Concrete pouring / curing"): ("Medium", "Protect fresh concrete from washout and follow the approved mix and curing method."),
        ("High Wind", "Work at height"): ("High", "Review site wind limits, secure tools/materials, and suspend work when conditions exceed the approved plan."),
    }
    level, advice = advisory.get((weather, task), ("Normal", "Follow the approved method statement, PPE requirements, housekeeping plan, and supervisor instructions."))
    st.markdown("### Safety advisory")
    if level == "High":
        st.error(f"{level} attention: {advice}")
    elif level == "Medium":
        st.warning(f"{level} attention: {advice}")
    else:
        st.success(advice)
    question = st.text_area("Ask the construction assistant", placeholder="Example: What should be checked before a concrete pour?")
    if st.button("Ask assistant", type="primary", disabled=not question.strip()):
        prompt = (
            "You are a cautious construction site assistant. Give practical general guidance in plain language. "
            "Prioritize worker safety, applicable local codes, approved method statements, and competent professionals. "
            "Do not invent site-specific facts. Mention when a professional must decide. User question: " + question
        )
        result = gemini_analyze(prompt)
        if result:
            st.markdown(result)
        else:
            q = question.lower()
            if any(word in q for word in ["concrete", "pour", "curing"]):
                answer = ("Before a pour, verify approved drawings and mix design, formwork stability, reinforcement and cover, "
                          "embedded services, access, equipment, weather, testing plan, and crew briefing. Follow the engineer's "
                          "method statement and local requirements.")
            elif any(word in q for word in ["crane", "lift", "lifting"]):
                answer = ("Check the lift plan, certified operator and rigging, load weight/radius, ground bearing, exclusion zone, "
                          "communication, inspection records, and weather limits. Stop if any condition is uncertain.")
            elif any(word in q for word in ["helmet", "ppe", "safety"]):
                answer = ("Check task-specific PPE, training, access/edge protection, housekeeping, equipment condition, and emergency routes. "
                          "Report hazards to the site supervisor and follow the site's safety plan.")
            else:
                answer = ("Use the approved drawings and method statement, assess hazards before starting, confirm competent supervision, "
                          "and follow applicable local regulations. For structural, electrical, lifting, or emergency decisions, consult "
                          "the responsible qualified professional.")
            st.markdown(answer)
    st.caption("Weather is selected manually; this demo does not fetch live weather data.")

st.markdown("---")
st.markdown('<p class="small-note">Educational capstone prototype · Verify all AI outputs and estimates with qualified professionals.</p>', unsafe_allow_html=True)
