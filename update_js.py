import re

with open('accu_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add scrubber variables and setup logic
scrubber_logic = """
let timerId = null;
let isPlaying = true;

function setupScrubber() {
    const scrubber = document.getElementById('time-scrubber');
    const playBtn = document.getElementById('toggle-play');
    
    scrubber.max = globalData.length - 1;
    
    scrubber.addEventListener('input', (e) => {
        currentIndex = parseInt(e.target.value);
        cumulativeFuelSaved = 0; // reset sum for accurate scrubber jump
        for(let i=0; i<currentIndex; i++) {
            cumulativeFuelSaved += (globalData[i].rb_diesel - globalData[i].lp_diesel) * 0.25;
        }
        tick(true); // force tick without advancing
    });
    
    playBtn.addEventListener('click', () => {
        isPlaying = !isPlaying;
        playBtn.textContent = isPlaying ? 'PAUSE' : 'PLAY';
        if (isPlaying) {
            timerId = setInterval(() => tick(false), 2000);
        } else {
            clearInterval(timerId);
        }
    });
}
"""

js = js.replace('let cumulativeFuelSaved = 0;', 'let cumulativeFuelSaved = 0;\n' + scrubber_logic)
js = js.replace('setInterval(tick, 2000);', 'timerId = setInterval(() => tick(false), 2000);\n            setupScrubber();')
js = js.replace('function tick() {', 'function tick(skipAdvance=false) {')
js = js.replace('currentIndex = (currentIndex + 1) % globalData.length;', 'if(!skipAdvance) { currentIndex = (currentIndex + 1) % globalData.length; } \n    document.getElementById("time-scrubber").value = currentIndex;')

# Add the new metrics binding inside tick()
metrics_logic = """
    // --- New Environmental Metrics ---
    updateElementVal('env-temp', row.temperature, 'temp');
    updateElementVal('env-wind', row.wind_speed, 'wind_speed');
    updateElementVal('env-solar', row.irradiance, 'irradiance');

    // --- Battery Internals ---
    const battKwh = row.lp_soc * 500;
    document.getElementById('batt-kwh').textContent = battKwh.toFixed(0);
    const rateEl = document.getElementById('batt-rate');
    const dirEl = document.getElementById('batt-dir');
    rateEl.textContent = Math.abs(row.lp_battery).toFixed(1) + ' kW';
    
    if (row.lp_battery < -0.1) {
        dirEl.textContent = '↓ CHARGING';
        dirEl.style.color = getVar('--color-battery');
    } else if (row.lp_battery > 0.1) {
        dirEl.textContent = '↑ DISCHARGING';
        dirEl.style.color = getVar('--color-diesel');
    } else {
        dirEl.textContent = '— IDLE';
        dirEl.style.color = getVar('--text-tertiary');
    }

    // --- Diesel Internals ---
    const dieselPct = (row.lp_diesel / 200.0) * 100;
    document.getElementById('diesel-pct').textContent = dieselPct.toFixed(1) + '%';
    document.getElementById('diesel-bar').style.width = dieselPct + '%';

    // --- Wind Power Curve Status ---
    const windStatEl = document.getElementById('wind-status-text');
    const windCard = document.querySelector('.source-card.wind');
    windCard.style.border = getVar('--card-border'); // reset
    if (row.wind_speed < 3.0) {
        windStatEl.textContent = "BELOW CUT-IN";
    } else if (row.wind_speed >= 3.0 && row.wind_speed < 12.0) {
        windStatEl.textContent = "RAMPING UP";
    } else if (row.wind_speed >= 12.0 && row.wind_speed <= 25.0) {
        windStatEl.textContent = "RATED OUTPUT";
    } else if (row.wind_speed > 25.0) {
        windStatEl.textContent = "SAFETY CUTOFF ⚠️";
        windStatEl.style.color = getVar('--color-alert');
        windCard.style.border = '2px solid ' + getVar('--color-alert');
    }

    // --- Extreme Weather Event Handling & Ticker ---
    const tickerBadge = document.getElementById('ticker-badge');
    const tickerMsg = document.getElementById('ticker-msg');
    
    let isExtreme = false;

    // 1. Wind Cutoff
    if (row.wind_speed > 25.0) {
        tickerBadge.className = 'ticker-badge danger';
        tickerBadge.textContent = 'EXTREME';
        tickerMsg.textContent = `WIND CUTOFF (${row.wind_speed.toFixed(1)} m/s) — Turbines locked. Diesel compensating.`;
        isExtreme = true;
    } 
    // 2. Blizzard Condition (High wind + Freezing)
    else if (row.wind_speed > 15.0 && row.temperature < -15.0) {
        tickerBadge.className = 'ticker-badge danger';
        tickerBadge.textContent = 'BLIZZARD';
        tickerMsg.textContent = `SEVERE BLIZZARD: ${row.temperature.toFixed(1)}°C with ${row.wind_speed.toFixed(1)} m/s winds. Heating load peaking.`;
        isExtreme = true;
    }
    // 3. Cold Snap
    else if (row.temperature < -25.0) {
        tickerBadge.className = 'ticker-badge warning';
        tickerBadge.textContent = 'COLD SNAP';
        tickerMsg.textContent = `EXTREME COLD (${row.temperature.toFixed(1)}°C) — Maximum heating load engaged.`;
        isExtreme = true;
    }
    // 4. Polar Night (Zero irradiance during day hours or sustained)
    else if (row.irradiance < 5.0 && row.solar_avail === 0) {
        tickerBadge.className = 'ticker-badge warning';
        tickerBadge.textContent = 'POLAR NIGHT';
        tickerMsg.textContent = "ZERO SOLAR YIELD — Relying entirely on wind and diesel reserves.";
        isExtreme = true;
    }
    // Default
    else {
        tickerBadge.className = 'ticker-badge safe';
        tickerBadge.textContent = 'INFO';
        tickerMsg.textContent = "System status optimal — AI maximizing renewable penetration.";
    }
"""

# Replace old ticker logic with new one
js = re.sub(r'// --- Update Ticker ---.*?// --- Update Comparison ---', metrics_logic + '\n    // --- Update Comparison ---', js, flags=re.DOTALL)
js = js.replace('// Update Ticker', '')

with open('accu_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated with scrubber and extreme weather logic")
