import re

with open('accu_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

ticker_code = """
    // TICKER UPDATE
    const tickerBadge = document.getElementById('ticker-badge');
    const tickerMsg = document.getElementById('ticker-msg');
    if (tickerBadge && tickerMsg) {
        if (overrides.storm) {
            tickerBadge.textContent = "CRITICAL";
            tickerBadge.className = "ticker-badge danger";
            tickerMsg.textContent = "SEVERE STORM DETECTED — Wind generation cut off to prevent turbine damage. Initiating load shedding.";
        } else if (overrides.cold) {
            tickerBadge.textContent = "WARNING";
            tickerBadge.className = "ticker-badge warning";
            tickerMsg.textContent = "EXTREME COLD ALERT — Heating load spiked. Battery derating limits capacity. Non-critical loads shed.";
        } else if (overrides.night) {
            tickerBadge.textContent = "INFO";
            tickerBadge.className = "ticker-badge safe";
            tickerMsg.textContent = "POLAR NIGHT — Zero solar irradiance. System relying entirely on wind and diesel reserves.";
        } else if (risk > 70) {
            tickerBadge.textContent = "CRITICAL";
            tickerBadge.className = "ticker-badge danger";
            tickerMsg.textContent = "SYSTEM AT RISK — Battery depleted and generation insufficient. Diesel generator at maximum capacity.";
        } else if (risk > 40) {
            tickerBadge.textContent = "WARNING";
            tickerBadge.className = "ticker-badge warning";
            tickerMsg.textContent = "WEATHER WARNING — Grid stability is compromised. Monitoring renewable reserves.";
        } else {
            tickerBadge.textContent = "INFO";
            tickerBadge.className = "ticker-badge safe";
            tickerMsg.textContent = "System status optimal — AI maximizing renewable penetration.";
        }
    }
"""

js = js.replace("document.getElementById('decision-text').textContent = getDecisionText(row);", 
                "document.getElementById('decision-text').textContent = getDecisionText(row);" + ticker_code)

with open('accu_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
