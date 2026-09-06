import re

with open('accu_frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update applyOverridesToRow to include Load Shedding
new_apply = """function applyOverridesToRow(baseRow, simSOC) {
    let row = { ...baseRow };
    
    // 1. Weather Inputs Patching
    if (overrides.day) {
        row.irradiance = Math.max(600, row.irradiance + 500); 
        row.temperature = Math.max(-10, row.temperature);
    } 
    else if (overrides.night) {
        row.irradiance = 0; 
    } 
    else if (overrides.storm) {
        row.wind_speed = Math.max(26.0, row.wind_speed + 15.0); 
        row.irradiance = Math.min(50, row.irradiance); 
    } 
    else if (overrides.cold) {
        row.temperature = Math.min(-35.0, row.temperature - 20.0); 
    }
    else if (overrides.normal) {
        if (row.wind_speed > 20) row.wind_speed = 15; 
        if (row.temperature < -20) row.temperature = -10; 
    }

    // 2. Base Load Calculation
    let baseLoad = row.load_kw;
    if (overrides.cold) baseLoad += 40.0;
    
    // LOAD SHEDDING LOGIC (Critical vs Non-Critical)
    let load_crit = baseLoad * 0.45; // 45% Life support/comms
    let load_non = baseLoad * 0.55;  // 55% Comfort/Science
    let shedding = false;
    
    // Determine risk
    let sim_soc = simSOC !== undefined ? simSOC : row.lp_soc;
    if (overrides.storm || overrides.cold || sim_soc < 0.35) {
        shedding = true;
        load_non = 0; // Cut non-critical loads
    }
    
    row.load_critical = load_crit;
    row.load_non_critical = load_non;
    row.shedding_active = shedding;
    row.load_kw = load_crit + load_non; // Actual applied load

    // 3. Solar Gen
    row.lp_solar = row.irradiance * 0.018;

    // 4. Wind Gen
    if (row.wind_speed < 3.0 || row.wind_speed > 25.0) {
        row.lp_wind = 0;
    } else if (row.wind_speed >= 12.0) {
        row.lp_wind = 50.0;
    } else {
        row.lp_wind = Math.pow(row.wind_speed / 12.0, 3) * 50.0;
    }

    // 5. Dynamic Re-balancing
    let ren_total = row.lp_solar + row.lp_wind;
    let deficit = row.load_kw - ren_total;
    
    if (deficit > 0) {
        let available_batt_kw = (sim_soc - 0.2) * 500; 
        if (available_batt_kw > deficit) {
            row.lp_battery = deficit;
            row.lp_diesel = 0;
        } else {
            row.lp_battery = Math.max(0, available_batt_kw);
            row.lp_diesel = deficit - row.lp_battery;
        }
    } else {
        row.lp_diesel = 0;
        let space_batt_kw = (1.0 - sim_soc) * 500;
        let charging_amount = Math.min(Math.abs(deficit), space_batt_kw);
        row.lp_battery = -charging_amount; 
    }
    
    row.wind_avail = row.lp_wind;
    row.solar_avail = row.lp_solar;
    
    return row;
}"""

js = re.sub(r'function applyOverridesToRow\(baseRow, simSOC\).*?return row;\n}', new_apply, js, flags=re.DOTALL)


# 2. Update tick() for Risk, Load Shedding, and Flow Diagram
tick_start = "    // Hero Cards\n    updateVal('val-temp', row.temperature, 1);"

tick_addition = """    
    // RISK SCORE CALCULATION
    let risk = 10;
    if (row.wind_speed > 20) risk += (row.wind_speed - 20) * 4;
    if (row.wind_speed > 25) risk += 30; // Cutoff spike
    if (row.temperature < -15) risk += Math.abs(row.temperature + 15) * 1.5;
    if (row.lp_soc < 0.4) risk += (0.4 - row.lp_soc) * 150;
    risk = Math.min(100, Math.max(0, risk));
    updateVal('val-risk', risk, 0);
    const riskEl = document.getElementById('val-risk');
    if (riskEl) {
        riskEl.parentElement.parentElement.style.borderColor = risk > 70 ? 'var(--color-alert)' : (risk > 40 ? 'orange' : 'var(--color-battery)');
        riskEl.style.color = risk > 70 ? 'var(--color-alert)' : (risk > 40 ? 'orange' : 'var(--color-battery)');
    }

    // LOAD SHEDDING UI
    updateVal('list-load-crit', row.load_critical, 0);
    updateVal('list-load-non', row.load_non_critical, 0);
    const shedAlert = document.getElementById('shedding-alert');
    if (shedAlert) {
        shedAlert.style.display = row.shedding_active ? 'block' : 'none';
    }

    // ANIMATED FLOW DIAGRAM
    updateVal('flow-val-solar', row.lp_solar, 0);
    updateVal('flow-val-wind', row.lp_wind, 0);
    updateVal('flow-val-diesel', row.lp_diesel, 0);
    updateVal('flow-val-batt', row.lp_soc * 100, 0);
    updateVal('flow-val-crit', row.load_critical, 0);
    updateVal('flow-val-non', row.load_non_critical, 0);

    const toggleClass = (id, cls, condition) => {
        const el = document.getElementById(id);
        if (el) condition ? el.classList.add(cls) : el.classList.remove(cls);
    };

    toggleClass('node-solar', 'active-solar', row.lp_solar > 0);
    toggleClass('node-wind', 'active-wind', row.lp_wind > 0);
    toggleClass('node-diesel', 'active-diesel', row.lp_diesel > 0);
    toggleClass('node-battery', 'active-battery', row.lp_battery < 0); // charging
    toggleClass('node-noncrit', 'shedding', row.shedding_active);

    const wireGen = document.getElementById('wire-gen');
    if (wireGen) {
        wireGen.className = 'wire-animated';
        if (row.lp_diesel > 0) wireGen.classList.add('flowing-diesel');
        else if (row.lp_solar > 0 || row.lp_wind > 0) wireGen.classList.add('flowing-ren');
    }

    const wireLoad = document.getElementById('wire-load');
    if (wireLoad) {
        wireLoad.className = 'wire-animated';
        if (row.lp_diesel > 0 && row.lp_battery >= 0) wireLoad.classList.add('flowing-diesel'); // Diesel discharging to load
        else wireLoad.classList.add('flowing-ren'); // Renewables or Battery to load
    }
"""

js = js.replace(tick_start, tick_addition + '\n' + tick_start)

# 3. Clean up the old list-load UI code in tick()
js = js.replace("updateVal('list-load', row.load_kw, 0);", "")


with open('accu_frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("app.js patched successfully.")
