"""
╔══════════════════════════════════════════════════════════════════╗
║  AI-Driven Smart Energy Management — Polar Research Stations    ║
║  Interactive Dashboard  •  SIH 2024  •  Problem 26061          ║
╚══════════════════════════════════════════════════════════════════╝

Run:  streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Polar Energy Management",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Cache the full pipeline so it only runs once ─────────────────
@st.cache_resource(show_spinner="⚡ Running AI pipeline — fetching weather, training model, optimizing energy...")
def run_full_pipeline():
    from pipeline import run_pipeline
    return run_pipeline(skip_forecast=False)


# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/8c/NCPOR_Logo.png/150px-NCPOR_Logo.png", width=80)
    st.title("System Status")
    st.caption("AI-Driven Smart Energy Management\nfor Polar Research Stations")
    st.divider()
    st.markdown("**Station:** Maitri, Antarctica")
    st.markdown("**Location:** 70.77°S, 11.73°E")
    st.markdown("**Problem:** SIH 26061 (MoES/NCPOR)")
    st.divider()

    st.markdown("### System Architecture")
    st.markdown("""
    ```
    Weather API → Forecaster (ML)
                ↘
    Solar (Physics) → Optimizer → Actions
    Wind  (Physics) ↗     ↑
                    Battery + Diesel
    ```
    """)

    st.divider()
    st.markdown("### 🧠 ML vs ⚙️ Physics")
    st.markdown("""
    | Component | Type |
    |-----------|------|
    | Load forecast | 🧠 **ML** (XGBoost) |
    | Solar gen | ⚙️ Physics formula |
    | Wind gen | ⚙️ Power curve |
    | Dispatch | 📐 LP Optimization |
    """)

# ── Run pipeline ─────────────────────────────────────────────────
results = run_full_pipeline()

# ── Header ───────────────────────────────────────────────────────
st.title("⚡ AI-Driven Smart Energy Management System")
st.markdown("##### Polar Research Station: **Maitri, Antarctica** · Ministry of Earth Sciences / NCPOR")

# ── KPI Cards ────────────────────────────────────────────────────
metrics = results.get("metrics", {})
fuel_rules = results.get("fuel_rules_L", 0)
fuel_lp = results.get("fuel_lp_L", 0)
fuel_saved = results.get("fuel_saved_L", 0)
fuel_pct = results.get("fuel_saved_pct", 0)
cost_saved = results.get("cost_saved_inr", 0)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🧠 Load Forecast MAE", f"{metrics.get('mae_kw', 0):.2f} kW")
col2.metric("📈 R² Score", f"{metrics.get('r2', 0):.4f}")
col3.metric("⛽ Standard Rules Fuel", f"{fuel_rules:.1f} L")
col4.metric("AI Optimized Fuel", f"{fuel_lp:.1f} L", delta=f"-{fuel_saved:.1f} L", delta_color="inverse")
col5.metric("Cost Saved", f"₹{cost_saved:,.0f}", delta=f"-{fuel_pct:.1f}%", delta_color="inverse")

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.title("Navigation")
section = st.sidebar.radio("", [
    "3D Station View",
    "Load Forecast",
    "Energy Mix",
    "Fuel Savings",
    "Weather & Renewables",
    "Data Explorer"
])

# ════════════════════════════════════════════════════════════════
# TAB 0 — 3D Station View (Frontend Integration)
# ════════════════════════════════════════════════════════════════
if section == "3D Station View":
    st.subheader("Interactive 3D Station Simulation")
    st.markdown("This 3D view is completely synchronized with the AI backend. The temperatures, power loads, and generation you see in the HUD are coming directly from the XGBoost + LP Optimizer output!")
    
    dash_df = results.get("dashboard_df")
    if dash_df is not None:
        import json
        import streamlit.components.v1 as components
        
        # Extract the necessary columns for the simulation
        # Handle missing temperature by pulling from fcast_weather or creating a safe default
        weather_df = results.get('fcast_weather')
        if weather_df is not None and 'temperature' in weather_df.columns:
            # Pad or truncate if lengths don't match, though they should
            temps = weather_df['temperature'].values
            if len(temps) >= len(dash_df):
                dash_df['temperature'] = temps[:len(dash_df)]
            else:
                dash_df['temperature'] = -30.0
        elif 'temperature' not in dash_df.columns:
            dash_df['temperature'] = -30.0
            
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


# ════════════════════════════════════════════════════════════════
# TAB 1 — Load Forecast (ML)
# ════════════════════════════════════════════════════════════════
if section == "Load Forecast":
    st.subheader("🧠 Load Forecasting — XGBoost Regressor  (Machine Learning)")
    st.info(
        "**This is the Machine Learning Brain.** It looks at weather and time to predict exactly how much electricity the station will need. "
        "While solar and wind are calculated using standard physics formulas, this AI actively learns from past patterns."
    )

    y_test = results.get("y_test")
    y_pred = results.get("y_pred")

    if y_test is not None and y_pred is not None:
        # Show last N days
        days_show = st.slider("Days to display", 3, 30, 7, key="forecast_days")
        n_show = min(days_show * 24, len(y_test))
        idx = y_test.index[-n_show:]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=idx, y=y_test.values[-n_show:],
            name="Actual (synthetic)", mode="lines",
            line=dict(color="#1E88E5", width=1.5),
        ))
        fig.add_trace(go.Scatter(
            x=idx, y=y_pred[-n_show:],
            name="Predicted (XGBoost)", mode="lines",
            line=dict(color="#FF7043", width=1.5, dash="dash"),
        ))
        fig.update_layout(
            title=f"Predicted vs Actual Load — Last {days_show} Days of Test Set",
            xaxis_title="Time (UTC)", yaxis_title="Load (kW)",
            height=450, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Feature importance
        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.markdown("#### Feature Importances")
            model = results.get("model")
            if model is not None:
                from config import FEATURE_COLS
                imp = model.feature_importances_
                imp_df = pd.DataFrame({
                    "Feature": FEATURE_COLS, "Importance": imp
                }).sort_values("Importance", ascending=True)

                fig_imp = go.Figure(go.Bar(
                    x=imp_df["Importance"], y=imp_df["Feature"],
                    orientation="h", marker_color="#7E57C2",
                ))
                fig_imp.update_layout(height=350, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                       xaxis_title="Importance")
                st.plotly_chart(fig_imp, use_container_width=True)

        with col_b:
            st.markdown("#### Model Metrics")
            st.metric("MAE", f"{metrics['mae_kw']:.2f} kW",
                      help="Mean Absolute Error — average prediction error")
            st.metric("RMSE", f"{metrics['rmse_kw']:.2f} kW",
                      help="Root Mean Square Error")
            st.metric("R²", f"{metrics['r2']:.4f}",
                      help="Coefficient of determination — 1.0 is perfect")
            st.metric("MAPE", f"{metrics['mape_pct']:.2f}%",
                      help="Mean Absolute Percentage Error")

# ════════════════════════════════════════════════════════════════
# TAB 2 — Energy Source Mix
# ════════════════════════════════════════════════════════════════
if section == "Energy Mix":
    st.subheader("🔋 Energy Source Mix — Optimized Dispatch")

    dash_df = results.get("dashboard_df")
    if dash_df is not None:
        optimizer = st.radio("Select optimizer:", ["AI Optimized", "Standard Rules"],
                             horizontal=True, key="opt_select")
        prefix = "lp" if optimizer == "AI Optimized" else "rb"

        ts = dash_df["timestamp"]

        # Stacked area chart
        fig_mix = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            row_heights=[0.7, 0.3],
            subplot_titles=("Energy Source Mix", "Battery State of Charge"),
            vertical_spacing=0.08,
        )

        fig_mix.add_trace(go.Scatter(
            x=ts, y=dash_df[f"{prefix}_solar"], name="☀️ Solar",
            fill="tozeroy", fillcolor="rgba(255, 215, 0, 0.6)",
            line=dict(width=0.5, color="#FFD700"), stackgroup="sources",
        ), row=1, col=1)

        fig_mix.add_trace(go.Scatter(
            x=ts, y=dash_df[f"{prefix}_wind"], name="💨 Wind",
            fill="tonexty", fillcolor="rgba(79, 195, 247, 0.6)",
            line=dict(width=0.5, color="#2BC871"), stackgroup="sources",
        ), row=1, col=1)

        batt_discharge = np.maximum(0, dash_df[f"{prefix}_battery"].values)
        fig_mix.add_trace(go.Scatter(
            x=ts, y=batt_discharge, name="🔋 Battery",
            fill="tonexty", fillcolor="rgba(102, 187, 106, 0.6)",
            line=dict(width=0.5, color="#66BB6A"), stackgroup="sources",
        ), row=1, col=1)

        fig_mix.add_trace(go.Scatter(
            x=ts, y=dash_df[f"{prefix}_diesel"], name="⛽ Diesel",
            fill="tonexty", fillcolor="rgba(239, 83, 80, 0.6)",
            line=dict(width=0.5, color="#555555"), stackgroup="sources",
        ), row=1, col=1)

        fig_mix.add_trace(go.Scatter(
            x=ts, y=dash_df["load_kw"], name="⚡ Load",
            line_shape="spline", line=dict(color="black", width=2, dash="dot"),
        ), row=1, col=1)

        # Battery SOC
        fig_mix.add_trace(go.Scatter(
            x=ts, y=dash_df[f"{prefix}_soc"] * 100, name="SOC",
            line_shape="spline", line=dict(color="#66BB6A", width=2), showlegend=False,
        ), row=2, col=1)

        fig_mix.add_hline(y=20, row=2, col=1,
                          line_dash="dot", line_color="red",
                          annotation_text="20% Floor")

        fig_mix.update_layout(height=600, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig_mix.update_yaxes(title_text="Power (kW)", row=1, col=1)
        fig_mix.update_yaxes(title_text="SOC (%)", range=[0, 105], row=2, col=1)
        fig_mix.update_xaxes(title_text="Time (UTC)", row=2, col=1)

        st.plotly_chart(fig_mix, use_container_width=True)

        # Source breakdown stats
        st.markdown("#### Source Energy Breakdown (kWh)")
        solar_kwh = dash_df[f"{prefix}_solar"].sum()
        wind_kwh = dash_df[f"{prefix}_wind"].sum()
        batt_kwh = batt_discharge.sum()
        diesel_kwh = dash_df[f"{prefix}_diesel"].sum()
        total_kwh = solar_kwh + wind_kwh + batt_kwh + diesel_kwh

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("☀️ Solar", f"{solar_kwh:.0f} kWh",
                  f"{solar_kwh/total_kwh*100:.1f}%" if total_kwh > 0 else "0%")
        c2.metric("💨 Wind", f"{wind_kwh:.0f} kWh",
                  f"{wind_kwh/total_kwh*100:.1f}%" if total_kwh > 0 else "0%")
        c3.metric("🔋 Battery", f"{batt_kwh:.0f} kWh",
                  f"{batt_kwh/total_kwh*100:.1f}%" if total_kwh > 0 else "0%")
        c4.metric("⛽ Diesel", f"{diesel_kwh:.0f} kWh",
                  f"{diesel_kwh/total_kwh*100:.1f}%" if total_kwh > 0 else "0%")

# ════════════════════════════════════════════════════════════════
# TAB 3 — Fuel Savings
# ════════════════════════════════════════════════════════════════
if section == "Fuel Savings":
    st.subheader("Fuel Optimization — AI vs Standard Rules")

    col_f1, col_f2 = st.columns([1, 1])

    with col_f1:
        fig_fuel = go.Figure()
        fig_fuel.add_trace(go.Bar(
            x=["Standard Rules", "AI Optimized"],
            y=[fuel_rules, fuel_lp],
            marker_color=["#555555", "#2BC871"],
            text=[f"{fuel_rules:.1f} L", f"{fuel_lp:.1f} L"],
            textposition="outside",
        ))
        fig_fuel.update_layout(
            title="Total Fuel Consumption",
            yaxis_title="Fuel (Litres)",
            height=400, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_fuel, use_container_width=True)

    with col_f2:
        st.markdown("### Savings Summary")
        st.markdown(f"""
        | | Standard Rules | AI Optimized |
        |---|---|---|
        | **Fuel** | {fuel_rules:.1f} L | {fuel_lp:.1f} L |
        | **Saving** | — | **{fuel_saved:.1f} L ({fuel_pct:.1f}%)** |
        | **Cost (₹250/L)** | ₹{fuel_rules*250:,.0f} | ₹{fuel_lp*250:,.0f} |
        | **Cost Saved** | — | **₹{cost_saved:,.0f}** |
        """)

        st.success(f"**AI Optimizer saves {fuel_pct:.1f}% fuel** compared to the rule-based baseline.")

        st.markdown("#### Why the AI Optimizer is better:")
        st.markdown("""
        - **Predicts the Future** — It looks at the 48-hour weather forecast and charges the battery *before* the wind dies down.
        - **Smart Mixing** — Instead of turning things on/off randomly, it finds the perfect mathematical mix of solar, wind, and diesel to save fuel.
        - **No Wasted Fuel** — It perfectly balances the battery so the diesel generator only runs when absolutely necessary.
        """)

    # Cumulative fuel over time
    if dash_df is not None:
        st.markdown("#### Cumulative Fuel Over Time")
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
            x=dash_df["timestamp"],
            y=np.cumsum(dash_df["rb_diesel"] * 0.25),
            name="Standard Rules", line=dict(color="#555555", width=2),
        ))
        fig_cum.add_trace(go.Scatter(
            x=dash_df["timestamp"],
            y=np.cumsum(dash_df["lp_diesel"] * 0.25),
            name="AI Optimized", line=dict(color="#2BC871", width=2),
        ))
        fig_cum.update_layout(
            yaxis_title="Cumulative Fuel (L)", xaxis_title="Time",
            height=350, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_cum, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 — Weather & Renewables
# ════════════════════════════════════════════════════════════════
if section == "Weather & Renewables":
    st.subheader("Weather Conditions & Renewable Generation")
    st.warning("Solar and wind generation are **physics-based** (not ML). "
               "They use deterministic formulas applied to real weather data.")

    fcast_weather = results.get("fcast_weather")
    fcast_solar = results.get("fcast_solar")
    fcast_wind = results.get("fcast_wind")

    if fcast_weather is not None:
        fig_wx = make_subplots(
            rows=3, cols=1, shared_xaxes=True,
            subplot_titles=("Temperature & Wind Speed",
                            "Solar Irradiance & Cloud Cover",
                            "Renewable Generation (Physics-Based)"),
            vertical_spacing=0.08,
        )

        ts = fcast_weather.index

        # Temperature
        fig_wx.add_trace(go.Scatter(
            x=ts, y=fcast_weather["temperature"], name="Temperature (°C)", line_shape="spline",
            line=dict(color="#FF7043", width=2),
        ), row=1, col=1)

        # Wind speed on secondary axis
        fig_wx.add_trace(go.Scatter(
            x=ts, y=fcast_weather["wind_speed"], name="Wind Speed (m/s)", line_shape="spline",
            line=dict(color="#2BC871", width=2),
            yaxis="y2",
        ), row=1, col=1)

        # Safety cutoff line
        fig_wx.add_hline(y=25, row=1, col=1, line_dash="dot",
                         line_color="red",
                         annotation_text="⚠️ Turbine cutoff 25 m/s")

        # Irradiance
        fig_wx.add_trace(go.Scatter(
            x=ts, y=fcast_weather["irradiance"], name="Irradiance (W/m²)", line_shape="spline",
            line=dict(color="#F9D949", width=2),
        ), row=2, col=1)

        fig_wx.add_trace(go.Scatter(
            x=ts, y=fcast_weather["cloud_cover"], name="Cloud Cover (%)", line_shape="spline",
            line=dict(color="#90A4AE", width=1.5, dash="dot"),
        ), row=2, col=1)

        # Renewable generation
        if fcast_solar is not None:
            fig_wx.add_trace(go.Scatter(
                x=ts, y=fcast_solar.values, name="Solar (kW)",
                fill="tozeroy", fillcolor="rgba(249, 217, 73, 0.15)",
                line=dict(color="#F9D949", width=1.5),
            ), row=3, col=1)

        if fcast_wind is not None:
            fig_wx.add_trace(go.Scatter(
                x=ts, y=fcast_wind.values, name="Wind (kW)",
                fill="tozeroy", fillcolor="rgba(43, 200, 113, 0.15)",
                line=dict(color="#2BC871", width=1.5),
            ), row=3, col=1)

        fig_wx.update_layout(height=750, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig_wx.update_yaxes(title_text="°C / m/s", row=1, col=1)
        fig_wx.update_yaxes(title_text="W/m² / %", row=2, col=1)
        fig_wx.update_yaxes(title_text="Power (kW)", row=3, col=1)
        fig_wx.update_xaxes(title_text="Time (UTC)", row=3, col=1)

        st.plotly_chart(fig_wx, use_container_width=True)

        # Polar phenomena callout
        solar_zero_pct = (fcast_solar.values < 0.01).sum() / len(fcast_solar) * 100
        wind_shutdown = (fcast_weather["wind_speed"] > 25).sum()

        p1, p2 = st.columns(2)
        p1.info(f"**Polar night effect:** {solar_zero_pct:.0f}% of forecast hours have zero solar output. "
                f"At 70.8°S in winter, the sun doesn't rise.")
        p2.warning(f"**Safety shutdowns:** {wind_shutdown} of {len(fcast_weather)} hours have wind > 25 m/s. "
                   f"Turbines shut down to prevent damage — diesel must cover the gap.")

# ════════════════════════════════════════════════════════════════
# TAB 5 — Data Explorer
# ════════════════════════════════════════════════════════════════
if section == "Data Explorer":
    st.subheader("Raw Data Explorer")

    if dash_df is not None:
        st.dataframe(dash_df, use_container_width=True, height=500)

        csv = dash_df.to_csv(index=False)
        st.download_button(
            "Download Dashboard CSV",
            csv, "polar_energy_dashboard.csv", "text/csv",
        )

# ── Footer ───────────────────────────────────────────────────────
st.divider()
st.caption(
    "Built for Smart India Hackathon 2024 · Problem Statement 26061 · "
    "Ministry of Earth Sciences / NCPOR · "
    "Weather data: Open-Meteo (ERA5 reanalysis + NWP forecast)"
)
