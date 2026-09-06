class PowerSimulation {
    constructor(buildings) {
        this.buildings = buildings;
        this.time = 0; // 0 to 24
        this.baseTemp = -30;
        
        this.state = {
            totalLoad: 0,
            solarGen: 0,
            windGen: 0,
            backupGen: 0,
            outsideTemp: -30,
            domeTemp: 7,
            buildings: {}
        };
        
        this.buildings.forEach(b => {
            this.state.buildings[b.id] = {
                currentPower: 0,
                loadPercent: 0,
                temperature: b.id === 'vcv_dome' ? 7 : (b.shape === 'box' ? 20 : -30),
                status: 'normal',
                history: Array(60).fill(0)
            };
        });
    }

    tick(dt) {
        this.time += dt * 0.5; 
        if (this.time >= 24) this.time -= 24;

        // Environment
        const timeRad = (this.time / 24) * Math.PI * 2;
        this.state.outsideTemp = this.baseTemp + Math.sin(timeRad - Math.PI/2) * 10;
        
        // VCV Dome specific temp (4 to 11 degrees)
        this.state.domeTemp = 7.5 + Math.sin(timeRad - Math.PI/2) * 3.5;

        // Generation
        // Solar (peak at noon)
        const solarFactor = Math.max(0, Math.sin(timeRad - Math.PI/2));
        this.state.solarGen = 200 + solarFactor * 800;
        
        // Wind (random gusts + baseline)
        const windBase = 200 + Math.sin(timeRad * 3) * 100;
        const windGust = Math.random() > 0.8 ? Math.random() * 200 : 0;
        this.state.windGen = windBase + windGust;

        let totalLoad = 0;

        // Building loads
        this.buildings.forEach(b => {
            const bState = this.state.buildings[b.id];
            
            if (b.basePower > 0) { // Consumer
                // Time of day usage pattern
                let timeMult = 1.0;
                if (b.category === 'living') {
                    // Morning and evening peaks
                    const morning = Math.max(0, Math.sin((this.time - 6) * Math.PI / 6));
                    const evening = Math.max(0, Math.sin((this.time - 18) * Math.PI / 6));
                    timeMult = 0.5 + (morning + evening) * 0.5;
                } else if (b.category === 'science' || b.category === 'technical') {
                    // Daytime peak
                    timeMult = 0.8 + Math.max(0, Math.sin((this.time - 8) * Math.PI / 12)) * 0.4;
                }
                
                // Heating load (colder = more power)
                let heatMult = 1.0;
                if (b.id === 'vcv_dome') {
                    const tempDiff = 11 - this.state.outsideTemp;
                    heatMult = 1.0 + (tempDiff / 50);
                } else if (b.shape === 'box') {
                    // Inside the dome, heating load is lower!
                    // Assuming most boxes are in the dome
                    const tempDiff = 20 - this.state.domeTemp;
                    heatMult = 1.0 + (tempDiff / 40);
                }

                // Random fluctuation
                const noise = 0.95 + Math.random() * 0.1;
                
                const power = b.basePower * timeMult * heatMult * noise;
                bState.currentPower = power;
                bState.loadPercent = (power / (b.basePower * 1.5)) * 100;
                totalLoad += power;
                
                // Temperatures
                if (b.id === 'vcv_dome') {
                    bState.temperature = this.state.domeTemp;
                } else if (b.shape === 'box') {
                    bState.temperature = 20 + Math.random() * 1.5;
                }

            } else { // Producer (Ring)
                bState.currentPower = -(this.state.solarGen + this.state.windGen);
                bState.loadPercent = Math.min(100, (Math.abs(bState.currentPower) / 1500) * 100);
            }

            // Update history
            bState.history.push(Math.abs(bState.currentPower));
            bState.history.shift();

            // Status
            if (bState.loadPercent > 90) bState.status = 'critical';
            else if (bState.loadPercent > 75) bState.status = 'warning';
            else bState.status = 'normal';
        });

        this.state.totalLoad = totalLoad;

        // Backup generator fills the gap if needed
        const totalGen = this.state.solarGen + this.state.windGen;
        if (totalLoad > totalGen) {
            this.state.backupGen = totalLoad - totalGen;
        } else {
            this.state.backupGen = 0;
        }
    }

    getState(id) {
        return id ? this.state.buildings[id] : this.state;
    }
}
