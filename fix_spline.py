import re

with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add line_shape="spline" to all go.Scatter that don't already have it
code = re.sub(
    r'(go\.Scatter\([^)]+)(line=dict\()',
    r'\1line_shape="spline", \2',
    code
)

# And fix line_shape being duplicated if the script runs twice
code = re.sub(r'line_shape="spline",\s*line_shape="spline",', 'line_shape="spline",', code)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Added splines to all charts!")
