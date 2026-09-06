css_additions = """
/* GRID UPDATES */
.grid-5 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--sp-4);
}

/* ENERGY FLOW DIAGRAM */
.flow-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--card-translucent);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--sp-6) var(--sp-8);
    position: relative;
}

.flow-col {
    display: flex;
    flex-direction: column;
    gap: 16px;
    position: relative;
    z-index: 2;
    min-width: 140px;
}

.flow-node {
    background: var(--bg-page);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 12px;
    text-align: center;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}

.flow-val {
    font-size: 1.1rem;
    color: var(--text-main);
    display: block;
    margin-top: 4px;
}

.flow-node.active-solar { border-color: var(--color-solar); box-shadow: 0 0 10px rgba(255,183,77,0.2); }
.flow-node.active-wind { border-color: var(--color-wind); box-shadow: 0 0 10px rgba(129,212,250,0.2); }
.flow-node.active-diesel { border-color: var(--color-diesel); box-shadow: 0 0 10px rgba(239,83,80,0.2); }
.flow-node.active-battery { border-color: var(--color-battery); box-shadow: 0 0 10px rgba(102,187,106,0.2); }
.flow-node.active-crit { border-color: var(--color-battery); color: var(--color-battery); }
.flow-node.shedding { border-color: var(--color-alert); color: var(--color-alert); opacity: 0.5; }

.flow-path {
    flex: 1;
    height: 4px;
    background: var(--border-color);
    position: relative;
    margin: 0 16px;
    border-radius: 2px;
    overflow: hidden;
    z-index: 1;
}

.wire-animated {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
    background-size: 200% 100%;
    opacity: 0;
}

.wire-animated.flowing {
    opacity: 1;
    animation: flowAnim 1.5s linear infinite;
}

.wire-animated.flowing-diesel { background: linear-gradient(90deg, transparent, var(--color-diesel), transparent); opacity: 1; animation: flowAnim 1s linear infinite; }
.wire-animated.flowing-ren { background: linear-gradient(90deg, transparent, var(--color-battery), transparent); opacity: 1; animation: flowAnim 1.5s linear infinite; }

@keyframes flowAnim {
    0% { background-position: 100% 0; }
    100% { background-position: -100% 0; }
}

@media (max-width: 768px) {
    .flow-container { flex-direction: column; gap: 24px; padding: var(--sp-4); }
    .flow-path { width: 4px; height: 40px; margin: 16px 0; }
    .wire-animated { background: linear-gradient(180deg, transparent, rgba(255,255,255,0.8), transparent); background-size: 100% 200%; }
    @keyframes flowAnim { 0% { background-position: 0 100%; } 100% { background-position: 0 -100%; } }
}
"""

with open('accu_frontend/style.css', 'a', encoding='utf-8') as f:
    f.write(css_additions)
print("style.css patched successfully.")
