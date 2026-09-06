/**
 * app.js — Main application entry point
 * Wires together the renderer, simulation, HUD, controls,
 * pan/zoom interactions, tooltips, and bottom panel.
 */

(function () {
    'use strict';

    // ─── INIT ───
    const canvas = document.getElementById('stationCanvas');
    const container = document.getElementById('canvasContainer');
    const renderer = new IsometricRenderer(canvas, 30);
    const simulation = new PowerSimulation(BUILDINGS);

    function resizeCanvas() {
        const rect = container.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
            renderer.resize(rect.width, rect.height, rect.width / 2, rect.height / 2);
        }
    }
    window.addEventListener('resize', resizeCanvas);
    setInterval(resizeCanvas, 500); // Failsafe for iframes
    resizeCanvas();

    // Center view
    renderer.offsetX = canvas.width / 2;
    renderer.offsetY = canvas.height / 2 + 50;
    
    // ─── PAN & ZOOM ───
    let isDragging = false;
    let dragStartX, dragStartY;
    let lastOffsetX, lastOffsetY;

    container.addEventListener('mousedown', e => {
        isDragging = true;
        dragStartX = e.clientX;
        dragStartY = e.clientY;
        lastOffsetX = renderer.offsetX;
        lastOffsetY = renderer.offsetY;
        container.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', e => {
        if (isDragging) {
            renderer.offsetX = lastOffsetX + (e.clientX - dragStartX);
            renderer.offsetY = lastOffsetY + (e.clientY - dragStartY);
        }

        // Hit test for hover
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        
        // Convert screen to isometric grid conceptually for hit test
        // Let hitTest handle screen coordinates by giving it mx, my
        const hit = renderer.hitTest(mx, my, BUILDINGS);
        renderer.hoveredBuilding = hit;
        container.style.cursor = isDragging ? 'grabbing' : (hit ? 'pointer' : 'grab');

        // Tooltip
        updateTooltip(hit, e.clientX, e.clientY);
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
        container.style.cursor = 'grab';
    });

    // Zoom with scroll
    container.addEventListener('wheel', e => {
        e.preventDefault();
        const zoomDelta = e.deltaY > 0 ? 0.9 : 1.1;
        const newGridSize = Math.max(10, Math.min(60, renderer.gridSize * zoomDelta));

        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        // Keep mouse at same world position
        const relX = mx - renderer.offsetX;
        const relY = my - renderer.offsetY;
        
        const scale = newGridSize / renderer.gridSize;
        
        renderer.offsetX = mx - (relX * scale);
        renderer.offsetY = my - (relY * scale);
        renderer.gridSize = newGridSize;
    }, { passive: false });

    // ─── CONTROLS ───
    document.getElementById('zoomIn').addEventListener('click', () => {
        renderer.gridSize = Math.min(60, renderer.gridSize * 1.2);
    });
    document.getElementById('zoomOut').addEventListener('click', () => {
        renderer.gridSize = Math.max(10, renderer.gridSize / 1.2);
    });
    document.getElementById('resetView').addEventListener('click', () => {
        resizeCanvas();
        renderer.offsetX = canvas.width / 2;
        renderer.offsetY = canvas.height / 2 + 50;
        renderer.gridSize = 30;
    });

    let showLabels = true;
    let showPower = true;
    let showSnow = true;
    const snowflakes = Array.from({length: 100}, () => ({
        x: Math.random() * 2000 - 1000,
        y: Math.random() * 1000 - 500,
        z: Math.random() * 10,
        r: Math.random() * 1.5 + 0.5,
        speed: Math.random() * 0.5 + 0.5,
        a: Math.random() * 0.5 + 0.1
    }));

    document.getElementById('toggleLabels').classList.add('active');
    document.getElementById('togglePower').classList.add('active');
    document.getElementById('toggleSnow').classList.add('active');

    document.getElementById('toggleLabels').addEventListener('click', (e) => {
        showLabels = !showLabels;
        e.target.classList.toggle('active');
    });
    document.getElementById('togglePower').addEventListener('click', (e) => {
        showPower = !showPower;
        e.target.classList.toggle('active');
    });
    document.getElementById('toggleSnow').addEventListener('click', (e) => {
        showSnow = !showSnow;
        e.target.classList.toggle('active');
    });

    // ─── BOTTOM PANEL ───
    const bottomPanel = document.getElementById('bottomPanel');
    const panelToggle = document.getElementById('panelToggle');

    panelToggle.addEventListener('click', () => {
        bottomPanel.classList.toggle('collapsed');
        panelToggle.querySelector('span').textContent =
            bottomPanel.classList.contains('collapsed')
                ? '▲ Power Grid Overview'
                : '▼ Power Grid Overview';
    });

    // Build power cards
    function buildPowerCards() {
        const grid = document.getElementById('powerGrid');
        grid.innerHTML = '';
        BUILDINGS.forEach(b => {
            const card = document.createElement('div');
            card.className = 'power-card';
            card.id = `card-${b.id}`;
            card.innerHTML = `
                <div class="card-name">${b.icon} ${b.name}</div>
                <div class="card-power">-- kW</div>
                <div class="card-bar-bg"><div class="card-bar" style="width:0%"></div></div>
                <div class="card-detail">Load: --% | ${b.basePower < 0 ? 'Generator' : 'Consumer'}</div>
            `;
            card.addEventListener('click', () => {
                const pos = renderer.gridToScreen(b.cx !== undefined ? b.cx : b.x + b.w/2, b.cy !== undefined ? b.cy : b.y + b.h/2);
                renderer.offsetX += canvas.width / 2 - pos.x;
                renderer.offsetY += canvas.height / 2 - pos.y;
            });
            grid.appendChild(card);
        });
    }
    buildPowerCards();

    function updatePowerCards() {
        BUILDINGS.forEach(b => {
            const state = simulation.getState(b.id);
            const card = document.getElementById(`card-${b.id}`);
            if (!card || !state) return;

            const powerEl = card.querySelector('.card-power');
            const barEl = card.querySelector('.card-bar');
            const detailEl = card.querySelector('.card-detail');

            const isGen = b.basePower < 0;
            powerEl.textContent = `${isGen ? '▲' : ''} ${Math.abs(state.currentPower).toFixed(1)} kW`;
            barEl.style.width = `${Math.min(100, state.loadPercent)}%`;
            detailEl.textContent = `Load: ${state.loadPercent.toFixed(0)}% | ${state.temperature.toFixed(1)}°C inside`;
        });
    }

    // ─── TOOLTIP ───
    const tooltip = document.getElementById('tooltip');
    const tooltipHeader = document.getElementById('tooltipHeader');
    const tooltipBody = document.getElementById('tooltipBody');

    function updateTooltip(building, mx, my) {
        if (!building) {
            tooltip.style.display = 'none';
            return;
        }

        const state = simulation.getState(building.id);

        tooltipHeader.innerHTML = `${building.icon} ${building.name}`;

        // Build sparkline SVG from history
        const history = state.history || [];
        let sparkline = '';
        if (history.length > 5) {
            const maxH = Math.max(...history, 1);
            const minH = Math.min(...history);
            const svgW = 200, svgH = 30;
            const pts = history.map((v, i) => {
                const x = (i / (history.length - 1)) * svgW;
                const y = svgH - ((v - minH) / (maxH - minH + 0.01)) * svgH;
                return `${x},${y}`;
            }).join(' ');
            sparkline = `<div style="margin-top:8px">
                <div style="font-size:9px;color:#666;margin-bottom:2px">POWER HISTORY (60s)</div>
                <svg width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}">
                    <polyline points="${pts}" fill="none" stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/>
                    <polyline points="0,${svgH} ${pts} ${svgW},${svgH}" fill="url(#sparkGrad-${building.id})" stroke="none" opacity="0.15"/>
                    <defs><linearGradient id="sparkGrad-${building.id}" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#fff"/>
                        <stop offset="100%" stop-color="transparent"/>
                    </linearGradient></defs>
                </svg>
            </div>`;
        }

        tooltipBody.innerHTML = `
            <div class="tooltip-row">
                <span>Category</span>
                <span class="tooltip-value">${BUILDING_CATEGORIES[building.category].label}</span>
            </div>
            <div class="tooltip-row">
                <span>Power</span>
                <span class="tooltip-value">${Math.abs(state.currentPower).toFixed(1)} kW</span>
            </div>
            <div class="tooltip-row">
                <span>Load</span>
                <span class="tooltip-value">${state.loadPercent.toFixed(0)}%</span>
            </div>
            <div class="tooltip-row">
                <span>Inside Temp</span>
                <span class="tooltip-value">${state.temperature.toFixed(1)}°C</span>
            </div>
            <div class="tooltip-row">
                <span>Status</span>
                <span class="tooltip-value">${state.status.toUpperCase()}</span>
            </div>
            ${sparkline}
            <div style="margin-top:8px;font-size:10px;color:#666">${building.description}</div>
        `;

        // Position tooltip
        const rect = container.getBoundingClientRect();
        let tx = mx - rect.left + 16;
        let ty = my - rect.top - 20;

        // Keep on screen
        if (tx + 260 > rect.width) tx = mx - rect.left - 270;
        if (ty + 200 > rect.height) ty = rect.height - 210;
        if (ty < 10) ty = 10;

        tooltip.style.display = 'block';
        tooltip.style.left = tx + 'px';
        tooltip.style.top = ty + 'px';
    }

    // ─── HUD UPDATES ───
    function updateHUD() {
        const s = simulation.getState();
        document.getElementById('totalLoad').textContent = `${s.totalLoad.toFixed(0)} kW`;
        document.getElementById('solarPower').textContent = `${s.solarGen.toFixed(0)} kW`;
        document.getElementById('windPower').textContent = `${s.windGen.toFixed(0)} kW`;
        document.getElementById('dieselPower').textContent = `${s.backupGen.toFixed(0)} kW`;
        document.getElementById('outsideTemp').textContent = `${s.outsideTemp.toFixed(1)}°C`;
        document.getElementById('domeTemp').textContent = `${s.domeTemp.toFixed(1)}°C`;

        // Time display
        const hours = Math.floor(simulation.time);
        const minutes = Math.floor((simulation.time % 1) * 60);
        const seconds = Math.floor(((simulation.time * 60) % 1) * 60);
        document.getElementById('timeDisplay').textContent =
            `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    // ─── RENDER LOOP ───
    let lastTime = null;
    let simTime = 0;

    function frame(timestamp) {
        if (lastTime === null) lastTime = timestamp;
        let dt = (timestamp - lastTime) / 1000;
        if (dt < 0 || dt > 1) dt = 0.016; // Safety clamp for iframe anomalies
        lastTime = timestamp;
        simTime += dt;

        // Simulation tick
        simulation.tick(dt);

        // Render
        renderer.clear();
        renderer.drawGround();
        renderer.drawRoads(ROADS);
        renderer.drawPowerLines(POWER_LINES, showPower, simTime);

        // Sort buildings by z to draw base then living then dome
        const sorted = [...BUILDINGS].sort((a, b) => a.z - b.z);
        sorted.forEach(b => {
            const state = simulation.getState(b.id);
            const isHovered = renderer.hoveredBuilding === b;
            renderer.drawBuilding(b, isHovered, state.status);
            if (showLabels) {
                renderer.drawPowerLabel(b, `${Math.abs(state.currentPower).toFixed(0)} kW`);
            }
        });

        if (showSnow) {
            snowflakes.forEach(f => {
                f.x -= f.speed * dt * 50;
                f.y += f.speed * dt * 20;
                const pos = renderer.gridToScreen(0,0,0); // use just screen offset conceptually
                let sx = pos.x + f.x;
                let sy = pos.y + f.y;
                if(sx < 0) f.x += canvas.width;
                if(sy > canvas.height) f.y -= canvas.height;
            });
            // Renderer doesn't know about screen space snowflakes directly, let's just pass the screen coords to it
            const snowToDraw = snowflakes.map(f => {
                const pos = renderer.gridToScreen(0,0,0);
                return {
                    x: (pos.x + f.x) % canvas.width,
                    y: (pos.y + f.y) % canvas.height,
                    r: f.r,
                    a: f.a
                };
            });
            // Fix modulo negative
            snowToDraw.forEach(s => {
                if(s.x < 0) s.x += canvas.width;
                if(s.y < 0) s.y += canvas.height;
            });
            renderer.drawSnow(snowToDraw);
        }

        // Update UI periodically
        if (Math.floor(timestamp / 200) !== Math.floor((timestamp - dt * 1000) / 200)) {
            updateHUD();
            updatePowerCards();
        }

        requestAnimationFrame(frame);
    }

    // ─── START ───
    requestAnimationFrame(frame);
    updateHUD();

})();
