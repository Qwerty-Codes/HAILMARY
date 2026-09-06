import re

with open('accu_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the hardcoded inline styles that block the tab JS from showing the sections
html = html.replace('style="display: none;"', '')

with open('accu_frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Removed inline display:none blocking the tabs.")
