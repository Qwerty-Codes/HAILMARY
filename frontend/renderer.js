// Canvas roundRect polyfill for older browsers
if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
        if (w < 2 * r) r = w / 2;
        if (h < 2 * r) r = h / 2;
        this.beginPath();
        this.moveTo(x + r, y);
        this.arcTo(x + w, y, x + w, y + h, r);
        this.arcTo(x + w, y + h, x, y + h, r);
        this.arcTo(x, y + h, x, y, r);
        this.arcTo(x, y, x + w, y, r);
        this.closePath();
        return this;
    };
}

class IsometricRenderer {
    constructor(canvas, gridSize) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d', { alpha: false }); // Optimize for no transparency on base
        this.gridSize = gridSize;
        this.offsetX = canvas.width / 2;
        this.offsetY = canvas.height / 2;
    }

    resize(width, height, offsetX, offsetY) {
        this.canvas.width = width;
        this.canvas.height = height;
        this.offsetX = offsetX;
        this.offsetY = offsetY;
    }

    gridToScreen(gx, gy, gz = 0) {
        const sx = (gx - gy) * this.gridSize;
        const sy = (gx + gy) * (this.gridSize / 2) - (gz * this.gridSize);
        return { x: this.offsetX + sx, y: this.offsetY + sy };
    }

    clear() {
        this.ctx.fillStyle = '#0f172a'; // Dark slate
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    drawGround() {
        // Grid pattern
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        for (let i = -30; i <= 30; i++) {
            const p1 = this.gridToScreen(i, -30);
            const p2 = this.gridToScreen(i, 30);
            this.ctx.moveTo(p1.x, p1.y);
            this.ctx.lineTo(p2.x, p2.y);
            
            const p3 = this.gridToScreen(-30, i);
            const p4 = this.gridToScreen(30, i);
            this.ctx.moveTo(p3.x, p3.y);
            this.ctx.lineTo(p4.x, p4.y);
        }
        this.ctx.stroke();
    }

    drawRoads(roads) {
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        roads.forEach(road => {
            const p1 = this.gridToScreen(road.x, road.y);
            const p2 = this.gridToScreen(road.x + road.w, road.y);
            const p3 = this.gridToScreen(road.x + road.w, road.y + road.h);
            const p4 = this.gridToScreen(road.x, road.y + road.h);
            
            this.ctx.beginPath();
            this.ctx.moveTo(p1.x, p1.y);
            this.ctx.lineTo(p2.x, p2.y);
            this.ctx.lineTo(p3.x, p3.y);
            this.ctx.lineTo(p4.x, p4.y);
            this.ctx.closePath();
            this.ctx.fill();
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            this.ctx.stroke();
        });
    }

    drawPowerLines(lines, showPower, time) {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.lineWidth = 2;
        
        lines.forEach(line => {
            const p1 = this.gridToScreen(line.x1, line.y1);
            const p2 = this.gridToScreen(line.x2, line.y2);
            
            this.ctx.beginPath();
            this.ctx.moveTo(p1.x, p1.y);
            this.ctx.lineTo(p2.x, p2.y);
            this.ctx.stroke();
            
            if (showPower) {
                const dashOffset = -time * 50;
                this.ctx.save();
                this.ctx.strokeStyle = '#fff';
                this.ctx.lineWidth = 2;
                this.ctx.setLineDash([5, 10]);
                this.ctx.lineDashOffset = dashOffset;
                this.ctx.beginPath();
                this.ctx.moveTo(p1.x, p1.y);
                this.ctx.lineTo(p2.x, p2.y);
                this.ctx.stroke();
                this.ctx.restore();
            }
        });
    }

    drawBuilding(b, isHovered, status) {
        if (b.shape === 'box') {
            this.drawBoxBuilding(b, isHovered, status);
        } else if (b.shape === 'ring') {
            this.drawRing(b, isHovered, status);
        } else if (b.shape === 'circle') {
            this.drawCircle(b, isHovered, status);
        } else if (b.shape === 'dome') {
            this.drawDome(b, isHovered, status);
        }
    }

    drawBoxBuilding(b, isHovered, status) {
        const h = b.h_z || 1;
        const p1 = this.gridToScreen(b.x, b.y, b.z);
        const p2 = this.gridToScreen(b.x + b.w, b.y, b.z);
        const p3 = this.gridToScreen(b.x + b.w, b.y + b.h, b.z);
        const p4 = this.gridToScreen(b.x, b.y + b.h, b.z);
        
        const top1 = this.gridToScreen(b.x, b.y, b.z + h);
        const top2 = this.gridToScreen(b.x + b.w, b.y, b.z + h);
        const top3 = this.gridToScreen(b.x + b.w, b.y + b.h, b.z + h);
        const top4 = this.gridToScreen(b.x, b.y + b.h, b.z + h);

        const fillTop = isHovered ? '#ffffff' : '#e2e8f0';
        const fillLeft = isHovered ? '#cbd5e1' : '#94a3b8';
        const fillRight = isHovered ? '#94a3b8' : '#64748b';
        const strokeColor = '#334155';

        // Right face
        this.ctx.fillStyle = fillRight;
        this.ctx.beginPath();
        this.ctx.moveTo(p2.x, p2.y);
        this.ctx.lineTo(p3.x, p3.y);
        this.ctx.lineTo(top3.x, top3.y);
        this.ctx.lineTo(top2.x, top2.y);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.stroke();

        // Left face
        this.ctx.fillStyle = fillLeft;
        this.ctx.beginPath();
        this.ctx.moveTo(p3.x, p3.y);
        this.ctx.lineTo(p4.x, p4.y);
        this.ctx.lineTo(top4.x, top4.y);
        this.ctx.lineTo(top3.x, top3.y);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.stroke();

        // Top face
        this.ctx.fillStyle = fillTop;
        this.ctx.beginPath();
        this.ctx.moveTo(top1.x, top1.y);
        this.ctx.lineTo(top2.x, top2.y);
        this.ctx.lineTo(top3.x, top3.y);
        this.ctx.lineTo(top4.x, top4.y);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.stroke();
    }

    drawRing(b, isHovered, status) {
        const center = this.gridToScreen(b.cx, b.cy, b.z);
        const topCenter = this.gridToScreen(b.cx, b.cy, b.z + b.h_z);
        const rx = b.radius * this.gridSize;
        const ry = b.radius * (this.gridSize / 2);
        
        const in_rx = (b.radius - 1) * this.gridSize;
        const in_ry = (b.radius - 1) * (this.gridSize / 2);

        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 1;
        
        // Base outer
        this.ctx.beginPath();
        this.ctx.ellipse(center.x, center.y, rx, ry, 0, 0, 2 * Math.PI);
        this.ctx.stroke();
        
        // Base inner
        this.ctx.beginPath();
        this.ctx.ellipse(center.x, center.y, in_rx, in_ry, 0, 0, 2 * Math.PI);
        this.ctx.stroke();

        // Top outer
        this.ctx.fillStyle = isHovered ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.1)';
        this.ctx.beginPath();
        this.ctx.ellipse(topCenter.x, topCenter.y, rx, ry, 0, 0, 2 * Math.PI);
        this.ctx.stroke();

        // Top inner
        this.ctx.beginPath();
        this.ctx.ellipse(topCenter.x, topCenter.y, in_rx, in_ry, 0, 0, 2 * Math.PI);
        this.ctx.stroke();

        // Draw panels
        for(let i=0; i<32; i++) {
            const angle = (i/32) * Math.PI * 2;
            const x = topCenter.x + Math.cos(angle) * rx;
            const y = topCenter.y + Math.sin(angle) * ry;
            const in_x = topCenter.x + Math.cos(angle) * in_rx;
            const in_y = topCenter.y + Math.sin(angle) * in_ry;
            this.ctx.beginPath();
            this.ctx.moveTo(x, y);
            this.ctx.lineTo(in_x, in_y);
            this.ctx.stroke();
        }
    }

    drawCircle(b, isHovered, status) {
        const center = this.gridToScreen(b.cx, b.cy, b.z);
        const rx = b.radius * this.gridSize;
        const ry = b.radius * (this.gridSize / 2);
        
        this.ctx.fillStyle = isHovered ? '#94a3b8' : '#475569';
        this.ctx.strokeStyle = '#fff';
        this.ctx.beginPath();
        this.ctx.ellipse(center.x, center.y, rx, ry, 0, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.stroke();
        
        // Inner circle
        this.ctx.beginPath();
        this.ctx.ellipse(center.x, center.y, rx*0.5, ry*0.5, 0, 0, 2 * Math.PI);
        this.ctx.stroke();
    }

    drawDome(b, isHovered, status) {
        const center = this.gridToScreen(b.cx, b.cy, b.z);
        const rx = b.radius * this.gridSize;
        const ry = b.radius * (this.gridSize / 2);
        
        // Base
        this.ctx.strokeStyle = 'rgba(255,255,255,0.3)';
        this.ctx.beginPath();
        this.ctx.ellipse(center.x, center.y, rx, ry, 0, 0, 2 * Math.PI);
        this.ctx.stroke();
        
        // Wireframe dome
        this.ctx.strokeStyle = isHovered ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.2)';
        this.ctx.lineWidth = 1;
        
        const h_px = b.h_z * this.gridSize;
        
        // Arcs
        for(let i=0; i<8; i++) {
            const angle = (i/8) * Math.PI;
            this.ctx.beginPath();
            for(let t=0; t<=Math.PI; t+=0.1) {
                const px = center.x + Math.cos(angle) * rx * Math.cos(t);
                const py = center.y + Math.sin(angle) * ry * Math.cos(t) - Math.sin(t) * h_px;
                if(t===0) this.ctx.moveTo(px, py);
                else this.ctx.lineTo(px, py);
            }
            this.ctx.stroke();
        }
        
        // Horizontal rings
        for(let j=1; j<4; j++) {
            const h_factor = Math.sin(j/4 * Math.PI/2);
            const r_factor = Math.cos(j/4 * Math.PI/2);
            const r_x = rx * r_factor;
            const r_y = ry * r_factor;
            const c_y = center.y - h_factor * h_px;
            
            this.ctx.beginPath();
            this.ctx.ellipse(center.x, c_y, r_x, r_y, 0, 0, 2 * Math.PI);
            this.ctx.stroke();
        }
    }

    drawPowerLabel(b, powerText) {
        let top;
        if (b.shape === 'box') {
            top = this.gridToScreen(b.x + b.w/2, b.y + b.h/2, b.z + (b.h_z || 1));
        } else {
            top = this.gridToScreen(b.cx, b.cy, b.z + (b.h_z || 1));
            if (b.shape === 'dome') top.y -= b.h_z * this.gridSize * 0.5;
        }

        const px = top.x;
        const py = top.y - 15;

        this.ctx.font = 'bold 10px "JetBrains Mono", monospace';
        const txtWidth = this.ctx.measureText(powerText).width;
        const padX = 6;
        const padY = 4;
        
        this.ctx.fillStyle = 'rgba(0,0,0,0.8)';
        this.ctx.strokeStyle = '#64748b';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.roundRect(px - txtWidth/2 - padX, py - 10 - padY, txtWidth + padX*2, 10 + padY*2, 4);
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.fillStyle = '#ffffff';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(powerText, px, py - 5);
    }

    drawSnow(snowflakes) {
        this.ctx.fillStyle = '#ffffff';
        snowflakes.forEach(flake => {
            this.ctx.globalAlpha = flake.a;
            this.ctx.beginPath();
            this.ctx.arc(flake.x, flake.y, flake.r, 0, Math.PI * 2);
            this.ctx.fill();
        });
        this.ctx.globalAlpha = 1.0;
    }

    hitTest(x, y, buildings) {
        let hit = null;
        let maxZ = -Infinity;
        
        for (const b of buildings) {
            let pts = [];
            if (b.shape === 'box') {
                const h = b.h_z || 1;
                // Just use the top face for hit testing roughly
                pts = [
                    this.gridToScreen(b.x, b.y, b.z + h),
                    this.gridToScreen(b.x + b.w, b.y, b.z + h),
                    this.gridToScreen(b.x + b.w, b.y + b.h, b.z + h),
                    this.gridToScreen(b.x, b.y + b.h, b.z + h)
                ];
            } else if (b.shape === 'ring' || b.shape === 'circle' || b.shape === 'dome') {
                const c = this.gridToScreen(b.cx, b.cy, b.z);
                const rx = b.radius * this.gridSize;
                const ry = b.radius * (this.gridSize / 2);
                const dx = (x - c.x) / rx;
                const dy = (y - c.y) / ry;
                if (dx*dx + dy*dy <= 1) {
                    if (b.z > maxZ) { maxZ = b.z; hit = b; }
                }
                continue;
            }

            if (pts.length > 0 && this.pointInPolygon(x, y, pts)) {
                if (b.z > maxZ) {
                    maxZ = b.z;
                    hit = b;
                }
            }
        }
        return hit;
    }

    pointInPolygon(x, y, vs) {
        let inside = false;
        for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
            const xi = vs[i].x, yi = vs[i].y;
            const xj = vs[j].x, yj = vs[j].y;
            const intersect = ((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
            if (intersect) inside = !inside;
        }
        return inside;
    }
}
