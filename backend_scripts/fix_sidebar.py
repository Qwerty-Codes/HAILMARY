with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('st.title("🏔️ Polar EMS")', 'st.title("System Status")')
code = code.replace('st.title("Demo Home")', 'st.title("Load Optimizer")')
code = code.replace('st.sidebar.title("Navigation")', 'st.sidebar.divider()\nst.sidebar.title("Navigation")')

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
