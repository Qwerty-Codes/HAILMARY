import re

with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Inject Custom CSS for Samsung Sans / Tesla aesthetic
css_injection = """
# ── Custom CSS ───────────────────────────────────────────────────
st.markdown(\"\"\"
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', 'Samsung Sans', sans-serif !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 400 !important;
        color: #aaaaaa !important;
        text-transform: uppercase;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px;
    }
    
    /* Hide Streamlit top padding to look more like a mobile app */
    .block-container {
        padding-top: 2rem !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111111;
        padding: 10px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #222222;
        border-radius: 8px;
        color: #aaaaaa;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #333333 !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
</style>
\"\"\", unsafe_allow_html=True)
"""
code = code.replace("st.title(\"❄️ AI Polar Energy Management System\")", css_injection + "\nst.title(\"Demo Home\")\nst.markdown(\"<span style='color:#4FC3F7; font-weight:500;'>Discharging</span>\", unsafe_allow_html=True)")

# 2. Update Colors and Plotly Templates
# Load Forecast
code = code.replace('line=dict(color="#FFD700"', 'line=dict(color="#F9D949"') # Solar Yellow
code = code.replace('fillcolor="rgba(255, 215, 0, 0.4)"', 'fillcolor="rgba(249, 217, 73, 0.4)"')
code = code.replace('line=dict(color="#4FC3F7"', 'line=dict(color="#2BC871"') # Wind Green
code = code.replace('fillcolor="rgba(79, 195, 247, 0.4)"', 'fillcolor="rgba(43, 200, 113, 0.4)"')
code = code.replace('template="plotly_white"', 'template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"')

# specifically target axis updates to remove grid lines
plotly_updates = """
        fig_mix.update_layout(
            yaxis_title="Power (kW)", xaxis_title="Time",
            height=400, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        )"""
code = re.sub(r'fig_mix\.update_layout\(.*?height=400, template="plotly_white",.*?\)', plotly_updates.strip(), code, flags=re.DOTALL)

plotly_updates_fc = """
        fig_fc.update_layout(
            yaxis_title="Load (kW)", xaxis_title="Time",
            height=400, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        )"""
code = re.sub(r'fig_fc\.update_layout\(.*?height=400, template="plotly_white",.*?\)', plotly_updates_fc.strip(), code, flags=re.DOTALL)

plotly_updates_fuel = """
        fig_fuel.update_layout(
            title="Total Fuel Consumption",
            yaxis_title="Fuel (Litres)",
            height=400, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        )"""
code = re.sub(r'fig_fuel\.update_layout\(.*?height=400, template="plotly_white",.*?\)', plotly_updates_fuel.strip(), code, flags=re.DOTALL)

# Also fix colors in Tab 3 (Fuel Savings) to match Tesla dark mode vibes
code = code.replace('marker_color=["#EF5350", "#4FC3F7"]', 'marker_color=["#555555", "#2BC871"]')
code = code.replace('color="#EF5350"', 'color="#555555"')
code = code.replace('color="#4FC3F7"', 'color="#2BC871"')

# Solar yellow in tab 2
code = code.replace('color="#FFB300"', 'color="#F9D949"')
code = code.replace('fillcolor="rgba(255, 179, 0, 0.5)"', 'fillcolor="rgba(249, 217, 73, 0.5)"')

# Wind green in tab 2
code = code.replace('color="#03A9F4"', 'color="#2BC871"')
code = code.replace('fillcolor="rgba(3, 169, 244, 0.5)"', 'fillcolor="rgba(43, 200, 113, 0.5)"')

# Diesel Grey in tab 2
code = code.replace('color="#757575"', 'color="#555555"')
code = code.replace('fillcolor="rgba(117, 117, 117, 0.5)"', 'fillcolor="rgba(85, 85, 85, 0.5)"')

# Battery line
code = code.replace('color="#8E24AA"', 'color="#ffffff"')
code = code.replace('color="#FF5252"', 'color="#EF5350"')

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Dashboard UI reworked!")
