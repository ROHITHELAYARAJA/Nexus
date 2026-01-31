/**
 * Nexus Background Neural Effects
 * Optimized for V2.0 Red Command aesthetic
 */

class BackgroundEffects {
    constructor(canvasId = 'neural-canvas') {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.warn(`Canvas #${canvasId} not found, creating one.`);
            this.canvas = document.createElement('canvas');
            this.canvas.id = canvasId;
            document.body.prepend(this.canvas);
        }

        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: -100, y: -100 };
        this.enabled = true;

        this.init();
        this.animate();

        window.addEventListener('resize', () => this.resize());
        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    init() {
        this.resize();
        this.particles = [];
        const count = Math.floor((this.canvas.width * this.canvas.height) / 25000);

        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.4,
                size: Math.random() * 2 + 0.5
            });
        }
    }

    animate() {
        if (!this.enabled) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and Draw
        this.particles.forEach((p, i) => {
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;

            // Draw Node
            this.ctx.fillStyle = 'rgba(248, 81, 73, 0.4)';
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fill();

            // Connections
            for (let j = i + 1; j < this.particles.length; j++) {
                const p2 = this.particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 150) {
                    this.ctx.strokeStyle = `rgba(248, 81, 73, ${0.1 * (1 - dist / 150)})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.beginPath();
                    this.ctx.moveTo(p.x, p.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.stroke();
                }
            }

            // Mouse Proximity
            const mdx = this.mouse.x - p.x;
            const mdy = this.mouse.y - p.y;
            const mdist = Math.sqrt(mdx * mdx + mdy * mdy);
            if (mdist < 100) {
                this.ctx.strokeStyle = `rgba(88, 166, 255, ${0.3 * (1 - mdist / 100)})`;
                this.ctx.beginPath();
                this.ctx.moveTo(p.x, p.y);
                this.ctx.lineTo(this.mouse.x, this.mouse.y);
                this.ctx.stroke();
            }
        });

        requestAnimationFrame(() => this.animate());
    }

    toggle(state) {
        this.enabled = state;
        if (state) this.animate();
    }
}

// Singleton
document.addEventListener('DOMContentLoaded', () => {
    window.backgroundEffects = new BackgroundEffects();
});
