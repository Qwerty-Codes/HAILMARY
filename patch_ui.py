import re

with open('accu_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Grid to 5 and Add Risk Score
html = html.replace('<!-- Row 1: Four Cards -->', '<!-- Row 1: Five Cards (Added Risk) -->')
html = html.replace('<div class="row grid-4">', '<div class="row grid-5">', 1)

risk_card = """                <div class="card stat-card" style="border-left: 2px solid var(--color-alert);">
                    <span class="label">System Risk Score</span>
                    <div class="value" style="color: var(--color-alert);"><span id="val-risk">--</span>%</div>
                </div>
"""
# Insert after SOC card
soc_card_end = 'id="val-soc">--</span>%</div>\n                </div>\n'
html = html.replace(soc_card_end, soc_card_end + risk_card)


# 2. Update Power Sources List (Load Shedding)
old_list = """                        <div class="list-row"><span class="list-label">Energy load</span><span class="list-val"><span id="list-load">--</span> kW</span></div>
                        <div class="list-row"><span class="list-label">Diesel fuel</span><span class="list-val"><span id="list-diesel">--</span>%</span></div>"""

new_list = """                        <div class="list-row"><span class="list-label" style="color: var(--color-battery);">Critical Load (P0-P2)</span><span class="list-val"><span id="list-load-crit">--</span> kW</span></div>
                        <div class="list-row"><span class="list-label">Non-Critical Load</span><span class="list-val"><span id="list-load-non">--</span> kW</span></div>
                        <div class="list-row" id="shedding-alert" style="display: none; background: rgba(255, 60, 60, 0.15); color: var(--color-alert); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; margin-top: 4px; margin-bottom: 8px; text-align: center; font-weight: 700;">⚠ LOAD SHEDDING ACTIVE</div>
                        <div class="list-row"><span class="list-label">Diesel fuel</span><span class="list-val"><span id="list-diesel">--</span>%</span></div>"""
html = html.replace(old_list, new_list)


# 3. Add Animated Energy Flow to Source Breakdown Tab
source_breakdown_start = '<section id="source-breakdown" class="dashboard-section">\n            <div class="row grid-4">'
flow_diagram = """<section id="source-breakdown" class="dashboard-section">
            <!-- Animated Energy Flow Diagram -->
            <div class="card flow-diagram-card" style="margin-bottom: 24px; padding: var(--sp-5);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                    <h2>Live Energy Flow</h2>
                    <span class="comp-badge" style="background: rgba(255,255,255,0.1); padding: 4px 12px; border-radius: var(--radius-sm); font-size: 0.8rem;">Digital Twin Telemetry</span>
                </div>
                
                <div class="flow-container">
                    <!-- Generation Nodes -->
                    <div class="flow-col">
                        <div id="node-solar" class="flow-node">Solar PV<br><span id="flow-val-solar" class="flow-val">0</span> kW</div>
                        <div id="node-wind" class="flow-node">Wind Farm<br><span id="flow-val-wind" class="flow-val">0</span> kW</div>
                        <div id="node-diesel" class="flow-node">Diesel Gen<br><span id="flow-val-diesel" class="flow-val">0</span> kW</div>
                    </div>
                    
                    <!-- Path 1 (Gen to Bus) -->
                    <div class="flow-path"><div id="wire-gen" class="wire-animated"></div></div>
                    
                    <!-- Battery Bus -->
                    <div class="flow-col" style="align-items: center;">
                        <div id="node-battery" class="flow-node battery-node">Battery Bus<br><span id="flow-val-batt" class="flow-val">0</span>%</div>
                    </div>
                    
                    <!-- Path 2 (Bus to Load) -->
                    <div class="flow-path"><div id="wire-load" class="wire-animated"></div></div>
                    
                    <!-- Consumption Nodes -->
                    <div class="flow-col">
                        <div id="node-crit" class="flow-node crit-node" style="border-color: var(--color-battery);">Critical (P0-P2)<br><span id="flow-val-crit" class="flow-val">0</span> kW</div>
                        <div id="node-noncrit" class="flow-node">Non-Critical<br><span id="flow-val-non" class="flow-val">0</span> kW</div>
                    </div>
                </div>
            </div>
            
            <div class="row grid-4">"""
html = html.replace(source_breakdown_start, flow_diagram)

with open('accu_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html patched successfully.")
