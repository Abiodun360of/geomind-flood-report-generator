
import streamlit as st
from groq import Groq
import folium
from folium import Element
import math
import time

st.set_page_config(
    page_title="GeoMind Flood Report Generator",
    page_icon="🌊",
    layout="wide"
)

NIGERIA_LOCATIONS = {
    # North West
    "kano": {"lat": 12.0022, "lon": 8.5920, "state": "Kano State"},
    "kaduna": {"lat": 10.5264, "lon": 7.4382, "state": "Kaduna State"},
    "sokoto": {"lat": 13.0059, "lon": 5.2476, "state": "Sokoto State"},
    "zaria": {"lat": 11.0851, "lon": 7.7199, "state": "Kaduna State"},
    "kebbi": {"lat": 12.4539, "lon": 4.1975, "state": "Kebbi State"},
    "zamfara": {"lat": 12.1704, "lon": 6.6624, "state": "Zamfara State"},
    # North East
    "maiduguri": {"lat": 11.8333, "lon": 13.1500, "state": "Borno State"},
    "yola": {"lat": 9.2035, "lon": 12.4954, "state": "Adamawa State"},
    "gombe": {"lat": 10.2897, "lon": 11.1673, "state": "Gombe State"},
    "bauchi": {"lat": 10.3158, "lon": 9.8442, "state": "Bauchi State"},
    "damaturu": {"lat": 11.7469, "lon": 11.9606, "state": "Yobe State"},
    # North Central
    "abuja": {"lat": 9.0765, "lon": 7.3986, "state": "FCT Abuja"},
    "lokoja": {"lat": 7.7965, "lon": 6.7356, "state": "Kogi State"},
    "makurdi": {"lat": 7.7322, "lon": 8.5391, "state": "Benue State"},
    "minna": {"lat": 9.6139, "lon": 6.5569, "state": "Niger State"},
    "lafia": {"lat": 8.4940, "lon": 8.5219, "state": "Nasarawa State"},
    "jos": {"lat": 9.8965, "lon": 8.8583, "state": "Plateau State"},
    "ilorin": {"lat": 8.4966, "lon": 4.5426, "state": "Kwara State"},
    # South West
    "lagos": {"lat": 6.5244, "lon": 3.3792, "state": "Lagos State"},
    "lagos island": {"lat": 6.4541, "lon": 3.3947, "state": "Lagos State"},
    "ibadan": {"lat": 7.3775, "lon": 3.9470, "state": "Oyo State"},
    "akure": {"lat": 7.2526, "lon": 5.1942, "state": "Ondo State"},
    "abeokuta": {"lat": 7.1475, "lon": 3.3619, "state": "Ogun State"},
    "ado ekiti": {"lat": 7.6190, "lon": 5.2210, "state": "Ekiti State"},
    "osogbo": {"lat": 7.7827, "lon": 4.5418, "state": "Osun State"},
    # South South
    "port harcourt": {"lat": 4.8156, "lon": 7.0498, "state": "Rivers State"},
    "warri": {"lat": 5.5167, "lon": 5.7500, "state": "Delta State"},
    "niger delta": {"lat": 4.9000, "lon": 6.0000, "state": "Niger Delta Region"},
    "benin city": {"lat": 6.3350, "lon": 5.6037, "state": "Edo State"},
    "uyo": {"lat": 5.0377, "lon": 7.9128, "state": "Akwa Ibom State"},
    "yenagoa": {"lat": 4.9247, "lon": 6.2642, "state": "Bayelsa State"},
    "calabar": {"lat": 4.9517, "lon": 8.3220, "state": "Cross River State"},
    "asaba": {"lat": 6.1833, "lon": 6.7333, "state": "Delta State"},
    # South East
    "enugu": {"lat": 6.4584, "lon": 7.5464, "state": "Enugu State"},
    "onitsha": {"lat": 6.1667, "lon": 6.7833, "state": "Anambra State"},
    "owerri": {"lat": 5.4836, "lon": 7.0333, "state": "Imo State"},
    "abakaliki": {"lat": 6.3249, "lon": 8.1137, "state": "Ebonyi State"},
    "umuahia": {"lat": 5.5320, "lon": 7.4863, "state": "Abia State"},
    # Rivers / Deltas
    "benue river": {"lat": 7.7322, "lon": 8.5391, "state": "Benue State"},
    "niger river": {"lat": 6.5833, "lon": 6.7500, "state": "Niger Delta"},
}

RISK_COLORS = {
    "CRITICAL": "#d32f2f",
    "HIGH": "#f57c00",
    "MODERATE": "#fbc02d",
    "LOW": "#388e3c",
    "MINIMAL": "#1976d2"
}

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

def step1_extract(client, location, context=""):
    system = "You are a GIS data extraction specialist. Extract and structure geographic facts only. No analysis. Be precise."
    prompt = f"""Extract geographic and environmental facts about this Nigerian location for flood risk assessment.
Location: {location}
Additional context: {context if context else "None"}

Output a numbered list covering:
1. Coordinates (approximate)
2. Geographical zone
3. Terrain type
4. Major water bodies nearby
5. Known environmental issues
6. Population density
7. Climate zone
8. NDVI or vegetation data if known"""
    return call_llm(client, prompt, system, temperature=0.1)

def step2_analyze(client, facts):
    system = "You are a senior GIS flood risk analyst specializing in Nigerian hydrology. Apply scientific methodology."
    prompt = f"""Using these geographic facts, perform a technical GIS flood risk analysis.

FACTS:
{facts}

Analyze:
1. HYDROLOGICAL RISK
2. TOPOGRAPHIC RISK
3. NDVI/VEGETATION RISK
4. URBAN RISK
5. CLIMATE RISK
6. HISTORICAL CONTEXT"""
    return call_llm(client, prompt, system, temperature=0.2)

def step3_reason(client, facts, analysis):
    system = "You are a flood risk expert. Use chain-of-thought reasoning. Always show thinking before conclusions."
    prompt = f"""Using chain-of-thought reasoning, determine the flood risk severity.

FACTS: {facts}
ANALYSIS: {analysis}

Follow this chain:
STEP A - Top 3 risk factors
STEP B - Mitigating factors
STEP C - How factors interact
STEP D - Compare to other Nigerian locations
STEP E - CONCLUSION: CRITICAL / HIGH / MODERATE / LOW / MINIMAL"""
    return call_llm(client, prompt, system, temperature=0.2)

def step4_report(client, location, facts, analysis, reasoning):
    system = "You are a professional GIS report writer for NEMA Nigeria. Write clear actionable reports. Only use provided information."
    prompt = f"""Generate a professional flood risk intelligence report.

LOCATION: {location}
FACTS: {facts}
ANALYSIS: {analysis}
REASONING: {reasoning}

Use these exact sections:
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
    
    # Try exact match first
    coords = NIGERIA_LOCATIONS.get(loc_key, None)
    
    # Try partial match if no exact match
    if not coords:
        for key, val in NIGERIA_LOCATIONS.items():
            if key in loc_key or loc_key in key:
                coords = val
                break
    
    # Default to Nigeria center if not found
    if not coords:
        coords = {"lat": 9.0820, "lon": 8.6753, "state": location}
    risk = extract_risk_level(report_text)
    color_hex = RISK_COLORS.get(risk, "#9c27b0")
    marker_color_map = {
        "CRITICAL": "red", "HIGH": "orange",
        "MODERATE": "beige", "LOW": "green", "MINIMAL": "blue"
    }
    marker_color = marker_color_map.get(risk, "purple")

    m = folium.Map(
        location=[coords["lat"], coords["lon"]],
        zoom_start=8,
        tiles="OpenStreetMap"
    )

    popup_html = f"""<div style='font-family:Arial;width:200px;color:#111;'>
        <h4 style='color:{color_hex};margin:0;'>🌊 {location}</h4>
        <hr><b>Risk:</b> <span style='color:{color_hex};'>{risk}</span><br>
        <b>State:</b> {coords["state"]}<br>
        <b>Coords:</b> {coords["lat"]:.3f}N, {coords["lon"]:.3f}E
    </div>"""

    folium.Marker(
        [coords["lat"], coords["lon"]],
        popup=folium.Popup(popup_html, max_width=220),
        tooltip=f"🌊 {risk} Risk — {location}",
        icon=folium.Icon(color=marker_color, icon="tint", prefix="fa")
    ).add_to(m)

    folium.Circle(
        [coords["lat"], coords["lon"]],
        radius=12000,
        color=color_hex,
        fill=True,
        fill_opacity=0.15
    ).add_to(m)

    return m

# ---- CSS ----
st.markdown("""
<style>
/* ===== FORCE LIGHT MODE ENTIRE APP ===== */
html, body, .stApp, .main, .block-container {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
}

/* All text elements */
p, li, span, label, div, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown p, .stMarkdown li,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #1a1a1a !important;
    background-color: transparent !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f8fafc !important;
}

/* Input fields */
.stTextInput input, .stTextArea textarea {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #cccccc !important;
}
.stTextInput label, .stTextArea label {
    color: #1a1a1a !important;
}

/* Buttons */
.stButton button {
    background-color: #f0f4ff !important;
    color: #1a1a1a !important;
    border: 1px solid #1a73e8 !important;
    border-radius: 8px !important;
}
.stButton button:hover {
    background-color: #1a73e8 !important;
    color: #ffffff !important;
}
.stButton button[kind="primary"] {
    background-color: #1a73e8 !important;
    color: #ffffff !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #f8fafc !important;
}
.stTabs [data-baseweb="tab"] {
    color: #444444 !important;
    background-color: #f0f4ff !important;
    margin-right: 4px !important;
    border-radius: 8px 8px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #1a73e8 !important;
    background-color: #ffffff !important;
    border-bottom: 3px solid #1a73e8 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    padding: 1rem !important;
}
.stTabs [data-baseweb="tab-panel"] * {
    color: #1a1a1a !important;
}

/* Info / alert boxes */
.stAlert, .stInfo, [data-testid="stAlert"] {
    background-color: #e8f0fe !important;
    color: #1a1a1a !important;
}
.stAlert p, .stInfo p {
    color: #1a1a1a !important;
}

/* Progress bar */
.stProgress > div > div {
    background-color: #1a73e8 !important;
}

/* Divider */
hr { border-color: #e0e0e0 !important; }

/* Chain steps */
.chain-step {
    background-color: #f0f4ff !important;
    border-left: 4px solid #1a73e8 !important;
    padding: 10px 14px !important;
    border-radius: 0 8px 8px 0 !important;
    margin: 6px 0 !important;
}
.chain-step b, .chain-step span {
    color: #1a1a1a !important;
}

/* Risk badge */
.risk-badge {
    display: inline-block !important;
    padding: 6px 20px !important;
    border-radius: 20px !important;
    font-weight: bold !important;
    font-size: 1.1rem !important;
    margin: 8px 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;">
    <h1 style="color:#1a73e8;margin:0;">🌊 GeoMind</h1>
    <h3 style="color:#333;font-weight:400;margin:4px 0;">
        Agentic Flood Risk Report Generator for Nigeria
    </h3>
    <p style="color:#555;font-size:0.9rem;">
        Powered by 4-Step Prompt Chaining · LLaMA 3.3 70B · GIS Intelligence
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

for key, val in [("report_result", None), ("quick_location", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

col_input, col_info = st.columns([1.5, 1])

with col_input:
    st.markdown("### 📍 Enter Location")
    default_loc = st.session_state.get("quick_location", "")
    location = st.text_input("Nigerian location to analyze",
        value=default_loc,
        placeholder="e.g. Lokoja, Kogi State")
    context = st.text_area("Additional context (optional)",
        placeholder="e.g. Near river confluence. Flooded in 2022.",
        height=90)

    st.markdown("**Quick Select:**")
    quick = {
        "🌊 Lokoja": "Lokoja, Kogi State",
        "🌊 Warri": "Warri, Delta State",
        "🌊 Makurdi": "Makurdi, Benue State",
        "🏙️ Lagos Island": "Lagos Island, Lagos State",
        "🌊 Yola": "Yola, Adamawa State",
    }
    cols = st.columns(3)
    for i, (label, value) in enumerate(quick.items()):
        if cols[i % 3].button(label, use_container_width=True, key=f"q{i}"):
            st.session_state.quick_location = value
            st.rerun()

    generate_btn = st.button(
        "🔗 Run Prompt Chain → Generate Report",
        use_container_width=True,
        type="primary",
        disabled=not location
    )

with col_info:
    st.markdown("### 🔗 How Prompt Chaining Works")
    steps = [
        ("1️⃣", "EXTRACT", "Pull structured geographic facts"),
        ("2️⃣", "ANALYZE", "Apply GIS methodology to facts"),
        ("3️⃣", "REASON", "Chain-of-thought risk assessment"),
        ("4️⃣", "REPORT", "Synthesize professional report"),
    ]
    for icon, title, desc in steps:
        st.markdown(f"""
        <div class="chain-step">
            <b>{icon} {title}</b><br>
            <span style="color:#444;">{desc}</span>
        </div>""", unsafe_allow_html=True)
    st.info("💡 Each step feeds into the next — this is prompt chaining")

if generate_btn and location:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    st.divider()
    st.markdown("### ⚙️ Running Prompt Chain...")
    progress = st.progress(0)
    status = st.empty()

    status.markdown("**🔍 Step 1: Extracting geographic facts...**")
    facts = step1_extract(client, location, context)
    progress.progress(25)

    status.markdown("**📊 Step 2: Running GIS analysis...**")
    analysis = step2_analyze(client, facts)
    progress.progress(50)

    status.markdown("**🧠 Step 3: Chain-of-thought reasoning...**")
    reasoning = step3_reason(client, facts, analysis)
    progress.progress(75)

    status.markdown("**📄 Step 4: Generating final report...**")
    report = step4_report(client, location, facts, analysis, reasoning)
    progress.progress(100)

    status.empty()
    st.session_state.report_result = {
        "location": location,
        "facts": facts,
        "analysis": analysis,
        "reasoning": reasoning,
        "report": report
    }
    st.rerun()

if st.session_state.report_result:
    result = st.session_state.report_result
    risk = extract_risk_level(result["report"])
    color = RISK_COLORS.get(risk, "#9c27b0")

    st.divider()
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0;">
        <h2 style="color:#1a1a1a;margin:0;">📄 Report: {result["location"]}</h2>
        <div class="risk-badge" style="background:{color}22;color:{color};border:2px solid {color};">
            🌊 {risk} FLOOD RISK
        </div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Full Report", "🗺️ Risk Map",
        "🔍 Step 1: Facts", "📊 Step 2: Analysis", "🧠 Step 3: Reasoning"
    ])

    with tab1:
        st.markdown(result["report"])
        st.download_button(
            "⬇️ Download Report",
            data=result["report"].encode(),
            file_name=f"GeoMind_{result['location'].replace(', ','_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with tab2:
        st.markdown(f"**📍 {result['location']} — {risk} Flood Risk Zone**")
        map_obj = build_map(result["location"], result["report"])
        # Save map to HTML string and display with components
        import streamlit.components.v1 as components
        map_html = map_obj._repr_html_()
        components.html(map_html, height=500)

    with tab3:
        st.markdown("**Extracted geographic facts — temperature 0.1 (maximum precision)**")
        st.markdown(result["facts"])

    with tab4:
        st.markdown("**GIS technical analysis — temperature 0.2**")
        st.markdown(result["analysis"])

    with tab5:
        st.markdown("**Chain-of-thought reasoning — forces AI to show work before conclusion**")
        st.markdown(result["reasoning"])
