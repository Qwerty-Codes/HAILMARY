import re
import os

# 1. GENERATE MERGED HTML
html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Microgrid Digital Twin</title>
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Plotly -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <!-- PapaParse -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="dashboard-container">
        
        <!-- HEADER ROW (Merged Reference style + Dark/Light toggle) -->
        <header class="aw-header" style="position: sticky; top: 0; z-index: 1000; padding: 16px 0;">
            <div class="header-left">
                <span class="eyebrow">LIVE POLAR STATION</span>
                <h1>Microgrid Digital Twin</h1>
            </div>
            <div class="header-right" style="display: flex; align-items: center; gap: 16px;">
                <div class="live-badge"><span class="pulse-dot"></span> LIVE SIMULATION</div>
                <button id="btn-pause" class="btn-outline">Pause</button>
                
                <!-- Restored Theme Toggle -->
                <button class="theme-switch" id="theme-toggle" aria-label="Toggle Theme">
                    <span class="icon sun-icon">☀️</span>
                    <span class="icon moon-icon">🌙</span>
                </button>
            </div>
        </header>

        <!-- RESTORED ALERT TICKER -->
        <div class="ticker-wrap">
            <div class="ticker-badge safe" id="ticker-badge">INFO</div>
            <span id="ticker-msg">System status optimal — AI maximizing renewable penetration.</span>
        </div>

        <!-- RESTORED TABS -->
        <nav class="aw-tabs">
            <a href="#digital-twin" class="tab-link active">Digital Twin</a>
            <a href="#source-breakdown" class="tab-link">Source Breakdown</a>
            <a href="#ai-comparison" class="tab-link">AI vs Manual</a>
        </nav>

        <!-- ========================================== -->
        <!-- SECTION 1: DIGITAL TWIN (Reference Layout) -->
        <!-- ========================================== -->
        <section id="digital-twin" class="dashboard-section active-section">
            <!-- Row 1: Four Cards -->
            <div class="row grid-4">
                <div class="card stat-card">
                    <span class="label">Temperature</span>
                    <div class="value"><span id="val-temp">--</span> °C</div>
                </div>
                <div class="card stat-card">
                    <span class="label">Wind</span>
                    <div class="value"><span id="val-wind">--</span> m/s</div>
                </div>
                <div class="card stat-card">
                    <span class="label">Solar</span>
                    <div class="value"><span id="val-solar">--</span> W/m²</div>
                </div>
                <div class="card stat-card">
                    <span class="label">Battery SOC</span>
                    <div class="value"><span id="val-soc">--</span>%</div>
                </div>
            </div>

            <!-- Row 2: 60/40 Split -->
            <div class="row split-60-40">
                <!-- Left Card: Chart -->
                <div class="card chart-card">
                    <div class="card-header">
                        <div>
                            <h2>24-hour energy balance</h2>
                            <span class="subtitle">Load vs renewable generation</span>
                        </div>
                        <div class="hour-indicator">Hour <span id="val-hour">--</span></div>
                    </div>
                    <div class="chart-legend">
                        <span class="legend-item"><span class="dot dot-load"></span> Load</span>
                        <span class="legend-item"><span class="dot dot-ren"></span> Renewables</span>
                    </div>
                    <div id="balance-chart" style="height: 220px; width: 100%; margin-top: 16px;"></div>
                </div>

                <!-- Right Card: List -->
                <div class="card list-card">
                    <h2>Power sources</h2>
                    <div class="list-container">
                        <div class="list-row"><span class="list-label">Solar generation</span><span class="list-val"><span id="list-solar">--</span> kW</span></div>
                        <div class="list-row"><span class="list-label">Wind generation</span><span class="list-val"><span id="list-wind">--</span> kW</span></div>
                        <div class="list-row"><span class="list-label">Energy load</span><span class="list-val"><span id="list-load">--</span> kW</span></div>
                        <div class="list-row"><span class="list-label">Diesel fuel</span><span class="list-val"><span id="list-diesel">--</span>%</span></div>
                        <div class="list-row"><span class="list-label">Battery temperature</span><span class="list-val"><span id="list-batt-temp">--</span> °C</span></div>
                    </div>
                </div>
            </div>

            <!-- Row 3: Decision -->
            <div class="row">
                <div class="card decision-card">
                    <h2>Simulation decision</h2>
                    <p id="decision-text">Initializing digital twin simulation...</p>
                </div>
            </div>

            <!-- Row 4: Action Buttons -->
            <div class="row button-row">
                <button class="btn-outline" id="btn-storm">Simulate storm</button>
                <button class="btn-outline" id="btn-cold">Simulate extreme cold</button>
                <button class="btn-outline" id="btn-normal">Return to normal</button>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- SECTION 2: SOURCE BREAKDOWN (Restored)     -->
        <!-- ========================================== -->
        <section id="source-breakdown" class="dashboard-section" style="display: none;">
            <div class="row grid-4">
                <!-- Diesel -->
                <div class="card source-card diesel">
                    <div class="card-header"><span class="card-title">DIESEL GEN</span></div>
                    <div class="value"><span id="src-diesel">0.0</span> <span style="font-size: 1rem;">kW</span></div>
                    <div class="card-details">
                        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); font-weight: 600; margin-bottom: 4px;">
                            <span>CAPACITY: 200 kW</span><span id="src-diesel-pct">0%</span>
                        </div>
                        <div style="height: 4px; background: var(--border-color); border-radius: 2px; overflow: hidden;">
                            <div id="src-diesel-bar" style="height: 100%; width: 0%; background: var(--color-diesel); transition: width 0.3s ease;"></div>
                        </div>
                    </div>
                </div>
                <!-- Solar -->
                <div class="card source-card solar">
                    <div class="card-header"><span class="card-title">SOLAR PV</span></div>
                    <div class="value"><span id="src-solar">0.0</span> <span style="font-size: 1rem;">kW</span></div>
                    <div class="card-details">
                        <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">ACTIVE YIELD</span>
                    </div>
                </div>
                <!-- Wind -->
                <div class="card source-card wind">
                    <div class="card-header"><span class="card-title">WIND TURBINE</span></div>
                    <div class="value"><span id="src-wind">0.0</span> <span style="font-size: 1rem;">kW</span></div>
                    <div class="card-details" style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">
                        STATUS: <span id="src-wind-status" style="color: var(--text-main);">--</span>
                    </div>
                </div>
                <!-- Battery -->
                <div class="card source-card battery">
                    <div class="card-header"><span class="card-title">BATTERY ESS</span></div>
                    <div class="value"><span id="src-batt">0.0</span> <span style="font-size: 1rem;">kW</span></div>
                    <div class="card-details" style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600; display: flex; flex-direction: column; gap: 4px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span>STORED:</span><span id="src-batt-kwh" style="color: var(--text-main);">-- / 500 kWh</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>RATE:</span><span id="src-batt-dir" style="color: var(--text-main);">--</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="mix-chart" style="height: 300px; width: 100%; margin-top: 24px;"></div>
        </section>

        <!-- ========================================== -->
        <!-- SECTION 3: AI VS MANUAL (Restored)         -->
        <!-- ========================================== -->
        <section id="ai-comparison" class="dashboard-section" style="display: none;">
            <div class="card comparison-card" style="padding: var(--sp-lg);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                    <h2>Cumulative Savings vs Manual Ops</h2>
                    <span class="comp-badge" style="background: var(--color-ren); color: #000; padding: 4px 12px; border-radius: var(--radius-sm); font-size: 0.8rem; font-weight: 700;">AI OPTIMIZATION IMPACT</span>
                </div>
                <div class="row grid-4">
                    <div>
                        <span class="label">Fuel Prevented</span>
                        <div class="value" style="color: var(--text-main);">-<span id="comp-fuel">0</span> <span style="font-size: 1rem;">L</span></div>
                    </div>
                    <div>
                        <span class="label">Cost Saved</span>
                        <div class="value" style="color: var(--color-ren);">₹-<span id="comp-cost">0</span></div>
                    </div>
                    <div>
                        <span class="label">CO₂ Averted</span>
                        <div class="value" style="color: var(--text-muted);">-<span id="comp-co2">0</span> <span style="font-size: 1rem;">kg</span></div>
                    </div>
                </div>
            </div>
        </section>

    </div>
    
    <script src="app.js"></script>
</body>
</html>
"""

with open('accu_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Unified HTML written.")
