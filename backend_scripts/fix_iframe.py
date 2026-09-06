import os

# Read app.js
with open('frontend/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Fix the requestAnimationFrame bug
old_loop = """    let lastTime = performance.now();
    let simTime = 0;

    function frame(timestamp) {
        const dt = (timestamp - lastTime) / 1000;
        lastTime = timestamp;"""

new_loop = """    let lastTime = null;
    let simTime = 0;

    function frame(timestamp) {
        if (lastTime === null) lastTime = timestamp;
        let dt = (timestamp - lastTime) / 1000;
        if (dt < 0 || dt > 1) dt = 0.016; // Safety clamp for iframe anomalies
        lastTime = timestamp;"""

if old_loop in app_js:
    app_js = app_js.replace(old_loop, new_loop)
    with open('frontend/app.js', 'w', encoding='utf-8') as f:
        f.write(app_js)
    print("Fixed requestAnimationFrame bug in app.js")
else:
    print("Could not find the target code in app.js!")

# Let's also fix the simulation time being negative just in case
# Wait, clamping dt ensures it's never negative.

# Let's also add a CSS fix to guarantee width/height isn't 0
with open('frontend/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

if "width: 100vw;" in css:
    css = css.replace("width: 100vw;", "width: 100%;")
if "height: 100vh;" in css:
    css = css.replace("height: 100vh;", "height: 100%;")
    
with open('frontend/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)

# Also fix resize Canvas to be foolproof
resize_old = """    function resizeCanvas() {
        const rect = container.getBoundingClientRect();
        renderer.resize(rect.width, rect.height, rect.width / 2, rect.height / 2);
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();"""

resize_new = """    function resizeCanvas() {
        const rect = container.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
            renderer.resize(rect.width, rect.height, rect.width / 2, rect.height / 2);
        }
    }
    window.addEventListener('resize', resizeCanvas);
    setInterval(resizeCanvas, 500); // Failsafe for iframes
    resizeCanvas();"""

if resize_old in app_js:
    app_js = app_js.replace(resize_old, resize_new)
    with open('frontend/app.js', 'w', encoding='utf-8') as f:
        f.write(app_js)
    print("Fixed resize logic in app.js")

# And finally, run bundle.py to regenerate bundled.html
import subprocess
subprocess.run(["python", "bundle.py"])
print("Re-bundled frontend.")
