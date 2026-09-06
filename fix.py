with open('config.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('FUEL_COST_PER_LITER = 2.50          # USD/liter', 'FUEL_COST_PER_LITER = 250.0         # INR/liter')
with open('config.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('pipeline.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('results["cost_saved_usd"] = cost_saved', 'results["cost_saved_inr"] = cost_saved')
text = text.replace('print(f"  Cost saved:      ${cost_saved:>8.2f}")', 'print(f"  Cost saved:      ₹{cost_saved:>8.0f}")')
text = text.replace('= ${cost_saved:.2f}', '= ₹{cost_saved:.0f}')
with open('pipeline.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed!')
