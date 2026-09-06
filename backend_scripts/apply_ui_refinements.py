import re

# ---------------------------------------------------------
# 1. Update style.css
# ---------------------------------------------------------
with open('accu_frontend/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace root variables entirely
old_root = r':root \{.*?\}\s*\[data-theme="dark"\] \{.*?\}'
new_vars = """
:root {
    /* SPACING SCALE */
    --sp-1: 4px;
    --sp-2: 8px;
    --sp-3: 12px;
    --sp-4: 16px;
    --sp-5: 24px;
    --sp-6: 32px;
    --sp-8: 48px;

    /* BORDER RADIUS SCALE */
    --radius-sm: 8px;       /* Badges, inputs, inner elements */
    --radius-md: 12px;      /* Ticker, small cards */
    --radius-lg: 16px;      /* Main cards, containers */
    --radius-pill: 9999px;  /* Buttons */

    /* LIGHT THEME (Base) */
    --bg-body: #F4F5F7;
    --bg-card: #FFFFFF;
    --bg-header: #051024;   /* Navy for light mode header */
    --bg-ticker: #0A1C3A;   /* Navy-light for light mode ticker */
    
    --text-main: #1F2937;
    --text-sec: #6B7280;
    --text-tertiary: #9CA3AF;
    --border-color: #E5E7EB;
    
    --shadow-subtle: 0 4px 20px rgba(0, 0, 0, 0.04);
    --card-border: 1px solid transparent;
    
    --comp-bg: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
    --comp-border: #DBEAFE;
    
    /* VIBRANT ACCENTS (Light Mode) */
    --color-diesel: #F59E0B;
    --color-solar:  #FBBF24;
    --color-wind:   #38BDF8;
    --color-battery:#10B981;
    --color-alert:  #EF4444;
}

[data-theme="dark"] {
    /* DARK THEME (True Black/Grey) */
    --bg-body: #0A0A0A;
    --bg-card: #1C1C1E;
    --bg-header: #0A0A0A;   /* True black header */
    --bg-ticker: #121212;   /* Very dark grey ticker */
    
    --text-main: #E5E5E5;
    --text-sec: #9A9A9A;
    --text-tertiary: #6B6B6B;
    --border-color: #2C2C2E;
    
    --shadow-subtle: none;
    --card-border: 1px solid #2C2C2E;
    
    --comp-bg: linear-gradient(135deg, #1C1C1E 0%, #242426 100%);
    --comp-border: #2C2C2E;
    
    /* DESATURATED ACCENTS (Dark Mode) */
    --color-diesel: #D97706; /* Dimmed amber */
    --color-solar:  #D97706; /* Dimmed yellow */
    --color-wind:   #0284C7; /* Dimmed blue */
    --color-battery:#059669; /* Dimmed emerald */
    --color-alert:  #DC2626; /* Dimmed red */
}
"""
css = re.sub(old_root, new_vars.strip(), css, flags=re.DOTALL)

# Refine Layout & Spacing Replacements
css = css.replace('background-color: var(--aw-navy);', 'background-color: var(--bg-header);')
css = css.replace('background-color: var(--aw-navy-light);', 'background-color: var(--bg-ticker);')
css = css.replace('background-color: var(--bg-color);', 'background-color: var(--bg-body);')
css = css.replace('padding: 28px;', 'padding: var(--sp-6);')
css = css.replace('padding: 24px;', 'padding: var(--sp-5);')
css = css.replace('padding: 16px;', 'padding: var(--sp-4);')
css = css.replace('gap: 24px;', 'gap: var(--sp-5);')
css = css.replace('gap: 20px;', 'gap: var(--sp-5);')
css = css.replace('gap: 16px;', 'gap: var(--sp-4);')
css = css.replace('gap: 8px;', 'gap: var(--sp-2);')

# Refine Typography & Colors
css = css.replace('color: var(--text-muted);', 'color: var(--text-sec);')
css = css.replace('color: var(--text-light);', 'color: var(--text-tertiary);')
css = css.replace('box-shadow: var(--card-shadow);', 'box-shadow: var(--shadow-subtle);')

# Fix ticker floating layout (SaaS style rounded ticker)
ticker_css = """
.ticker-wrap {
    background-color: var(--bg-ticker);
    color: var(--text-main);
    padding: var(--sp-3) var(--sp-4);
    overflow: hidden;
    white-space: nowrap;
    position: sticky;
    top: 92px; /* Height of the header */
    z-index: 999;
    
    /* SaaS Rounded Banner modifications */
    max-width: 1100px;
    margin: var(--sp-4) auto 0;
    border-radius: var(--radius-md);
    border: var(--card-border);
    box-shadow: var(--shadow-subtle);
}
"""
css = re.sub(r'\.ticker-wrap\s*\{[^}]+\}', ticker_css.strip(), css)

# Fix Badge rounding (nested proportional rounding)
css = css.replace('border-radius: 4px;', 'border-radius: var(--radius-sm);')
css = css.replace('border-bottom-left-radius: var(--radius-md);', 'border-bottom-left-radius: var(--radius-sm); border-top-right-radius: var(--radius-lg);')

# Ensure cards use the new radius scale
css = css.replace('border-radius: var(--radius-lg);', 'border-radius: var(--radius-lg);')

# Fix active tab underline rounding
css = css.replace('border-radius: 4px 4px 0 0;', 'border-radius: var(--radius-sm) var(--radius-sm) 0 0;')

# Ensure icons are consistent size
icon_css = """
.card-icon {
    font-size: 1.2rem; /* Uniform size */
    opacity: 0.9;
}
"""
css = re.sub(r'\.card-icon\s*\{[^}]+\}', icon_css.strip(), css)

# Hierarchy: Less heavy weights
css = css.replace('font-weight: 900;', 'font-weight: 800;')
css = css.replace('font-weight: 800;', 'font-weight: 700;') 
# Leave 700 and below alone to avoid making it too thin, but we toned down the extremes.

with open('accu_frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(css)


# ---------------------------------------------------------
# 2. Update app.js (Dynamic CSS variable usage for Chart)
# ---------------------------------------------------------
with open('accu_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Remove hardcoded COLORS dictionary and replace with CSS variable retrieval
js = re.sub(r'const COLORS = \{[^}]+\};', '', js)

chart_update_logic = """
function getVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function updateChartTheme() {
    if (globalData.length === 0) return;
    
    // Pull from CSS variables instead of hardcoded hex
    const gridColor = getVar('--border-color');
    const fontColor = getVar('--text-sec');
    
    Plotly.relayout('mix-chart', {
        'yaxis.gridcolor': gridColor,
        'font.color': fontColor
    });
    
    updateChart();
}
"""
js = re.sub(r'function updateChartTheme\(\)\s*\{[\s\S]*?updateChart\(\);\n\}', chart_update_logic.strip(), js)

# Update chart drawing to use getVar()
chart_draw_logic = """
function updateChart() {
    let startIdx = Math.max(0, currentIndex - 6);
    let endIdx = Math.min(globalData.length, currentIndex + 12);
    let windowData = globalData.slice(startIdx, endIdx);
    
    let x = windowData.map(d => d.timestamp);
    
    // Convert hex to rgba for muted fills
    function hexToRgba(hex, alpha) {
        if (!hex) return 'transparent';
        hex = hex.replace('#', '');
        let r = parseInt(hex.substring(0, 2), 16);
        let g = parseInt(hex.substring(2, 4), 16);
        let b = parseInt(hex.substring(4, 6), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    const cDiesel = getVar('--color-diesel');
    const cSolar = getVar('--color-solar');
    const cWind = getVar('--color-wind');
    const cBattery = getVar('--color-battery');
    const cLoad = getVar('--text-main');
    const cGrid = getVar('--border-color');
    
    let fillOpacity = '0.35'; // Slightly more muted for professional look
    
    let trace_diesel = { x, y: windowData.map(d => d.lp_diesel), name: 'Diesel', type: 'scatter', stackgroup: 'one', fillcolor: hexToRgba(cDiesel, fillOpacity), line: {shape: 'spline', color: cDiesel, width: 1.5} };
    let trace_solar = { x, y: windowData.map(d => d.lp_solar), name: 'Solar', type: 'scatter', stackgroup: 'one', fillcolor: hexToRgba(cSolar, fillOpacity), line: {shape: 'spline', color: cSolar, width: 1.5} };
    let trace_wind = { x, y: windowData.map(d => d.lp_wind), name: 'Wind', type: 'scatter', stackgroup: 'one', fillcolor: hexToRgba(cWind, fillOpacity), line: {shape: 'spline', color: cWind, width: 1.5} };
    let trace_battery = { x, y: windowData.map(d => d.lp_battery < 0 ? Math.abs(d.lp_battery) : 0), name: 'Battery', type: 'scatter', stackgroup: 'one', fillcolor: hexToRgba(cBattery, fillOpacity), line: {shape: 'spline', color: cBattery, width: 1.5} };
    
    let trace_load = { x, y: windowData.map(d => d.load_kw), name: 'Load', type: 'scatter', line: {shape: 'spline', color: cLoad, width: 2.5} };

    let data = [trace_diesel, trace_solar, trace_wind, trace_battery, trace_load];
    
    let shapes = [{
        type: 'line',
        x0: globalData[currentIndex].timestamp,
        x1: globalData[currentIndex].timestamp,
        y0: 0,
        y1: 1,
        yref: 'paper',
        line: { color: getVar('--text-tertiary'), width: 2, dash: 'dot' }
    }];

    Plotly.react('mix-chart', data, {
        margin: { t: 10, r: 10, b: 30, l: 40 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        xaxis: { showgrid: false },
        yaxis: { showgrid: true, gridcolor: cGrid, zeroline: false },
        showlegend: true,
        legend: { orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'right', x: 1 },
        shapes: shapes,
        font: { family: 'Roboto, sans-serif', color: getVar('--text-sec') }
    });
}
"""
js = re.sub(r'function updateChart\(\)\s*\{[\s\S]*?\}\n\n', chart_draw_logic.strip() + '\n\n', js)

with open('accu_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Senior UI refinements applied!")
