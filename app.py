
import streamlit as st
from groq import Groq
import folium
from streamlit_folium import st_folium
import math
import time

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="GeoMind Flood Report Generator",
    page_icon="🌊",
    layout="wide"
)

# ---- NIGERIA LOCATIONS ----
NIGERIA_LOCATIONS = {
    "lokoja": {"lat": 7.8, "lon": 6.7, "state": "Kogi State"},
    "kano": {"lat": 12.0022, "lon": 8.5920, "state": "Kano State"},
    "lagos": {"lat": 6.5244, "lon": 3.3792, "state": "Lagos State"},
    "abuja": {"lat": 9.0765, "lon": 7.3986, "state": "FCT Abuja"},
    "niger delta": {"lat": 5.0, "lon": 6.0, "state": "Niger Delta"},
    "benue": {"lat": 7.7199, "lon": 8.7893, "state": "Benue State"},
    "port harcourt": {"lat": 4.8156, "lon": 7.0498, "state": "Rivers State"},
    "maiduguri": {"lat": 11.8333, "lon": 13.15, "state": "Borno State"},
    "sokoto": {"lat": 13.0059, "lon": 5.2476, "state": "Sokoto State"},
    "ibadan": {"lat": 7.3775, "lon": 3.947, "state": "Oyo State"},
    "enugu": {"lat": 6.4584, "lon": 7.5464, "state": "Enugu State"},
    "kaduna": {"lat": 10.5264, "lon": 7.4382, "state": "Kaduna State"},
    "warri": {"lat": 5.5167, "lon": 5.75, "state": "Delta State"},
    "yola": {"lat": 9.2035, "lon": 12.4954, "state": "Adamawa State"},
    "makurdi": {"lat": 7.7322, "lon": 8.5391, "state": "Benue State"},
}

RISK_COLORS = {
    "CRITICAL": "#d32f2f",
    "HIGH": "#f57c00",
    "MODERATE": "#fbc02d",
    "LOW": "#388e3c",
    "MINIMAL": "#1976d2"
}

# ---- LLM CALL ----
def call_llm(client, prompt, system, temperature=0.3, max_tokens=800):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# ---- PROMPT CHAIN STEPS ----
def step1_extract(client, location, context=""):
    system = """You are a GIS data extraction specialist.
Extract and structure geographic facts only. No analysis. No recommendations.
Be precise with coordinates and data values."""
    prompt = f"""Extract all relevant geographic and environmental facts about this Nigerian location for flood risk assessment.

Location: {location}
Additional context: {context if context else "None provided"}

Output a structured numbered list covering:
1. Location coordinates (approximate)
2. Geographical zone
3. Terrain type
4. Major water bodies nearby
5. Known environmental issues
6. Population density level
7. Climate zone
8. NDVI or vegetation data if known

Facts only. No analysis."""
    return call_llm(client, prompt, system, temperature=0.1)

def step2_analyze(client, facts):
    system = """You are a senior GIS flood risk analyst specializing in Nigerian hydrology.
Apply scientific GIS methodology. Output structured analysis only."""
    prompt = f"""Using these geographic facts, perform a technical GIS flood risk analysis.

EXTRACTED FACTS:
{facts}

Analyze:
1. HYDROLOGICAL RISK: River proximity, drainage, watershed
2. TOPOGRAPHIC RISK: Elevation, slope, terrain vulnerability
3. NDVI/VEGETATION RISK: Vegetation impact on water absorption
4. URBAN RISK: Infrastructure exposure
5. CLIMATE RISK: Rainfall patterns, climate change
6. HISTORICAL CONTEXT: Known flood events"""
    return call_llm(client, prompt, system, temperature=0.2)

def step3_reason(client, facts, analysis):
    system = """You are a flood risk expert using chain-of-thought reasoning.
Always show your thinking step by step before reaching conclusions.
This reduces errors and hallucination."""
    prompt = f"""Using chain-of-thought reasoning, determine the flood risk severity.

FACTS: {facts}
ANALYSIS: {analysis}

Follow this exact chain:
STEP A - What are the TOP 3 risk factors? Reason through each.
STEP B - What factors REDUCE the risk? Reason through each.
STEP C - How do these factors interact?
STEP D - Compare to other Nigerian flood-prone areas.
STEP E - CONCLUSION: Risk level = CRITICAL / HIGH / MODERATE / LOW / MINIMAL

Show ALL reasoning. Do not skip steps."""
    return call_llm(client, prompt, system, temperature=0.2)

def step4_report(client, location, facts, analysis, reasoning):
    system = """You are a professional GIS report writer for the Nigerian Emergency Management Agency (NEMA).
Write clear, actionable flood risk reports.
CRITICAL: Only use information from the provided analysis. Do not invent new facts."""
    prompt = f"""Generate a professional flood risk intelligence report.

LOCATION: {location}
FACTS: {facts}
ANALYSIS: {analysis}
REASONING: {reasoning}

Write with these exact sections:
# FLOOD RISK INTELLIGENCE REPORT
## Location Overview
## Key Geographic Risk Factors
## GIS Analysis Summary
## Risk Assessment
**Overall Risk Level:** [CRITICAL/HIGH/MODERATE/LOW/MINIMAL]
**Confidence Level:** [High/Medium/Low]
## Priority Recommendations
## Suggested GIS Actions
*Report generated by GeoMind AI | Powered by LLaMA 3.3 70B*"""
    return call_llm(client, prompt, system, temperature=0.4, max_tokens=1200)

def extract_risk_level(report_text):
    for level in ["CRITICAL", "HIGH", "MODERATE", "LOW", "MINIMAL"]:
        if level in report_text:
            return level
    return "MODERATE"

def build_map(location, report_text):
    loc_key = location.lower().split(",")[0].strip()
    coords = NIGERIA_LOCATIONS.get(loc_key, {"lat": 9.0820, "lon": 8.6753, "state": location})
    risk = extract_risk_level(report_text)
    color_hex = RISK_COLORS.get(risk, "#9c27b0")

    risk_color_map = {
        "CRITICAL": "red", "HIGH": "orange",
        "MODERATE": "beige", "LOW": "green", "MINIMAL": "blue"
    }
    marker_color = risk_color_map.get(risk, "purple")

    m = folium.Map(location=[coords["lat"], coords["lon"]], zoom_start=8, tiles="CartoDB positron")

    popup_html = f"""
    <div style="font-family:Arial;width:220px;">
        <h4 style="color:{color_hex};margin:0;">🌊 {location}</h4>
        <hr style="margin:6px 0;">
        <b>Risk Level:</b> <span style="color:{color_hex};font-weight:bold;">{risk}</span><br>
        <b>State:</b> {coords["state"]}<br>
        <b>Coords:</b> {coords["lat"]:.4f}°N, {coords["lon"]:.4f}°E<br>
        <hr style="margin:6px 0;">
        <small>GeoMind Flood Intelligence Report</small>
    </div>"""

    folium.Marker(
        [coords["lat"], coords["lon"]],
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=f"🌊 {location} — {risk} Risk",
        icon=folium.Icon(color=marker_color, icon="tint", prefix="fa")
    ).add_to(m)

    folium.Circle(
        [coords["lat"], coords["lon"]],
        radius=15000,
        color=color_hex,
        fill=True,
        fill_opacity=0.15,
        tooltip=f"{risk} Flood Risk Zone"
    ).add_to(m)

    legend = f"""<div style="position:fixed;bottom:30px;left:30px;z-index:1000;
        background:white;padding:14px;border-radius:10px;
        border:2px solid {color_hex};font-family:Arial;font-size:12px;min-width:160px;">
        <b style="color:{color_hex};">🌊 Flood Risk Map</b><br><br>
        <span style="color:{color_hex};font-size:16px;">●</span>
        <b style="color:{color_hex};"> {risk} RISK</b><br>
        <span style="color:gray;font-size:11px;">{location}</span>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    return m

# ---- CUSTOM CSS ----
st.markdown("""
<style>
    .main { background: #f8fafc; }
    .risk-badge {
        display: inline-block; padding: 6px 18px;
        border-radius: 20px; font-weight: bold;
        font-size: 1.1rem; margin: 8px 0;
    }
    .chain-step {
        background: #f0f4ff; border-left: 4px solid #1a73e8;
        padding: 8px 14px; border-radius: 0 8px 8px 0;
        margin: 6px 0; font-size: 13px;
    }
    .chain-done {
        background: #f0fff4; border-left: 4px solid #34a853;
    }
</style>""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;">
    <h1 style="color:#1a73e8;margin:0;">🌊 GeoMind</h1>
    <h3 style="color:#444;font-weight:400;margin:4px 0;">
        Agentic Flood Risk Report Generator for Nigeria
    </h3>
    <p style="color:gray;font-size:0.9rem;">
        Powered by 4-Step Prompt Chaining · LLaMA 3.3 70B · GIS Intelligence
    </p>
</div>""", unsafe_allow_html=True)

st.divider()

# ---- SESSION STATE ----
for key, val in [("report_result", None), ("generating", False)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ---- INPUT SECTION ----
col_input, col_info = st.columns([1.5, 1])

with col_input:
    st.markdown("### 📍 Enter Location")
    location = st.text_input(
        "Nigerian location to analyze",
        placeholder="e.g. Lokoja, Kogi State",
        help="Enter any Nigerian city, state, or region"
    )
    context = st.text_area(
        "Additional context (optional)",
        placeholder="e.g. Located near river confluence. Experienced flooding in 2022. Dense urban settlement.",
        height=100,
        help="Add any extra information to improve report accuracy"
    )

    st.markdown("**Quick Select:**")
    quick_locations = {
        "🌊 Lokoja, Kogi": "Lokoja, Kogi State",
        "🌊 Warri, Delta": "Warri, Delta State",
        "🌊 Makurdi, Benue": "Makurdi, Benue State",
        "🌊 Yola, Adamawa": "Yola, Adamawa State",
        "🏙️ Lagos Island": "Lagos Island, Lagos State",
    }
    cols = st.columns(3)
    for i, (label, value) in enumerate(quick_locations.items()):
        if cols[i % 3].button(label, use_container_width=True, key=f"quick_{i}"):
            st.session_state["quick_location"] = value
            st.rerun()

    if "quick_location" in st.session_state:
        location = st.session_state["quick_location"]

    generate_btn = st.button(
        "🔗 Run Prompt Chain → Generate Report",
        use_container_width=True,
        type="primary",
        disabled=not location
    )

with col_info:
    st.markdown("### 🔗 How Prompt Chaining Works")
    steps = [
        ("1️⃣", "EXTRACT", "Pull structured geographic facts from location"),
        ("2️⃣", "ANALYZE", "Apply GIS methodology to the facts"),
        ("3️⃣", "REASON", "Chain-of-thought risk severity assessment"),
        ("4️⃣", "REPORT", "Synthesize into professional flood report"),
    ]
    for icon, title, desc in steps:
        st.markdown(f"""
        <div class="chain-step">
            <b>{icon} {title}</b><br>
            <span style="color:#666;">{desc}</span>
        </div>""", unsafe_allow_html=True)
    st.info("💡 Each step output feeds the next step as input — this is prompt chaining")

# ---- GENERATE REPORT ----
if generate_btn and location:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    st.divider()
    st.markdown("### ⚙️ Running Prompt Chain...")

    progress = st.progress(0)
    status = st.empty()
    step_display = st.empty()

    chain_steps = [
        ("🔍 Step 1: Extracting geographic facts...", 25),
        ("📊 Step 2: Running GIS analysis...", 50),
        ("🧠 Step 3: Chain-of-thought reasoning...", 75),
        ("📄 Step 4: Generating final report...", 100),
    ]

    facts, analysis, reasoning, report = "", "", "", ""

    for i, (msg, pct) in enumerate(chain_steps):
        status.markdown(f"**{msg}**")
        step_display.markdown(f"""
        <div class="chain-step {'chain-done' if i > 0 else ''}">
            {msg}
        </div>""", unsafe_allow_html=True)

        if i == 0:
            facts = step1_extract(client, location, context)
        elif i == 1:
            analysis = step2_analyze(client, facts)
        elif i == 2:
            reasoning = step3_reason(client, facts, analysis)
        elif i == 3:
            report = step4_report(client, location, facts, analysis, reasoning)

        progress.progress(pct)
        time.sleep(0.3)

    status.empty()
    step_display.empty()

    st.session_state.report_result = {
        "location": location,
        "facts": facts,
        "analysis": analysis,
        "reasoning": reasoning,
        "report": report
    }
    st.rerun()

# ---- DISPLAY RESULTS ----
if st.session_state.report_result:
    result = st.session_state.report_result
    risk_level = extract_risk_level(result["report"])
    risk_color = RISK_COLORS.get(risk_level, "#9c27b0")

    st.divider()
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0;">
        <h2 style="margin:0;">📄 Report Ready: {result["location"]}</h2>
        <div class="risk-badge" style="background:{risk_color}22;color:{risk_color};
             border:2px solid {risk_color};">
            🌊 {risk_level} FLOOD RISK
        </div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Full Report", "🗺️ Risk Map",
        "🔍 Chain Step 1", "📊 Chain Step 2", "🧠 Chain Step 3"
    ])

    with tab1:
        st.markdown(result["report"])
        report_bytes = result["report"].encode()
        st.download_button(
            "⬇️ Download Report (.txt)",
            data=report_bytes,
            file_name=f"GeoMind_FloodReport_{result['location'].replace(', ','_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with tab2:
        st.markdown(f"**📍 {result['location']} — {risk_level} Flood Risk Zone**")
        map_obj = build_map(result["location"], result["report"])
        st_folium(map_obj, width=700, height=500)

    with tab3:
        st.markdown("### 🔍 Step 1: Extracted Geographic Facts")
        st.info("This step extracts only facts — no analysis yet. Temperature: 0.1 (maximum precision)")
        st.markdown(result["facts"])

    with tab4:
        st.markdown("### 📊 Step 2: GIS Technical Analysis")
        st.info("This step applies GIS methodology to the extracted facts. Temperature: 0.2")
        st.markdown(result["analysis"])

    with tab5:
        st.markdown("### 🧠 Step 3: Chain-of-Thought Reasoning")
        st.info("This step shows explicit reasoning before reaching conclusions — reduces hallucination. Temperature: 0.2")
        st.markdown(result["reasoning"])
