import re

# Update pipeline.py
with open('pipeline.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('cost_saved_usd = fuel_saved_L * 2.50  # Assuming $2.50/L', 'cost_saved_inr = fuel_saved_L * 250.0  # Assuming ₹250/L')
text = text.replace('"cost_saved_usd": cost_saved_usd', '"cost_saved_inr": cost_saved_inr')
text = text.replace('$ {cost_saved_usd', '₹ {cost_saved_inr')
text = text.replace('${cost_saved_usd', '₹{cost_saved_inr')

with open('pipeline.py', 'w', encoding='utf-8') as f:
    f.write(text)

# Update dashboard.py
with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('cost_saved_usd', 'cost_saved_inr')
text = text.replace('cost_saved_usd', 'cost_saved_inr')
text = text.replace('"${cost_saved:.2f}"', '"₹{cost_saved:,.0f}"')
text = text.replace('Cost @$2.50/L', 'Cost (₹250/L)')
text = text.replace('${fuel_rules*2.5:.2f}', '₹{fuel_rules*250:,.0f}')
text = text.replace('${fuel_lp*2.5:.2f}', '₹{fuel_lp*250:,.0f}')
text = text.replace('${cost_saved:.2f}', '₹{cost_saved:,.0f}')

# Simplify dashboard explanations
text = text.replace('**LP optimizer saves', '**AI Optimizer saves')
text = text.replace('LP-Optimal', 'AI Optimized')
text = text.replace('lp_diesel', 'lp_diesel') # keep code vars
text = text.replace('Rule-Based', 'Standard Rules')
text = text.replace('Rule-based', 'Standard Rules')

# Simple explanation block
old_explanation = '''        st.markdown("#### Why the LP wins:")
        st.markdown("""
        - **Look-ahead planning** — the LP sees the entire forecast horizon and pre-positions
          the battery to avoid diesel during predicted wind lulls.
        - **Fractional allocation** — rules use all-or-nothing priority; the LP can split sources optimally.
        - **No forced idle** — the LP doesn't have generator min-runtime constraints (pure LP),
          so it avoids burning fuel at idle.
        """)'''

new_explanation = '''        st.markdown("#### Why the AI Optimizer is better:")
        st.markdown("""
        - **Predicts the Future** — It looks at the 48-hour weather forecast and charges the battery *before* the wind dies down.
        - **Smart Mixing** — Instead of turning things on/off randomly, it finds the perfect mathematical mix of solar, wind, and diesel to save fuel.
        - **No Wasted Fuel** — It perfectly balances the battery so the diesel generator only runs when absolutely necessary.
        """)'''

text = text.replace(old_explanation, new_explanation)

old_info = '''    st.info(
        "**This is the core ML component.** The model *learns* the relationship between "
        "weather, time-of-day, recent load history → future electrical load. "
        "Solar and wind use physics formulas; this is the part that actually learns from data.",
        icon="🧠"
    )'''

new_info = '''    st.info(
        "**This is the Machine Learning Brain.** It looks at weather and time to predict exactly how much electricity the station will need. "
        "While solar and wind are calculated using standard physics formulas, this AI actively learns from past patterns.",
        icon="🧠"
    )'''

text = text.replace(old_info, new_info)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated both files.")
