import json

def bundle_frontend():
    with open('frontend/index.html', 'r', encoding='utf-8') as f: html = f.read()
    with open('frontend/styles.css', 'r', encoding='utf-8') as f: css = f.read()
    with open('frontend/buildings.js', 'r', encoding='utf-8') as f: bjs = f.read()
    with open('frontend/renderer.js', 'r', encoding='utf-8') as f: rjs = f.read()
    with open('frontend/simulation.js', 'r', encoding='utf-8') as f: sjs = f.read()
    with open('frontend/app.js', 'r', encoding='utf-8') as f: ajs = f.read()

    # --- INJECT AI DATA HOOK INTO SIMULATION ---
    ai_hook = """
        if (window.STATION_DATA && window.STATION_DATA.length > 0) {
            let hourIndex = Math.floor(this.time) % window.STATION_DATA.length;
            if (hourIndex < 0) hourIndex += window.STATION_DATA.length;
            const data = window.STATION_DATA[hourIndex];
            
            this.state.outsideTemp = data.temperature;
            this.state.domeTemp = Math.max(5, data.temperature + 40); 
            this.state.solarGen = data.lp_solar;
            this.state.windGen = data.lp_wind;
            this.state.backupGen = data.lp_diesel;
            
            let totalLoad = data.load_kw;
            
            const consumers = this.buildings.filter(b => b.basePower > 0);
            const totalBase = consumers.reduce((sum, b) => sum + b.basePower, 0);
            
            consumers.forEach(b => {
                const bState = this.state.buildings[b.id];
                const ratio = b.basePower / totalBase;
                const power = totalLoad * ratio * (0.9 + Math.random()*0.2);
                bState.currentPower = power;
                bState.loadPercent = (power / (b.basePower * 1.5)) * 100;
                
                if (b.id === 'vcv_dome') bState.temperature = this.state.domeTemp;
                else bState.temperature = 20 + Math.random() * 1.5;
                
                bState.history.push(Math.abs(bState.currentPower));
                bState.history.shift();
                
                if (bState.loadPercent > 90) bState.status = 'critical';
                else if (bState.loadPercent > 75) bState.status = 'warning';
                else bState.status = 'normal';
            });
            
            const producers = this.buildings.filter(b => b.basePower <= 0);
            producers.forEach(b => {
                const bState = this.state.buildings[b.id];
                bState.currentPower = -(this.state.solarGen + this.state.windGen);
                bState.loadPercent = Math.min(100, (Math.abs(bState.currentPower) / 1500) * 100);
                bState.history.push(Math.abs(bState.currentPower));
                bState.history.shift();
                bState.status = 'normal';
            });
            
            this.state.totalLoad = totalLoad;
            return;
        }
    """
    
    # Insert the hook right after `if (this.time >= 24) this.time -= 24;`
    sjs = sjs.replace('if (this.time >= 24) this.time -= 24;', 'if (this.time >= 24) this.time -= 24;\n' + ai_hook)

    html = html.replace('<link rel="stylesheet" href="styles.css">', f'<style>{css}</style>')
    html = html.replace('<script src="buildings.js"></script>', f'<script>{bjs}</script>')
    html = html.replace('<script src="renderer.js"></script>', f'<script>{rjs}</script>')
    html = html.replace('<script src="simulation.js"></script>', f'<script>{sjs}</script>')
    html = html.replace('<script src="app.js"></script>', f'<script>{ajs}</script>')
    
    with open('frontend/bundled.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    bundle_frontend()
