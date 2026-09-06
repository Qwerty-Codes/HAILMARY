with open('frontend/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace("font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;", "font-family: 'Roboto', 'Samsung Sans', system-ui, -apple-system, sans-serif;")
css = css.replace("background: var(--bg);", "background: #000000;")
css = css.replace("background: #000;", "background: #000000;")

with open('frontend/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)

import subprocess
subprocess.run(["python", "bundle.py"])
