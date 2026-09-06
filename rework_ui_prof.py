import re

with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Title & Header
code = code.replace('st.title("Demo Home")', 'st.title("Load Optimizer")')
code = code.replace('st.markdown("<span style=\'color:#4FC3F7; font-weight:500;\'>Discharging</span>", unsafe_allow_html=True)', '')

# 2. Sidebar Navigation
tabs_code = '''tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐 3D Station View", "📊 Load Forecast", "🔋 Energy Mix", "⛽ Fuel Savings", "🌤️ Weather & Renewables", "📋 Data Explorer"
])'''
sidebar_code = '''st.sidebar.title("Navigation")
section = st.sidebar.radio("", [
    "3D Station View",
    "Load Forecast",
    "Energy Mix",
    "Fuel Savings",
    "Weather & Renewables",
    "Data Explorer"
])'''
code = code.replace(tabs_code, sidebar_code)

# 3. Replace Tabs with If Statements
code = code.replace('with tab0:', 'if section == "3D Station View":')
code = code.replace('with tab1:', 'if section == "Load Forecast":')
code = code.replace('with tab2:', 'if section == "Energy Mix":')
code = code.replace('with tab3:', 'if section == "Fuel Savings":')
code = code.replace('with tab4:', 'if section == "Weather & Renewables":')
code = code.replace('with tab5:', 'if section == "Data Explorer":')

# 4. Remove Emojis from Subheaders and Buttons
emoji_map = {
    "🌐 Interactive 3D Station Simulation (Powered by AI)": "Interactive 3D Station Simulation",
    "📊 Load Forecast (Next 48h)": "Load Forecast (Next 48h)",
    "🔋 Energy Mix — LP Optimal Dispatch": "Energy Mix — AI Optimal Dispatch",
    "⛽ Fuel Optimization — LP vs Standard Rules": "Fuel Optimization — AI vs Standard Rules",
    "🌤️ Weather Conditions & Renewable Generation": "Weather Conditions & Renewable Generation",
    "📋 Raw Data Explorer": "Raw Data Explorer",
    "⬇️ Download Dashboard CSV": "Download Dashboard CSV",
    "💰 Cost Saved": "Cost Saved",
    "⛽ AI Optimized Fuel": "AI Optimized Fuel",
    "☀️ Solar (kW)": "Solar (kW)",
    "💨 Wind (kW)": "Wind (kW)",
    "☀️ **Polar night effect:**": "**Polar night effect:**",
    "💨 **Safety shutdowns:**": "**Safety shutdowns:**"
}
for old, new in emoji_map.items():
    code = code.replace(old, new)

# 5. Remove Streamlit Info Icons
code = re.sub(r',\s*icon="[^"]+"', '', code)

# 6. Smooth Plotly Lines (spline) & Transparency (Lucidity)
# Adjust line_shape="spline" for go.Scatter
code = code.replace('name="Actual Load", line=dict(', 'name="Actual Load", line_shape="spline", line=dict(')
code = code.replace('name="Forecast (XGBoost)", line=dict(', 'name="Forecast (XGBoost)", line_shape="spline", line=dict(')
code = code.replace('name="Solar", line=dict(', 'name="Solar", line_shape="spline", line=dict(')
code = code.replace('name="Wind", line=dict(', 'name="Wind", line_shape="spline", line=dict(')
code = code.replace('name="Diesel", line=dict(', 'name="Diesel", line_shape="spline", line=dict(')
code = code.replace('name="Battery (Discharge)", line=dict(', 'name="Battery", line_shape="spline", line=dict(')
code = code.replace('name="Load", line=dict(', 'name="Load", line_shape="spline", line=dict(')
code = code.replace('name="Battery SOC %", line=dict(', 'name="Battery SOC %", line_shape="spline", line=dict(')

# Weather tab lines
code = code.replace('name="Temperature (°C)",\n            line=dict(', 'name="Temperature (°C)", line_shape="spline",\n            line=dict(')
code = code.replace('name="Wind Speed (m/s)",\n            line=dict(', 'name="Wind Speed (m/s)", line_shape="spline",\n            line=dict(')
code = code.replace('name="Irradiance (W/m²)",\n            line=dict(', 'name="Irradiance (W/m²)", line_shape="spline",\n            line=dict(')
code = code.replace('name="Cloud Cover (%)",\n            line=dict(', 'name="Cloud Cover (%)", line_shape="spline",\n            line=dict(')

# Adjust Opacity (Lucidity)
code = code.replace('fillcolor="rgba(249, 217, 73, 0.5)"', 'fillcolor="rgba(249, 217, 73, 0.15)"')
code = code.replace('fillcolor="rgba(43, 200, 113, 0.5)"', 'fillcolor="rgba(43, 200, 113, 0.15)"')
code = code.replace('fillcolor="rgba(85, 85, 85, 0.5)"', 'fillcolor="rgba(85, 85, 85, 0.15)"')

code = code.replace('fillcolor="rgba(249, 217, 73, 0.4)"', 'fillcolor="rgba(249, 217, 73, 0.15)"')
code = code.replace('fillcolor="rgba(43, 200, 113, 0.4)"', 'fillcolor="rgba(43, 200, 113, 0.15)"')

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Professional UI updates applied!")
