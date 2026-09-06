import re

# 1. Update index.html
with open('accu_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace tabs with anchor links
old_tabs = """<nav class="tabs">
                <a href="#" class="active">Live Monitoring</a>
                <a href="#">Overview</a>
                <a href="#">Source Breakdown</a>
                <a href="#">AI vs Manual</a>
                <a href="#">Forecast</a>
            </nav>"""

new_tabs = """<nav class="tabs">
                <a href="#section-live" class="tab-link active">Live Monitoring</a>
                <a href="#section-live" class="tab-link">Overview</a>
                <a href="#section-sources" class="tab-link">Source Breakdown</a>
                <a href="#section-ai" class="tab-link">AI vs Manual</a>
                <a href="#section-forecast" class="tab-link">Forecast</a>
            </nav>"""
html = html.replace(old_tabs, new_tabs)

# Add IDs to sections
html = html.replace('<div class="top-row">', '<div class="top-row" id="section-live">')
html = html.replace('<div class="comparison-card">', '<div class="comparison-card" id="section-ai">')
html = html.replace('<div class="card-grid">', '<div class="card-grid" id="section-sources">')
html = html.replace('<div class="chart-section">', '<div class="chart-section" id="section-forecast">')

with open('accu_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 2. Update style.css
with open('accu_frontend/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Add sticky header and smooth scrolling
css_updates = """
html {
    scroll-behavior: smooth;
    scroll-padding-top: 140px; /* Accounts for sticky header + ticker */
}

/* =========================================
   HEADER & NAVIGATION
========================================= */
.aw-header {
    background-color: var(--aw-navy);
    color: #FFF;
    padding-top: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    position: sticky;
    top: 0;
    z-index: 1000;
}
"""
css = re.sub(r'/\* =========================================\s*HEADER & NAVIGATION\s*========================================= \*/\s*\.aw-header {[^}]+}', css_updates.strip(), css)

# Make ticker sticky too so it stays under the header
ticker_update = """
.ticker-wrap {
    background-color: var(--aw-navy-light);
    color: #FFF;
    padding: 8px 0;
    overflow: hidden;
    white-space: nowrap;
    position: sticky;
    top: 92px; /* Height of the header */
    z-index: 999;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
"""
css = re.sub(r'\.ticker-wrap {[^}]+}', ticker_update.strip(), css)

with open('accu_frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(css)


# 3. Update app.js
with open('accu_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

tab_logic = """
// Tab click logic
document.querySelectorAll('.tab-link').forEach(link => {
    link.addEventListener('click', function(e) {
        // Update active class immediately on click
        document.querySelectorAll('.tab-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});

document.addEventListener("DOMContentLoaded", () => {
"""
js = js.replace('document.addEventListener("DOMContentLoaded", () => {', tab_logic)

with open('accu_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Tabs fixed!")
