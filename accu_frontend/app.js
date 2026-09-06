// FULL APP.JS REWRITE

let globalData = [];
let currentIndex = 0;
let timerId = null;
let isPlaying = true;
let isDarkMode = true;
let cumulativeFuel = 0;
const TANK_CAPACITY = 5000;
let liveSOC = 0.6; 

let currentBgState = 'none';
let snowCanvas, snowCtx, snowParticles = [];

// Enforced mutual exclusivity: exactly one mode is always active.
// Start in normal mode.
let overrides = { night: false, storm: false, cold: false, day: false, normal: true };

window.onerror = function(message, source, lineno, colno, error) {
    document.getElementById('decision-text').textContent = "JS ERROR: " + message + " at line " + lineno;
};

Papa.parse('../output/dashboard_data.csv?cb=' + new Date().getTime(), {
    download: true,
    header: true,
    dynamicTyping: true,
    error: function(err) {
        document.getElementById('decision-text').textContent = "PapaParse ERROR: " + err;
    },
    complete: function(results) {
        try {
            globalData = results.data.filter(row => row.timestamp);
            if(globalData.length === 0) {
                document.getElementById('decision-text').textContent = "ERROR: globalData is empty.";
                return;
            }
            liveSOC = globalData[0].lp_soc;
            initTheme();
            initTabs();
            initCharts();
            initWeatherBg();
            setupControls();
            timerId = setInterval(() => tick(false), 2000);
            tick(true); // force first render immediately
        } catch(e) {
            document.getElementById('decision-text').textContent = "INIT ERROR: " + e.message;
        }
    }
});

function getVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// ----------------------------------------------------
// UNIFIED STATE & CASCADING SIMULATION PIPELINE
// ----------------------------------------------------

function setOverrideState(mode) {
    // 1. Mutually exclusive enforcement
    const modes = ['day', 'night', 'normal', 'storm', 'cold'];
    if (!modes.includes(mode)) mode = 'normal';
    
    // Uncheck everything, check the one active mode
    modes.forEach(m => {
        overrides[m] = (m === mode);
        const el = document.getElementById('tgl-' + m);
        if (el) el.checked = (m === mode);
    });
    
    // 2. Immediately force a UI recalculation to eliminate latency
    tick(true);
}

function applyOverridesToRow(baseRow, simSOC) {
    let row = { ...baseRow };
    
    // 1. Weather Inputs Patching
    if (overrides.day) {
        row.irradiance = Math.max(600, row.irradiance + 500); 
        row.temperature = Math.max(-10, row.temperature);
    } 
    else if (overrides.night) {
        row.irradiance = 0; 
    } 
    else if (overrides.storm) {
        row.wind_speed = Math.max(26.0, row.wind_speed + 15.0); 
        row.irradiance = Math.min(50, row.irradiance); 
    } 
    else if (overrides.cold) {
        row.temperature = Math.min(-35.0, row.temperature - 20.0); 
    }
    else if (overrides.normal) {
        if (row.wind_speed > 20) row.wind_speed = 15; 
        if (row.temperature < -20) row.temperature = -10; 
    }

    // 2. Base Load Calculation
    let baseLoad = row.load_kw;
    if (overrides.cold) baseLoad += 40.0;
    
    // LOAD SHEDDING LOGIC (Critical vs Non-Critical)
    let load_crit = baseLoad * 0.45; // 45% Life support/comms
    let load_non = baseLoad * 0.55;  // 55% Comfort/Science
    let shedding = false;
    
    // Determine risk
    let sim_soc = simSOC !== undefined ? simSOC : row.lp_soc;
    if (overrides.storm || overrides.cold || sim_soc < 0.35) {
        shedding = true;
        load_non = 0; // Cut non-critical loads
    }
    
    row.load_critical = load_crit;
    row.load_non_critical = load_non;
    row.shedding_active = shedding;
    row.load_kw = load_crit + load_non; // Actual applied load

    // 3. Solar Gen
    row.lp_solar = row.irradiance * 0.018;

    // 4. Wind Gen
    if (row.wind_speed < 3.0 || row.wind_speed > 25.0) {
        row.lp_wind = 0;
    } else if (row.wind_speed >= 12.0) {
        row.lp_wind = 50.0;
    } else {
        row.lp_wind = Math.pow(row.wind_speed / 12.0, 3) * 50.0;
    }

    // 5. Dynamic Re-balancing
    let ren_total = row.lp_solar + row.lp_wind;
    let deficit = row.load_kw - ren_total;
    
    if (deficit > 0) {
        let available_batt_kw = (sim_soc - 0.2) * 500; 
        if (available_batt_kw > deficit) {
            row.lp_battery = deficit;
            row.lp_diesel = 0;
        } else {
            row.lp_battery = Math.max(0, available_batt_kw);
            row.lp_diesel = deficit - row.lp_battery;
        }
    } else {
        row.lp_diesel = 0;
        let space_batt_kw = (1.0 - sim_soc) * 500;
        let charging_amount = Math.min(Math.abs(deficit), space_batt_kw);
        row.lp_battery = -charging_amount; 
    }
    
    row.wind_avail = row.lp_wind;
    row.solar_avail = row.lp_solar;
    
    return row;
}

// ----------------------------------------------------
// UI UPDATES & DOM SYNC
// ----------------------------------------------------

function setupControls() {
    const playBtn = document.getElementById('btn-pause');
    if(playBtn) playBtn.addEventListener('click', () => {
        isPlaying = !isPlaying;
        playBtn.textContent = isPlaying ? 'Pause' : 'Play';
        if (isPlaying) {
            timerId = setInterval(() => tick(false), 2000);
            tick(true); // tick immediately on unpause
        } else {
            clearInterval(timerId);
        }
    });

    const modes = ['day', 'night', 'normal', 'storm', 'cold'];
    modes.forEach(m => {
        const el = document.getElementById('tgl-' + m);
        if (el) {
            el.addEventListener('change', (e) => {
                // If the user tries to uncheck the active mode, fall back to normal
                setOverrideState(e.target.checked ? m : 'normal');
            });
        }
    });
    
    // Initialize default state visually
    setOverrideState('normal');
}

function initTheme() {
    const tBtn = document.getElementById('theme-toggle');
    if (tBtn) {
        tBtn.addEventListener('click', () => {
            isDarkMode = !isDarkMode;
            document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
            if(!isPlaying) tick(true);
        });
    }
}

function initTabs() {
    const links = document.querySelectorAll('.tab-link');
    const sections = document.querySelectorAll('.dashboard-section');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent URL hash jumping if not desired
            links.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active-section'));
            link.classList.add('active');
            const targetId = link.getAttribute('href').replace('#', '');
            const targetSec = document.getElementById(targetId);
            if(targetSec) targetSec.classList.add('active-section');
            if(!isPlaying) tick(true); // force re-render in case of chart resize
        });
    });
}

function updateVal(id, val, dp=0) {
    const el = document.getElementById(id);
    if (!el) return;
    if (val === undefined || val === null || isNaN(val)) el.textContent = '--';
    else el.textContent = val.toFixed(dp);
}

function tick(skipAdvance=false) {
    if (!skipAdvance) currentIndex = (currentIndex + 1) % globalData.length;
    
    const baseRow = globalData[currentIndex];
    if(!baseRow) return;

    // Apply simulation physics to the row
    let row = applyOverridesToRow(baseRow, liveSOC);

    // Update real live battery SOC dynamically based on the battery dispatch
    liveSOC = liveSOC - (row.lp_battery / 500);
    liveSOC = Math.max(0.2, Math.min(1.0, liveSOC));
    
    // Sync the derived SOC into the row for downstream UI components
    row.lp_soc = liveSOC;

    // --- DYNAMIC WEATHER BACKGROUND ---
    let newState = 'night';
    if (row.wind_speed >= 25.0 || (row.wind_speed > 15.0 && row.temperature < -15.0)) {
        newState = 'storm';
    } else if (row.irradiance > 50) {
        newState = 'day';
    }

    if (newState !== currentBgState) {
        document.querySelectorAll('.weather-bg').forEach(el => el.classList.remove('active'));
        const target = document.getElementById('bg-' + newState);
        if (target) target.classList.add('active');
        currentBgState = newState;
    }

    
    // RISK SCORE CALCULATION
    let risk = 10;
    if (row.wind_speed > 20) risk += (row.wind_speed - 20) * 4;
    if (row.wind_speed > 25) risk += 30; // Cutoff spike
    if (row.temperature < -15) risk += Math.abs(row.temperature + 15) * 1.5;
    if (row.lp_soc < 0.4) risk += (0.4 - row.lp_soc) * 150;
    risk = Math.min(100, Math.max(0, risk));
    updateVal('val-risk', risk, 0);
    const riskEl = document.getElementById('val-risk');
    if (riskEl) {
        riskEl.parentElement.parentElement.style.borderColor = risk > 70 ? 'var(--color-alert)' : (risk > 40 ? 'orange' : 'var(--color-battery)');
        riskEl.style.color = risk > 70 ? 'var(--color-alert)' : (risk > 40 ? 'orange' : 'var(--color-battery)');
    }

    // LOAD SHEDDING UI
    updateVal('list-load-crit', row.load_critical, 0);
    updateVal('list-load-non', row.load_non_critical, 0);
    const shedAlert = document.getElementById('shedding-alert');
    if (shedAlert) {
        shedAlert.style.display = row.shedding_active ? 'block' : 'none';
    }

    // ANIMATED FLOW DIAGRAM
    updateVal('flow-val-solar', row.lp_solar, 0);
    updateVal('flow-val-wind', row.lp_wind, 0);
    updateVal('flow-val-diesel', row.lp_diesel, 0);
    updateVal('flow-val-batt', row.lp_soc * 100, 0);
    updateVal('flow-val-crit', row.load_critical, 0);
    updateVal('flow-val-non', row.load_non_critical, 0);

    const toggleClass = (id, cls, condition) => {
        const el = document.getElementById(id);
        if (el) condition ? el.classList.add(cls) : el.classList.remove(cls);
    };

    toggleClass('node-solar', 'active-solar', row.lp_solar > 0);
    toggleClass('node-wind', 'active-wind', row.lp_wind > 0);
    toggleClass('node-diesel', 'active-diesel', row.lp_diesel > 0);
    toggleClass('node-battery', 'active-battery', row.lp_battery < 0); // charging
    toggleClass('node-noncrit', 'shedding', row.shedding_active);

    const wireGen = document.getElementById('wire-gen');
    if (wireGen) {
        wireGen.className = 'wire-animated';
        if (row.lp_diesel > 0) wireGen.classList.add('flowing-diesel');
        else if (row.lp_solar > 0 || row.lp_wind > 0) wireGen.classList.add('flowing-ren');
    }

    const wireLoad = document.getElementById('wire-load');
    if (wireLoad) {
        wireLoad.className = 'wire-animated';
        if (row.lp_diesel > 0 && row.lp_battery >= 0) wireLoad.classList.add('flowing-diesel'); // Diesel discharging to load
        else wireLoad.classList.add('flowing-ren'); // Renewables or Battery to load
    }

    // Hero Cards
    updateVal('val-temp', row.temperature, 1);
    updateVal('val-wind', row.wind_speed, 1);
    updateVal('val-solar', row.irradiance, 0);
    updateVal('val-soc', row.lp_soc * 100, 0);

    // AI vs Manual calculations (assuming 55kW flat manual generator operation for simple metric)
    let fuel_saved = Math.max(0, row.rb_diesel - row.lp_diesel) * 0.3; 
    if(!skipAdvance) cumulativeFuel += fuel_saved;
    updateVal('comp-fuel', cumulativeFuel, 1);
    updateVal('comp-cost', cumulativeFuel * 255, 0); 
    updateVal('comp-co2', cumulativeFuel * 2.68, 0); 
    
    // Source Breakdown Tab
    updateVal('src-solar', row.lp_solar, 1);
    updateVal('src-wind', row.lp_wind, 1);
    updateVal('src-diesel', row.lp_diesel, 1);
    updateVal('src-batt', row.lp_battery, 1);
    updateVal('src-load', row.load_kw, 1);
    
    const windStatEl = document.getElementById('src-wind-status');
    if (windStatEl) {
        if(row.wind_speed > 25.0) {
            windStatEl.textContent = 'CUT-OFF (PROTECTION)';
            windStatEl.style.color = getVar('--color-alert');
        } else if(row.wind_speed < 3.0) {
            windStatEl.textContent = 'BELOW CUT-IN';
            windStatEl.style.color = getVar('--color-alert');
        } else {
            windStatEl.textContent = 'GENERATING';
            windStatEl.style.color = getVar('--color-battery');
        }
    }
    
    // Digital Twin List
    updateVal('list-solar', row.lp_solar, 0);
    updateVal('list-wind', row.lp_wind, 0);
    
    
    // Normalize diesel to a % for the UI bar (0-100kW scale)
    let dPct = Math.min(100, (row.lp_diesel / Math.max(row.load_kw, 1)) * 100);
    updateVal('list-diesel', dPct, 0);

    updateVal('list-batt-temp', row.temperature + 15, 1); 

    // Alert Ticker
    const tickerBadge = document.getElementById('ticker-badge');
    const tickerText = document.getElementById('ticker-text');
    if(tickerBadge && tickerText) {
        tickerBadge.className = 'ticker-badge'; // reset
        if (row.wind_speed > 25.0) {
            tickerBadge.classList.add('danger');
            tickerBadge.textContent = 'EXTREME';
            tickerText.textContent = `WIND CUTOFF (${row.wind_speed.toFixed(1)} m/s) — Turbines locked. Diesel compensating.`;
        } else if (row.temperature < -40.0) {
            tickerBadge.classList.add('warning');
            tickerBadge.textContent = 'COLD SNAP';
            tickerText.textContent = `EXTREME COLD (${row.temperature.toFixed(1)}°C) — Maximum heating load engaged.`;
        } else if (row.lp_soc < 0.25) {
            tickerBadge.classList.add('warning');
            tickerBadge.textContent = 'LOW SOC';
            tickerText.textContent = `BATTERY AT ${(row.lp_soc*100).toFixed(0)}% — Prioritizing generator charging.`;
        } else {
            tickerBadge.classList.add('safe');
            tickerBadge.textContent = 'NORMAL';
            tickerText.textContent = `Grid stable. Temperature ${row.temperature.toFixed(1)}°C. Renewables nominal.`;
        }
    }
    
    // Decision sentence
    document.getElementById('decision-text').textContent = getDecisionText(row);
    // TICKER UPDATE
    const tickerBadge = document.getElementById('ticker-badge');
    const tickerMsg = document.getElementById('ticker-msg');
    if (tickerBadge && tickerMsg) {
        if (overrides.storm) {
            tickerBadge.textContent = "CRITICAL";
            tickerBadge.className = "ticker-badge danger";
            tickerMsg.textContent = "SEVERE STORM DETECTED — Wind generation cut off to prevent turbine damage. Initiating load shedding.";
        } else if (overrides.cold) {
            tickerBadge.textContent = "WARNING";
            tickerBadge.className = "ticker-badge warning";
            tickerMsg.textContent = "EXTREME COLD ALERT — Heating load spiked. Battery derating limits capacity. Non-critical loads shed.";
        } else if (overrides.night) {
            tickerBadge.textContent = "INFO";
            tickerBadge.className = "ticker-badge safe";
            tickerMsg.textContent = "POLAR NIGHT — Zero solar irradiance. System relying entirely on wind and diesel reserves.";
        } else if (risk > 70) {
            tickerBadge.textContent = "CRITICAL";
            tickerBadge.className = "ticker-badge danger";
            tickerMsg.textContent = "SYSTEM AT RISK — Battery depleted and generation insufficient. Diesel generator at maximum capacity.";
        } else if (risk > 40) {
            tickerBadge.textContent = "WARNING";
            tickerBadge.className = "ticker-badge warning";
            tickerMsg.textContent = "WEATHER WARNING — Grid stability is compromised. Monitoring renewable reserves.";
        } else {
            tickerBadge.textContent = "INFO";
            tickerBadge.className = "ticker-badge safe";
            tickerMsg.textContent = "System status optimal — AI maximizing renewable penetration.";
        }
    }

    
    // Charts update with full cascade
    updateCharts();
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

// ----------------------------------------------------
// CHARTS (Plotly)
// ----------------------------------------------------

function initCharts() {
    const layoutBase = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 10, r: 10, b: 40, l: 40 },
        xaxis: { showgrid: false, zeroline: false, color: getVar('--text-muted'), tickformat: '%H:%M' },
        yaxis: { showgrid: true, gridcolor: getVar('--border-color'), zeroline: false, color: getVar('--text-muted') },
        showlegend: false,
        font: { family: 'Inter' }
    };
    
    Plotly.newPlot('balance-chart', [{x:[], y:[], type:'scatter'}], layoutBase, {displayModeBar: false});
    Plotly.newPlot('mix-chart', [{x:[], y:[], type:'scatter'}], layoutBase, {displayModeBar: false});
}

function updateCharts() {
    const layoutBase = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 10, r: 10, b: 40, l: 40 },
        xaxis: { showgrid: false, zeroline: false, color: getVar('--text-muted'), tickformat: '%H:%M' },
        yaxis: { showgrid: true, gridcolor: getVar('--border-color'), zeroline: false, color: getVar('--text-muted') },
        showlegend: false,
        font: { family: 'Inter' }
    };

    let startIdx = Math.max(0, currentIndex - 24);
    let endIdx = Math.min(globalData.length, currentIndex + 1);
    if(endIdx - startIdx < 2) return;
    
    let rawData = globalData.slice(startIdx, endIdx);
    
    let windowData = rawData.map(d => applyOverridesToRow(d));
    
    // Pass full datetime string to Plotly so it treats x-axis as chronological instead of categorical
    let xDays = windowData.map(d => String(d.timestamp));
    
    let tL = windowData.map(d => d.load_kw);
    let tRen = windowData.map(d => d.lp_solar + d.lp_wind);

    Plotly.react('balance-chart', [
        { x: xDays, y: tL, type: 'scatter', mode: 'lines', name: 'Load', line: {color: getVar('--color-load'), width: 2, shape: 'spline'} },
        { x: xDays, y: tRen, type: 'scatter', mode: 'lines', name: 'Renewables', line: {color: getVar('--color-ren'), width: 2, shape: 'spline'} }
    ], layoutBase, {displayModeBar: false});

    let xMix = [];
    let mixL = [];
    let mixS = [];
    let mixW = [];
    let mixD = [];
    
    let rawMixWindow = globalData.slice(Math.max(0, currentIndex - 6), Math.min(globalData.length, currentIndex + 12));
    let mixWindow = rawMixWindow.map(d => applyOverridesToRow(d));

    for(let d of mixWindow) {
        xMix.push(String(d.timestamp));
        mixL.push(d.load_kw);
        mixS.push(d.lp_solar);
        mixW.push(d.lp_wind);
        mixD.push(d.lp_diesel);
    }

    Plotly.react('mix-chart', [
        { x: xMix, y: mixS, type: 'scatter', mode: 'lines', name: 'Solar', line: {color: getVar('--color-solar'), shape: 'spline'} },
        { x: xMix, y: mixW, type: 'scatter', mode: 'lines', name: 'Wind', line: {color: getVar('--color-wind'), shape: 'spline'} },
        { x: xMix, y: mixD, type: 'scatter', mode: 'lines', name: 'Diesel', line: {color: getVar('--color-diesel'), shape: 'spline', dash: 'dot'} },
        { x: xMix, y: mixL, type: 'scatter', mode: 'lines', name: 'Load', line: {color: getVar('--text-muted'), shape: 'spline', width: 1} }
    ], layoutBase, {displayModeBar: false});
}

// ----------------------------------------------------
// WEATHER CANVAS
// ----------------------------------------------------

function initWeatherBg() {
    snowCanvas = document.getElementById("snow-canvas");
    if(!snowCanvas) return;
    snowCtx = snowCanvas.getContext("2d");
    
    function resize() {
        snowCanvas.width = window.innerWidth;
        snowCanvas.height = window.innerHeight;
    }
    window.addEventListener("resize", resize);
    resize();

    for(let i=0; i<150; i++) {
        snowParticles.push({
            x: Math.random() * snowCanvas.width,
            y: Math.random() * snowCanvas.height,
            vx: (Math.random() * 15 + 10), 
            vy: (Math.random() * 8 + 5),   
            r: Math.random() * 2 + 1,      
            alpha: Math.random() * 0.6 + 0.2
        });
    }
    
    requestAnimationFrame(renderSnow);
}

function renderSnow() {
    requestAnimationFrame(renderSnow);
    
    if (currentBgState !== "storm") return; 
    
    snowCtx.clearRect(0, 0, snowCanvas.width, snowCanvas.height);
    snowCtx.fillStyle = "white";
    
    snowParticles.forEach(p => {
        snowCtx.globalAlpha = p.alpha;
        snowCtx.beginPath();
        snowCtx.arc(p.x, p.y, p.r, 0, Math.PI*2);
        snowCtx.fill();
        
        p.x += p.vx;
        p.y += p.vy;
        
        if (p.x > snowCanvas.width) p.x = 0;
        if (p.y > snowCanvas.height) p.y = 0;
    });
}
