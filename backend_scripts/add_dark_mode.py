import re

# ---------------------------------------------------------
# 1. Update style.css
# ---------------------------------------------------------
with open('accu_frontend/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace root variables and add data-theme="dark"
old_root = r':root \{[^}]+\}'
new_vars = """
:root {
    /* Base AccuWeather Colors */
    --aw-navy: #051024;
    --aw-navy-light: #0A1C3A;
    
    /* Semantic/Source Colors (adjusted for both themes) */
    --color-diesel: #F59E0B; /* Amber */
    --color-solar:  #FCD34D; /* Yellow */
    --color-wind:   #38BDF8; /* Sky Blue */
    --color-battery:#10B981; /* Emerald Green */
    --color-alert:  #EF4444; /* Red */
    
    /* Light Theme (Default) */
    --bg-color: #F0F2F5;
    --card-bg: #FFFFFF;
    --text-main: #1F2937;
    --text-muted: #6B7280;
    --text-light: #9CA3AF;
    --border-color: #E5E7EB;
    --card-shadow: 0 4px 12px rgba(0,0,0,0.06);
    --card-border: 1px solid transparent;
    --comp-bg: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
    --comp-border: #DBEAFE;
}

[data-theme="dark"] {
    /* Dark Theme */
    --bg-color: #0B1120;
    --card-bg: #111827;
    --text-main: #F3F4F6;
    --text-muted: #9CA3AF;
    --text-light: #6B7280;
    --border-color: #1F2937;
    --card-shadow: none;
    --card-border: 1px solid #1F2937;
    --comp-bg: linear-gradient(135deg, #111827 0%, #1F2937 100%);
    --comp-border: #374151;
}

/* Fluid Transitions */
body, .hero-card, .source-card, .chart-section, .comparison-card, 
h1, h2, h3, span, div, .card-bottom, .hero-secondary, .ticker-wrap, .aw-header {
    transition: background-color 0.3s ease, background 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

/* Theme Toggle Button */
.theme-switch {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 20px;
    width: 48px;
    height: 28px;
    position: relative;
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 0;
    margin-left: 16px;
    outline: none;
}

.theme-switch .icon {
    position: absolute;
    font-size: 14px;
    transition: all 0.4s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.theme-switch .sun-icon {
    left: 6px;
    opacity: 1;
    transform: rotate(0deg) scale(1);
}

.theme-switch .moon-icon {
    right: 6px;
    opacity: 0;
    transform: rotate(-90deg) scale(0);
}

[data-theme="dark"] .theme-switch .sun-icon {
    opacity: 0;
    transform: rotate(90deg) scale(0);
}

[data-theme="dark"] .theme-switch .moon-icon {
    opacity: 1;
    transform: rotate(0deg) scale(1);
}
"""
css = re.sub(old_root, new_vars.strip(), css)

# Replace hardcoded colors with CSS variables
css = css.replace('background-color: var(--aw-bg);', 'background-color: var(--bg-color);')
css = css.replace('background: var(--aw-card);', 'background: var(--card-bg);\n    border: var(--card-border);')
css = css.replace('box-shadow: var(--shadow-md);', 'box-shadow: var(--card-shadow);')
css = css.replace('border-top: 1px solid var(--aw-border);', 'border-top: 1px solid var(--border-color);')
css = css.replace('border: 1px solid #DBEAFE;', 'border: 1px solid var(--comp-border);')
css = css.replace('background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);', 'background: var(--comp-bg);')

with open('accu_frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(css)


# ---------------------------------------------------------
# 2. Update index.html
# ---------------------------------------------------------
with open('accu_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add theme toggle button next to clock
clock_str = '<div class="clock" id="live-clock">00:00:00 UTC</div>'
new_clock_str = """<div class="header-actions" style="display: flex; align-items: center;">
                    <div class="clock" id="live-clock">00:00:00 UTC</div>
                    <button class="theme-switch" id="theme-toggle" aria-label="Toggle Dark Mode">
                        <span class="icon sun-icon">☀️</span>
                        <span class="icon moon-icon">🌙</span>
                    </button>
                </div>"""
html = html.replace(clock_str, new_clock_str)

with open('accu_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)


# ---------------------------------------------------------
# 3. Update app.js
# ---------------------------------------------------------
with open('accu_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add theme logic
theme_logic = """
// --- Theme Logic ---
let isDarkMode = false;

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        isDarkMode = true;
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    
    document.getElementById('theme-toggle').addEventListener('click', () => {
        isDarkMode = !isDarkMode;
        if (isDarkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        }
        updateChartTheme();
    });
}

function updateChartTheme() {
    if (globalData.length === 0) return;
    
    const gridColor = isDarkMode ? '#1F2937' : '#E5E7EB';
    const fontColor = isDarkMode ? '#9CA3AF' : '#6B7280';
    
    Plotly.relayout('mix-chart', {
        'yaxis.gridcolor': gridColor,
        'font.color': fontColor
    });
    
    // We also need to redraw to update the Load line color (White in dark, Black in light)
    updateChart();
}
"""

js = theme_logic + js

# Inside DOMContentLoaded, call initTheme()
js = js.replace('initClock();', 'initTheme();\n    initClock();')

# Update Plotly layout colors based on theme dynamically inside updateChart()
chart_grid_light = "yaxis: { showgrid: true, gridcolor: '#E5E7EB', zeroline: false },"
chart_grid_dynamic = "yaxis: { showgrid: true, gridcolor: isDarkMode ? '#1F2937' : '#E5E7EB', zeroline: false },"
js = js.replace(chart_grid_light, chart_grid_dynamic)

chart_font_light = "font: { family: 'Roboto, sans-serif' }"
chart_font_dynamic = "font: { family: 'Roboto, sans-serif', color: isDarkMode ? '#9CA3AF' : '#6B7280' }"
js = js.replace(chart_font_light, chart_font_dynamic)

load_line_light = "color: '#1F2937'"
load_line_dynamic = "color: isDarkMode ? '#F3F4F6' : '#1F2937'"
js = js.replace(load_line_light, load_line_dynamic)

now_line_light = "color: '#6B7280'"
now_line_dynamic = "color: isDarkMode ? '#9CA3AF' : '#6B7280'"
js = js.replace(now_line_light, now_line_dynamic)

with open('accu_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Dark mode implemented!")
