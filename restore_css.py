css = """
:root {
    /* SPACING SCALE */
    --sp-1: 4px;   --sp-2: 8px;   --sp-3: 12px;
    --sp-4: 16px;  --sp-5: 24px;  --sp-6: 32px;

    /* RADIUS SCALE */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-pill: 9999px;
    --radius-btn: 10px;

    /* DARK THEME (Black/Grey SaaS style - Source of Truth) */
    --bg-page: #050505;
    --bg-card: #161616;
    --bg-ticker: #111111;
    
    --border-color: #282828;
    
    --text-main: #FFFFFF;
    --text-muted: #8A8A8A;
    
    /* DESATURATED ACCENTS */
    --color-diesel: #D97706;  /* Dimmed amber */
    --color-solar:  #D97706;  /* Dimmed yellow/amber */
    --color-wind:   #0284C7;  /* Dimmed blue */
    --color-battery:#059669;  /* Dimmed emerald */
    --color-alert:  #DC2626;  /* Dimmed red */
    
    --color-load: #E86A33;    /* Muted Orange for Twin */
    --color-ren: #4ADE80;     /* Muted Green for Twin */
}

/* Light Theme overrides for the toggle */
[data-theme="light"] {
    --bg-page: #F0F2F5;
    --bg-card: #FFFFFF;
    --bg-ticker: #0A1C3A;
    --border-color: #E5E7EB;
    
    --text-main: #1F2937;
    --text-muted: #6B7280;
    
    --color-diesel: #F59E0B;
    --color-wind:   #38BDF8;
    --color-battery:#10B981;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-page);
    color: var(--text-main);
    line-height: 1.5;
    min-height: 100vh;
    padding: 20px 20px;
    -webkit-font-smoothing: antialiased;
    transition: background-color 0.3s ease, color 0.3s ease;
}

.dashboard-container {
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: var(--sp-5);
}

/* HEADER */
.aw-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 8px;
    background-color: var(--bg-page);
    transition: background-color 0.3s ease;
}

.eyebrow {
    display: block;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}

h1 { font-size: 1.75rem; font-weight: 700; letter-spacing: -0.02em; }

.live-badge {
    background: rgba(59, 130, 246, 0.1);
    color: #93C5FD;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: var(--radius-pill);
    display: flex;
    align-items: center;
    gap: 8px;
}

.pulse-dot {
    width: 8px; height: 8px;
    background-color: #3B82F6;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } 100% { opacity: 1; transform: scale(1); } }

/* TICKER */
.ticker-wrap {
    background-color: var(--bg-ticker);
    color: #FFF;
    padding: var(--sp-3) var(--sp-4);
    overflow: hidden;
    white-space: nowrap;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 12px;
    transition: background-color 0.3s ease, border-color 0.3s ease;
}

.ticker-badge {
    padding: 2px 8px;
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    font-weight: 700;
}
.ticker-badge.safe { background: var(--color-battery); color: #000; }
.ticker-badge.warning { background: var(--color-diesel); color: #000; }
.ticker-badge.danger { background: var(--color-alert); color: #FFF; }

/* TABS */
.aw-tabs {
    display: flex;
    gap: 24px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0;
    margin-bottom: 16px;
}

.tab-link {
    color: var(--text-muted);
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 600;
    padding: 8px 0;
    position: relative;
    cursor: pointer;
}

.tab-link.active {
    color: var(--text-main);
}

.tab-link.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--color-diesel);
    border-radius: 3px 3px 0 0;
}

/* SECTIONS */
.dashboard-section { display: none; }
.dashboard-section.active-section { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

/* CARDS */
.card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--sp-5);
    transition: background-color 0.3s ease, border-color 0.3s ease;
}

.row { display: flex; gap: var(--sp-5); width: 100%; margin-bottom: var(--sp-5); }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--sp-5); }
.split-60-40 { display: grid; grid-template-columns: 1.4fr 1fr; gap: var(--sp-5); }

h2 { font-size: 1.1rem; font-weight: 600; margin-bottom: 4px; }
.subtitle { font-size: 0.85rem; color: var(--text-muted); }
.label { font-size: 0.85rem; color: var(--text-muted); font-weight: 500; }
.value { font-size: 1.8rem; font-weight: 700; letter-spacing: -0.02em; }

/* CHARTS */
.chart-legend { display: flex; gap: 16px; margin-top: 16px; }
.legend-item { font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot-load { background-color: var(--color-load); }
.dot-ren { background-color: var(--color-ren); }

/* LISTS */
.list-container { display: flex; flex-direction: column; gap: 16px; margin-top: 24px; }
.list-row { display: flex; justify-content: space-between; align-items: center; }
.list-label { font-size: 0.9rem; color: var(--text-muted); }
.list-val { font-size: 0.95rem; font-weight: 600; }

/* DECISION */
#decision-text { margin-top: 8px; font-size: 0.95rem; color: var(--text-main); line-height: 1.4; opacity: 0.9; }

/* BUTTONS */
.btn-outline {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-main);
    padding: 10px 16px;
    border-radius: var(--radius-btn);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}
.btn-outline:hover { background: rgba(255,255,255,0.05); }

/* THEME SWITCH */
.theme-switch {
    background: rgba(128, 128, 128, 0.2);
    border: none;
    border-radius: 20px;
    width: 48px; height: 28px;
    position: relative;
    cursor: pointer;
    display: flex;
    align-items: center;
}
.theme-switch .icon { position: absolute; font-size: 14px; transition: all 0.4s ease; }
.theme-switch .sun-icon { left: 6px; opacity: 0; transform: rotate(90deg) scale(0); }
.theme-switch .moon-icon { right: 6px; opacity: 1; transform: rotate(0deg) scale(1); }

[data-theme="light"] .theme-switch .sun-icon { opacity: 1; transform: rotate(0deg) scale(1); }
[data-theme="light"] .theme-switch .moon-icon { opacity: 0; transform: rotate(-90deg) scale(0); }
"""

with open('accu_frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Unified CSS written.")
