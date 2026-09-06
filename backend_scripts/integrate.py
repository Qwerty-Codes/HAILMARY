import re

with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Tabs
old_tabs = '''tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Load Forecast", "🔋 Energy Mix", "⛽ Fuel Savings", "🌤️ Weather & Renewables", "📋 Data Explorer"
])'''

new_tabs = '''tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐 3D Station View", "📊 Load Forecast", "🔋 Energy Mix", "⛽ Fuel Savings", "🌤️ Weather & Renewables", "📋 Data Explorer"
])

# ════════════════════════════════════════════════════════════════
# TAB 0 — 3D Station View (Frontend Integration)
# ════════════════════════════════════════════════════════════════
with tab0:
    st.subheader("🌐 Interactive 3D Station Simulation (Powered by AI)")
    st.markdown("This 3D view is completely synchronized with the AI backend. The temperatures, power loads, and generation you see in the HUD are coming directly from the XGBoost + LP Optimizer output!")
    
    dash_df = results.get("dashboard_df")
    if dash_df is not None:
        import json
        import streamlit.components.v1 as components
        
        # Extract the necessary columns for the simulation
        sim_data = dash_df[["load_kw", "temperature", "lp_solar", "lp_wind", "lp_diesel"]].to_dict(orient="records")
        
        try:
            with open("frontend/bundled.html", "r", encoding="utf-8") as f:
                html_content = f.read()
                
            # Inject the AI data into the JS window object
            injection = f"<script>window.STATION_DATA = {json.dumps(sim_data)};</script>"
            html_content = html_content.replace("</body>", injection + "</body>")
            
            # Render the 3D canvas
            components.html(html_content, height=850, scrolling=False)
        except Exception as e:
            st.error(f"Could not load 3D frontend. Did you run bundle.py? Error: {e}")
'''

code = code.replace(old_tabs, new_tabs)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("dashboard.py updated to integrate SIHPOLAR 3D view!")
