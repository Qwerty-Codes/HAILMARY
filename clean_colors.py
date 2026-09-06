import re

with open('accu_frontend/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace hardcoded header/badge colors with design tokens
css = css.replace('color: #FFF;', 'color: var(--text-main);')
css = css.replace('color: #94A3B8;', 'color: var(--text-tertiary);')
css = css.replace('color: #E2E8F0;', 'color: var(--text-main);')
css = css.replace('color: var(--aw-navy);', 'color: var(--text-main);')
css = css.replace('color: #064E3B;', 'color: var(--bg-body);') # Badges in dark mode need contrast against battery green

with open('accu_frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Remaining hardcoded colors cleaned.")
