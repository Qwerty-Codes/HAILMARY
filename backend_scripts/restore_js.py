js = """
let globalData = [];
let currentIndex = 0;
let timerId = null;
let isPlaying = true;
let isDarkMode = true; // True Black defaults as true now
let cumulativeFuel = 0;
const TANK_CAPACITY = 5000;

Papa.parse('../output/dashboard_data.csv', {
    download: true,
    header: true,
    dynamicTyping: true,
    complete: function(results) {
        globalData = results.data.filter(row => row.timestamp);
        initTheme();
        initTabs();
        initCharts();
        setupControls();
        timerId = setInterval(() => tick(false), 2000);
        tick(true);
    }
});

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
    
    if (savedTheme === 'light' || (!savedTheme && prefersLight)) {
        isDarkMode = false;
        document.documentElement.setAttribute('data-theme', 'light');
    }
    
    document.getElementById('theme-toggle').addEventListener('click', () => {
        isDarkMode = !isDarkMode;
        if (isDarkMode) {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
        updateChartTheme();
    });
}

function initTabs() {
    const links = document.querySelectorAll('.tab-link');
    const sections = document.querySelectorAll('.dashboard-section');
    
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            links.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active-section'));
            
            link.classList.add('active');
            const targetId = link.getAttribute('href').substring(1);
            document.getElementById(targetId).classList.add('active-section');
            
            // Re-render charts when visible
            updateCharts();
        });
    });
}

function setupControls() {
    const playBtn = document.getElementById('btn-pause');
    playBtn.addEventListener('click', () => {
        isPlaying = !isPlaying;
        playBtn.textContent = isPlaying ? 'Pause' : 'Play';
        if (isPlaying) {
            timerId = setInterval(() => tick(false), 2000);
        } else {
            clearInterval(timerId);
        }
    });

    document.getElementById('btn-storm').addEventListener('click', () => {
        const target = globalData.findIndex(d => d.wind_speed > 20);
        if (target !== -1) jumpTo(target);
    });

    document.getElementById('btn-cold').addEventListener('click', () => {
        const target = globalData.findIndex(d => d.temperature < -20);
        if (target !== -1) jumpTo(target);
    });

    document.getElementById('btn-normal').addEventListener('click', () => {
        const target = globalData.findIndex(d => d.wind_speed > 5 && d.wind_speed < 12 && d.temperature > -10 && d.solar_avail > 0);
        if (target !== -1) jumpTo(target);
    });
}

function jumpTo(idx) {
    currentIndex = idx;
    cumulativeFuel = 0;
    for (let i = 0; i < currentIndex; i++) {
        cumulativeFuel += (globalData[i].lp_diesel * 0.25);
    }
    tick(true);
}

function getVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function updateVal(id, val, dp=0) {
    const el = document.getElementById(id);
    if (!el) return;
    if (val === undefined || val === null || isNaN(val)) {
        el.textContent = '--';
    } else {
        el.textContent = val.toFixed(dp);
    }
}

function getDecisionText(row) {
    let ren = row.lp_solar + row.lp_wind;
    if (ren >= row.load_kw) {
        if (row.lp_battery < -0.1) return "Renewable generation covers the current load; excess power is charging the battery.";
        return "Renewable generation covers the current load; excess power is being curtailed (battery full).";
    } else {
        if (row.lp_diesel > 0.1) {
            if (row.lp_battery > 0.1) return "Renewables and battery are insufficient; diesel generator engaged to cover the deficit.";
            return "Renewables are insufficient and battery is below threshold; diesel generator engaged.";
        }
        return "Renewable generation is insufficient; battery discharging to cover the remaining load.";
    }
}

function tick(skipAdvance=false) {
    if (!skipAdvance) {
        currentIndex = (currentIndex + 1) % globalData.length;
    }
    
    const row = globalData[currentIndex];
    if(!row) return;

    // --- DIGITAL TWIN METRICS ---
    updateVal('val-temp', row.temperature, 1);
    updateVal('val-wind', row.wind_speed, 1);
    updateVal('val-solar', row.irradiance, 0);
    updateVal('val-soc', row.lp_soc * 100, 0);

    updateVal('list-solar', row.lp_solar, 0);
    updateVal('list-wind', row.lp_wind, 0);
    updateVal('list-load', row.load_kw, 0);
    
    cumulativeFuel += (row.lp_diesel * 0.25);
    let fuelPct = Math.max(0, ((TANK_CAPACITY - cumulativeFuel) / TANK_CAPACITY) * 100);
    updateVal('list-diesel', fuelPct, 0);
    
    let battTemp = 15 + ((Math.abs(row.lp_battery) / 500) * 10);
    if(row.temperature < -15) battTemp -= 2;
    updateVal('list-batt-temp', battTemp, 1);

    const d = new Date(row.timestamp);
    document.getElementById('val-hour').textContent = d.getHours();
    document.getElementById('decision-text').textContent = getDecisionText(row);

    // --- SOURCE BREAKDOWN METRICS ---
    updateVal('src-diesel', row.lp_diesel, 1);
    updateVal('src-solar', row.lp_solar, 1);
    updateVal('src-wind', row.lp_wind, 1);
    updateVal('src-batt', Math.abs(row.lp_battery), 1);
    
    const dieselPct = (row.lp_diesel / 200.0) * 100;
    document.getElementById('src-diesel-pct').textContent = dieselPct.toFixed(1) + '%';
    document.getElementById('src-diesel-bar').style.width = dieselPct + '%';
    
    const windStatEl = document.getElementById('src-wind-status');
    if(windStatEl) {
        if (row.wind_speed < 3.0) windStatEl.textContent = "BELOW CUT-IN";
        else if (row.wind_speed < 12.0) windStatEl.textContent = "RAMPING UP";
        else if (row.wind_speed <= 25.0) windStatEl.textContent = "RATED OUTPUT";
        else {
            windStatEl.textContent = "SAFETY CUTOFF ⚠️";
            windStatEl.style.color = getVar('--color-alert');
        }
    }

    const battDir = document.getElementById('src-batt-dir');
    if(battDir) {
        if (row.lp_battery < -0.1) { battDir.textContent = '↓ CHARGING'; battDir.style.color = getVar('--color-battery'); }
        else if (row.lp_battery > 0.1) { battDir.textContent = '↑ DISCHARGING'; battDir.style.color = getVar('--color-diesel'); }
        else { battDir.textContent = '— IDLE'; battDir.style.color = getVar('--text-muted'); }
    }
    
    const battKwh = row.lp_soc * 500;
    if(document.getElementById('src-batt-kwh')) document.getElementById('src-batt-kwh').textContent = battKwh.toFixed(0) + ' / 500 kWh';

    // --- AI VS MANUAL METRICS ---
    let savedTotal = 0;
    for(let i=0; i<=currentIndex; i++) {
        let rbF = globalData[i].rb_diesel * 0.25;
        let lpF = globalData[i].lp_diesel * 0.25;
        savedTotal += (rbF - lpF);
    }
    updateVal('comp-fuel', savedTotal, 1);
    updateVal('comp-cost', savedTotal * 250, 0); // ₹250/L
    updateVal('comp-co2', savedTotal * 2.68, 0); // 2.68 kg CO2/L

    // --- ALERT TICKER LOGIC ---
    const tickerBadge = document.getElementById('ticker-badge');
    const tickerMsg = document.getElementById('ticker-msg');
    if(tickerBadge && tickerMsg) {
        if (row.wind_speed > 25.0) {
            tickerBadge.className = 'ticker-badge danger'; tickerBadge.textContent = 'EXTREME';
            tickerMsg.textContent = `WIND CUTOFF (${row.wind_speed.toFixed(1)} m/s) — Turbines locked. Diesel compensating.`;
        } else if (row.wind_speed > 15.0 && row.temperature < -15.0) {
            tickerBadge.className = 'ticker-badge danger'; tickerBadge.textContent = 'BLIZZARD';
            tickerMsg.textContent = `SEVERE BLIZZARD: ${row.temperature.toFixed(1)}°C with ${row.wind_speed.toFixed(1)} m/s winds.`;
        } else if (row.temperature < -25.0) {
            tickerBadge.className = 'ticker-badge warning'; tickerBadge.textContent = 'COLD SNAP';
            tickerMsg.textContent = `EXTREME COLD (${row.temperature.toFixed(1)}°C) — Maximum heating load engaged.`;
        } else if (row.irradiance < 5.0 && row.solar_avail === 0) {
            tickerBadge.className = 'ticker-badge warning'; tickerBadge.textContent = 'POLAR NIGHT';
            tickerMsg.textContent = "ZERO SOLAR YIELD — Relying entirely on wind and diesel reserves.";
        } else {
            tickerBadge.className = 'ticker-badge safe'; tickerBadge.textContent = 'INFO';
            tickerMsg.textContent = "System status optimal — AI maximizing renewable penetration.";
        }
    }

    updateCharts();
}

function initCharts() {
    Plotly.newPlot('balance-chart', [], { margin: { t: 5, r: 0, b: 20, l: 0 }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', xaxis: { showgrid: false, zeroline: false, showticklabels: false }, yaxis: { showgrid: true, gridcolor: '#282828', zeroline: false, showticklabels: false }, showlegend: false }, {displayModeBar: false, responsive: true});
    Plotly.newPlot('mix-chart', [], { margin: { t: 10, r: 10, b: 30, l: 40 }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', xaxis: { showgrid: false }, yaxis: { showgrid: true, gridcolor: '#282828' }, showlegend: false }, {displayModeBar: false, responsive: true});
}

function updateChartTheme() {
    const gridColor = getVar('--border-color');
    const fontColor = getVar('--text-muted');
    Plotly.relayout('balance-chart', { 'yaxis.gridcolor': gridColor });
    Plotly.relayout('mix-chart', { 'yaxis.gridcolor': gridColor, 'font.color': fontColor });
    updateCharts();
}

function updateCharts() {
    if (globalData.length === 0) return;
    
    // 1. Digital Twin Chart
    let startIdx = currentIndex;
    let endIdx = Math.min(globalData.length, currentIndex + 24);
    let windowData = globalData.slice(startIdx, endIdx);
    if (windowData.length < 24) windowData = windowData.concat(globalData.slice(0, 24 - windowData.length));
    
    let x = Array.from({length: 24}, (_, i) => i);
    let traceLoad = { x, y: windowData.map(d => d.load_kw), type: 'scatter', line: {shape: 'spline', color: getVar('--color-load'), width: 2} };
    let traceRen = { x, y: windowData.map(d => d.lp_solar + d.lp_wind), type: 'scatter', line: {shape: 'spline', color: getVar('--color-ren'), width: 2} };
    
    if(document.getElementById('balance-chart').offsetWidth > 0) {
        Plotly.react('balance-chart', [traceLoad, traceRen], { margin: { t: 5, r: 0, b: 0, l: 0 }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', xaxis: { showgrid: false, zeroline: false, showticklabels: false }, yaxis: { showgrid: true, gridcolor: getVar('--border-color'), zeroline: false, showticklabels: false }, showlegend: false });
    }

    // 2. Source Breakdown Mix Chart
    if(document.getElementById('mix-chart').offsetWidth > 0) {
        let mixWindow = globalData.slice(Math.max(0, currentIndex - 6), Math.min(globalData.length, currentIndex + 12));
        let mx = mixWindow.map(d => d.timestamp);
        
        function h2r(hex, a) { hex = hex.trim().replace('#',''); return `rgba(${parseInt(hex.substr(0,2),16)},${parseInt(hex.substr(2,2),16)},${parseInt(hex.substr(4,2),16)},${a})`; }
        
        let cD = getVar('--color-diesel'); let cS = getVar('--color-solar'); let cW = getVar('--color-wind'); let cB = getVar('--color-battery');
        
        let tD = {x: mx, y: mixWindow.map(d=>d.lp_diesel), type:'scatter', stackgroup:'one', fillcolor: h2r(cD, 0.35), line:{shape:'spline', color: cD}};
        let tS = {x: mx, y: mixWindow.map(d=>d.lp_solar), type:'scatter', stackgroup:'one', fillcolor: h2r(cS, 0.35), line:{shape:'spline', color: cS}};
        let tW = {x: mx, y: mixWindow.map(d=>d.lp_wind), type:'scatter', stackgroup:'one', fillcolor: h2r(cW, 0.35), line:{shape:'spline', color: cW}};
        let tB = {x: mx, y: mixWindow.map(d=>d.lp_battery < 0 ? Math.abs(d.lp_battery) : 0), type:'scatter', stackgroup:'one', fillcolor: h2r(cB, 0.35), line:{shape:'spline', color: cB}};
        let tL = {x: mx, y: mixWindow.map(d=>d.load_kw), type:'scatter', line:{shape:'spline', color: getVar('--text-main'), width: 2.5}};
        
        Plotly.react('mix-chart', [tD, tS, tW, tB, tL], { margin: { t: 10, r: 10, b: 30, l: 40 }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', xaxis: { showgrid: false }, yaxis: { showgrid: true, gridcolor: getVar('--border-color'), zeroline: false }, showlegend: false, font: {color: getVar('--text-muted')} });
    }
}
"""

with open('accu_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Unified JS written.")
