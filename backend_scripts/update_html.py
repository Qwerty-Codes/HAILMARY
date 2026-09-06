import re

with open('accu_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Demo Scrubber (Inject below header)
scrubber_html = """
    <!-- Demo Scrubber -->
    <div class="demo-controls" style="max-width: 1100px; margin: 16px auto 0; padding: 0 24px; display: flex; align-items: center; gap: 16px;">
        <label for="time-scrubber" style="font-size: 0.85rem; font-weight: 600; color: var(--text-sec);">DEMO TIME TRAVEL:</label>
        <input type="range" id="time-scrubber" min="0" max="100" value="0" style="flex: 1; cursor: pointer;">
        <button id="toggle-play" style="background: var(--bg-card); color: var(--text-main); border: var(--card-border); padding: 4px 12px; border-radius: var(--radius-sm); cursor: pointer; font-weight: 600;">PAUSE</button>
    </div>
"""
html = html.replace('</header>', '</header>\n' + scrubber_html)

# 2. Environmental Row (Inject below Hero Load)
env_html = """
                        <div class="env-row" style="display: flex; gap: 24px; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border-color);">
                            <div class="env-stat">
                                <span class="env-label" style="font-size: 0.75rem; color: var(--text-tertiary); font-weight: 600;">TEMP</span>
                                <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-main);"><span id="env-temp">--</span>°C</div>
                            </div>
                            <div class="env-stat">
                                <span class="env-label" style="font-size: 0.75rem; color: var(--text-tertiary); font-weight: 600;">WIND</span>
                                <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-main);"><span id="env-wind">--</span> m/s</div>
                            </div>
                            <div class="env-stat">
                                <span class="env-label" style="font-size: 0.75rem; color: var(--text-tertiary); font-weight: 600;">SOLAR IRR</span>
                                <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-main);"><span id="env-solar">--</span> W/m²</div>
                            </div>
                        </div>
"""
# Insert after hero-main
html = re.sub(r'(<div class="hero-main">.*?</div>)', r'\1' + env_html, html, flags=re.DOTALL)


# 3. Add details to source cards
# Diesel
diesel_ext = """
                <div class="card-details" style="margin-top: 12px; display: flex; flex-direction: column; gap: 4px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-sec); font-weight: 600;">
                        <span>CAPACITY: 200 kW</span>
                        <span id="diesel-pct">0%</span>
                    </div>
                    <div style="height: 4px; background: var(--border-color); border-radius: 2px; overflow: hidden;">
                        <div id="diesel-bar" style="height: 100%; width: 0%; background: var(--color-diesel); transition: width 0.3s ease;"></div>
                    </div>
                </div>
"""
html = re.sub(r'(<div class="source-card diesel">.*?<div class="card-bottom">.*?</div>)', r'\1' + diesel_ext, html, flags=re.DOTALL)

# Wind
wind_ext = """
                <div class="card-details" style="margin-top: 12px; font-size: 0.75rem; color: var(--text-sec); font-weight: 600;">
                    STATUS: <span id="wind-status-text" style="color: var(--text-main);">--</span>
                </div>
"""
html = re.sub(r'(<div class="source-card wind">.*?<div class="card-bottom">.*?</div>)', r'\1' + wind_ext, html, flags=re.DOTALL)

# Battery
battery_ext = """
                <div class="card-details" style="margin-top: 12px; display: flex; flex-direction: column; gap: 4px; font-size: 0.75rem; color: var(--text-sec); font-weight: 600;">
                    <div style="display: flex; justify-content: space-between;">
                        <span>STORED: <span id="batt-kwh" style="color: var(--text-main);">--</span> / 500 kWh</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>RATE: <span id="batt-rate" style="color: var(--text-main);">--</span></span>
                        <span id="batt-dir" style="font-weight: 800;">--</span>
                    </div>
                </div>
"""
html = re.sub(r'(<div class="source-card battery">.*?<div class="card-bottom">.*?</div>)', r'\1' + battery_ext, html, flags=re.DOTALL)

with open('accu_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html updated with new metrics")
