/**
 * TRON Light Cycle Background Animation
 * 
 * Renders animated light cycles racing on a grid, leaving glowing trails,
 * with collision detection and explosion effects.
 */

class TronBackground {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.animationId = null;
        this.isRunning = false;
        
        // Grid settings
        this.gridSize = 25; // pixels per grid cell (larger = slower movement)
        this.gridColor = 'rgba(0, 200, 200, 0.01)';
        
        // Safe zone margins (pixels) - minimal now that cards are transparent
        this.marginTop = 5;
        this.marginBottom = 5;
        this.marginLeft = 5;
        this.marginRight = 5;
        
        // Light cycles
        this.cycles = [];
        this.trails = []; // Each trail is an array of {x, y} points
        
        // Explosion particles
        this.particles = [];
        
        // Target for race mode (user can click to set)
        this.target = null; // { x, y } in grid coords
        this.targetPulse = 0; // Animation pulse
        
        // Colors for the two cycles (will be updated from theme)
        this.colors = {
            cyan: { r: 0, g: 200, b: 200 },
            orange: { r: 255, g: 140, b: 0 }
        };
        
        // Score tracking
        this.scores = { cyan: 0, orange: 0 };
        this.lastWinner = null;
        this.showingWinner = false;
        this.winnerDisplayTime = 0;
        
        // Timing
        this.lastTime = 0;
        this.moveInterval = 80; // ms between moves (slower = less frantic)
        this.timeSinceMove = 0;
        
        // Bind methods
        this.animate = this.animate.bind(this);
        this.handleResize = this.handleResize.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.updateThemeColors = this.updateThemeColors.bind(this);
    }
    
    /**
     * Convert HSL to RGB
     */
    hslToRgb(h, s, l) {
        s /= 100;
        l /= 100;
        const a = s * Math.min(l, 1 - l);
        const f = n => {
            const k = (n + h / 30) % 12;
            return l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        };
        return {
            r: Math.round(f(0) * 255),
            g: Math.round(f(8) * 255),
            b: Math.round(f(4) * 255)
        };
    }
    
    /**
     * Update colors from CSS theme variables
     */
    updateThemeColors() {
        const style = getComputedStyle(document.documentElement);
        const accentH = parseInt(style.getPropertyValue('--accent-h').trim()) || 187;
        const secondaryH = parseInt(style.getPropertyValue('--secondary-h').trim()) || 25;
        const accentS = parseInt(style.getPropertyValue('--accent-s').trim()) || 92;
        const accentL = parseInt(style.getPropertyValue('--accent-l').trim()) || 50;
        
        // Update cycle colors from theme
        this.colors.cyan = this.hslToRgb(accentH, accentS, accentL);
        this.colors.orange = this.hslToRgb(secondaryH, 85, 55);
        
        // Update grid color to match theme
        const c = this.colors.cyan;
        this.gridColor = `rgba(${c.r}, ${c.g}, ${c.b}, 0.01)`;
    }
    
    /**
     * Initialize the canvas and start animation
     */
    init() {
        // Create canvas if it doesn't exist
        this.canvas = document.getElementById('tron-background');
        if (!this.canvas) {
            this.canvas = document.createElement('canvas');
            this.canvas.id = 'tron-background';
            this.canvas.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                pointer-events: none;
            `;
            document.body.insertBefore(this.canvas, document.body.firstChild);
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.handleResize();
        window.addEventListener('resize', this.handleResize);
        
        // Click/tap to set race target
        document.addEventListener('click', this.handleClick);
        document.addEventListener('touchstart', this.handleClick, { passive: true });
        
        // Listen for theme changes and update colors
        document.addEventListener('themechange', this.updateThemeColors);
        
        // Initial theme color sync
        this.updateThemeColors();
        
        this.resetGame();
    }
    
    /**
     * Handle click/tap to set race target
     */
    handleClick(event) {
        // Ignore if clicking on interactive elements
        const target = event.target;
        if (target.closest('button, a, input, select, textarea, .modal, .drawer, .header, .mobile-tabs')) {
            return;
        }
        
        // Only allow setting target if game is running, not showing winner, and no target exists
        if (!this.isRunning || this.showingWinner || this.target) return;
        
        // Get click position
        const clientX = event.touches ? event.touches[0].clientX : event.clientX;
        const clientY = event.touches ? event.touches[0].clientY : event.clientY;
        
        // Convert to grid coordinates
        const gridX = Math.floor(clientX / this.gridSize);
        const gridY = Math.floor(clientY / this.gridSize);
        
        // Check if within play bounds
        if (this.playBounds) {
            const { minX, maxX, minY, maxY } = this.playBounds;
            if (gridX >= minX && gridX <= maxX && gridY >= minY && gridY <= maxY) {
                // Check not on any trail
                let onTrail = false;
                for (const trail of this.trails) {
                    for (const point of trail) {
                        if (point.x === gridX && point.y === gridY) {
                            onTrail = true;
                            break;
                        }
                    }
                }
                
                if (!onTrail) {
                    this.target = { x: gridX, y: gridY };
                    this.targetPulse = 0;
                    
                    // Turn both cycles toward the target immediately
                    for (const cycle of this.cycles) {
                        const dx = gridX - cycle.x;
                        const dy = gridY - cycle.y;
                        
                        // Turn toward the larger axis difference
                        if (Math.abs(dx) > Math.abs(dy)) {
                            // Target is more horizontal
                            cycle.dx = dx > 0 ? 1 : -1;
                            cycle.dy = 0;
                        } else {
                            // Target is more vertical
                            cycle.dx = 0;
                            cycle.dy = dy > 0 ? 1 : -1;
                        }
                    }
                }
            }
        }
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    /**
     * Reset the game state
     */
    resetGame() {
        // Calculate safe play area (avoiding UI elements)
        const minX = Math.ceil(this.marginLeft / this.gridSize);
        const maxX = Math.floor((this.canvas.width - this.marginRight) / this.gridSize) - 1;
        const minY = Math.ceil(this.marginTop / this.gridSize);
        const maxY = Math.floor((this.canvas.height - this.marginBottom) / this.gridSize) - 1;
        
        const playW = maxX - minX;
        const playH = maxY - minY;
        const centerY = minY + Math.floor(playH / 2);
        
        // Create two light cycles at opposite sides within play area
        this.cycles = [
            {
                x: minX + Math.floor(playW * 0.15),
                y: centerY,
                dx: 1,
                dy: 0,
                color: this.colors.cyan,
                name: 'cyan'
            },
            {
                x: minX + Math.floor(playW * 0.85),
                y: centerY,
                dx: -1,
                dy: 0,
                color: this.colors.orange,
                name: 'orange'
            }
        ];
        
        // Store play boundaries for AI
        this.playBounds = { minX, maxX, minY, maxY };
        
        // Reset trails
        this.trails = [[], []];
        
        // Add starting positions to trails
        this.cycles.forEach((cycle, i) => {
            this.trails[i].push({ x: cycle.x, y: cycle.y });
        });
        
        // Clear particles
        this.particles = [];
    }
    
    /**
     * Start the animation
     */
    start() {
        if (this.isRunning) return;
        
        this.init();
        this.isRunning = true;
        this.lastTime = performance.now();
        this.animate();
    }
    
    /**
     * Stop the animation
     */
    stop() {
        this.isRunning = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        window.removeEventListener('resize', this.handleResize);
        
        // Clear the canvas
        if (this.ctx) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
        
        // Remove canvas
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
            this.canvas = null;
        }
    }
    
    /**
     * Main animation loop
     */
    animate(currentTime = performance.now()) {
        if (!this.isRunning) return;
        
        const deltaTime = currentTime - this.lastTime;
        this.lastTime = currentTime;
        
        this.timeSinceMove += deltaTime;
        
        // Move cycles at fixed interval
        if (this.timeSinceMove >= this.moveInterval) {
            this.timeSinceMove = 0;
            this.updateCycles();
        }
        
        // Update particles
        this.updateParticles(deltaTime);
        
        // Render
        this.render();
        
        this.animationId = requestAnimationFrame(this.animate);
    }
    
    /**
     * Update cycle positions and check for collisions
     */
    updateCycles() {
        const gridW = Math.floor(this.canvas.width / this.gridSize);
        const gridH = Math.floor(this.canvas.height / this.gridSize);
        const bounds = this.playBounds || { minX: 1, maxX: gridW - 2, minY: 1, maxY: gridH - 2 };
        
        // Check for collisions and move each cycle
        for (let i = 0; i < this.cycles.length; i++) {
            const cycle = this.cycles[i];
            
            // AI: Decide if we should turn
            this.aiDecide(cycle, i, gridW, gridH);
            
            // Move
            cycle.x += cycle.dx;
            cycle.y += cycle.dy;
            
            // Check collision with play area boundaries
            if (cycle.x < bounds.minX || cycle.x > bounds.maxX || 
                cycle.y < bounds.minY || cycle.y > bounds.maxY) {
                this.explode(cycle);
                return;
            }
            
            // Check collision with any trail
            for (let t = 0; t < this.trails.length; t++) {
                for (let p = 0; p < this.trails[t].length - 1; p++) {
                    const point = this.trails[t][p];
                    if (point.x === cycle.x && point.y === cycle.y) {
                        this.explode(cycle);
                        return;
                    }
                }
            }
            
            // Add position to trail
            this.trails[i].push({ x: cycle.x, y: cycle.y });
            
            // Check if cycle reached target (race mode)
            if (this.target && cycle.x === this.target.x && cycle.y === this.target.y) {
                // This cycle wins!
                this.scores[cycle.name]++;
                this.lastWinner = cycle.name;
                this.showingWinner = true;
                this.winnerDisplayTime = 1000;
                this.target = null; // Clear target
                
                // Brief celebration particles at target
                const px = cycle.x * this.gridSize + this.gridSize / 2;
                const py = cycle.y * this.gridSize + this.gridSize / 2;
                for (let p = 0; p < 15; p++) {
                    const angle = (Math.PI * 2 / 15) * p;
                    this.particles.push({
                        x: px, y: py,
                        vx: Math.cos(angle) * 3,
                        vy: Math.sin(angle) * 3,
                        life: 0.6,
                        color: cycle.color,
                        size: 4
                    });
                }
                
                // Reset after short delay
                setTimeout(() => {
                    if (this.isRunning) {
                        this.showingWinner = false;
                        this.resetGame();
                    }
                }, 1200);
                return;
            }
            
            // Limit trail length (shorter = cleaner look)
            const maxTrailLength = 120;
            if (this.trails[i].length > maxTrailLength) {
                this.trails[i].shift();
            }
        }
    }
    
    /**
     * Main AI decision making - implements all behavior objectives
     */
    aiDecide(cycle, index, gridW, gridH) {
        const opponent = this.cycles[1 - index];
        const bounds = this.playBounds || { minX: 1, maxX: gridW - 2, minY: 1, maxY: gridH - 2 };
        
        // Calculate distances for proximity-based decisions
        const distToOpponent = this.getDistance(cycle, opponent);
        const distToTarget = this.target ? this.getDistance(cycle, this.target) : Infinity;
        
        // ===== RACE MODE (Target Set) =====
        if (this.target) {
            // Check if about to die (2 cells ahead)
            if (this.willDieAhead(cycle, bounds, 2)) {
                this.turnTowardGoal(cycle, index, bounds, this.target);
                return;
            }
            
            // Get more focused as we approach target
            if (distToTarget <= 8) {
                // Close to target - stay on course unless forced to turn
                return;
            }
            
            // Occasionally adjust toward target (10% chance)
            if (Math.random() < 0.1) {
                const dx = this.target.x - cycle.x;
                const dy = this.target.y - cycle.y;
                // Only turn if we're not heading toward target at all
                const headingToward = (cycle.dx * dx + cycle.dy * dy) > 0;
                if (!headingToward) {
                    this.turnTowardGoal(cycle, index, bounds, this.target);
                }
            }
            return;
        }
        
        // ===== NORMAL MODE (No Target) =====
        
        // Priority 1: Don't die - check 3 cells ahead
        if (this.willDieAhead(cycle, bounds, 3)) {
            this.turnToSafestDirection(cycle, index, bounds);
            return;
        }
        
        // Calculate aggression based on proximity
        const isCloseToOpponent = distToOpponent <= 10;
        const aggressionChance = isCloseToOpponent ? 0.25 : 0.08;
        
        // Priority 2: Offensive moves when close to opponent
        if (isCloseToOpponent && Math.random() < aggressionChance) {
            this.tryToCutOff(cycle, opponent, index, bounds);
            return;
        }
        
        // Priority 3: Natural movement - 70% continue, 30% consider turn
        if (Math.random() < 0.70) {
            // Continue current direction if safe
            return;
        }
        
        // 30% of the time, consider a turn for variety
        if (Math.random() < 0.5) {
            // Random safe turn for natural wandering
            this.turnToSafestDirection(cycle, index, bounds);
        }
    }
    
    /**
     * Get Manhattan distance between two points
     */
    getDistance(a, b) {
        return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
    }
    
    /**
     * Check if cycle will die within N cells ahead
     */
    willDieAhead(cycle, bounds, distance) {
        for (let i = 1; i <= distance; i++) {
            const checkX = cycle.x + cycle.dx * i;
            const checkY = cycle.y + cycle.dy * i;
            
            // Wall collision
            if (checkX < bounds.minX || checkX > bounds.maxX || 
                checkY < bounds.minY || checkY > bounds.maxY) {
                return true;
            }
            
            // Trail collision
            for (const trail of this.trails) {
                for (const point of trail) {
                    if (point.x === checkX && point.y === checkY) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
    /**
     * Turn toward a goal point while avoiding obstacles
     */
    turnTowardGoal(cycle, index, bounds, goal) {
        const options = this.getValidTurnOptions(cycle, index, bounds);
        if (options.length === 0) return;
        
        const dx = goal.x - cycle.x;
        const dy = goal.y - cycle.y;
        
        // Score each option by alignment with goal direction
        let bestOption = options[0];
        let bestScore = -Infinity;
        
        for (const opt of options) {
            // Alignment score (dot product direction)
            let score = 0;
            if (dx !== 0) score += opt.dx * Math.sign(dx);
            if (dy !== 0) score += opt.dy * Math.sign(dy);
            
            // Bonus for continuing current direction (smooth paths)
            if (opt.dx === cycle.dx && opt.dy === cycle.dy) {
                score += 0.5;
            }
            
            if (score > bestScore) {
                bestScore = score;
                bestOption = opt;
            }
        }
        
        cycle.dx = bestOption.dx;
        cycle.dy = bestOption.dy;
    }
    
    /**
     * Check if continuing would hit own trail
     */
    wouldHitOwnTrail(cycle, trail, distance) {
        for (let i = 1; i <= distance; i++) {
            const checkX = cycle.x + cycle.dx * i;
            const checkY = cycle.y + cycle.dy * i;
            
            // Check own trail (skip last few points - too close)
            for (let j = 0; j < trail.length - 3; j++) {
                if (trail[j].x === checkX && trail[j].y === checkY) {
                    return true;
                }
            }
        }
        return false;
    }
    
    /**
     * Check how many cells ahead are blocked
     */
    getThreatsAhead(cycle, distance, bounds) {
        let blockedAt = -1;
        
        for (let i = 1; i <= distance; i++) {
            const checkX = cycle.x + cycle.dx * i;
            const checkY = cycle.y + cycle.dy * i;
            
            // Check play area boundaries
            if (checkX < bounds.minX || checkX > bounds.maxX || 
                checkY < bounds.minY || checkY > bounds.maxY) {
                blockedAt = i;
                break;
            }
            
            // Check trails
            for (const trail of this.trails) {
                for (const point of trail) {
                    if (point.x === checkX && point.y === checkY) {
                        blockedAt = i;
                        break;
                    }
                }
                if (blockedAt > 0) break;
            }
            if (blockedAt > 0) break;
        }
        
        return { blocked: blockedAt > 0, distance: blockedAt };
    }
    
    /**
     * Check if a specific position is safe
     */
    isPositionSafe(x, y, bounds) {
        // Check play area boundaries
        if (x < bounds.minX || x > bounds.maxX || 
            y < bounds.minY || y > bounds.maxY) {
            return false;
        }
        
        // Check all trails
        for (const trail of this.trails) {
            for (const point of trail) {
                if (point.x === x && point.y === y) {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    /**
     * Count free space in a direction (how much room to maneuver)
     */
    countFreeSpace(startX, startY, dx, dy, bounds, maxDepth = 15) {
        let count = 0;
        let x = startX;
        let y = startY;
        
        for (let i = 0; i < maxDepth; i++) {
            x += dx;
            y += dy;
            if (this.isPositionSafe(x, y, bounds)) {
                count++;
            } else {
                break;
            }
        }
        
        return count;
    }
    
    /**
     * Turn to the safest direction (most free space)
     */
    turnToSafestDirection(cycle, index, bounds) {
        const options = this.getValidTurnOptions(cycle, bounds);
        
        if (options.length === 0) return; // No escape - death is inevitable
        
        // Score each option by available space
        let bestOption = options[0];
        let bestScore = -1;
        
        for (const opt of options) {
            const nextX = cycle.x + opt.dx;
            const nextY = cycle.y + opt.dy;
            
            // Count space in the new direction
            const space = this.countFreeSpace(nextX, nextY, opt.dx, opt.dy, bounds);
            
            // Also consider perpendicular space
            let perpSpace = 0;
            if (opt.dx !== 0) {
                perpSpace = this.countFreeSpace(nextX, nextY, 0, 1, bounds) +
                           this.countFreeSpace(nextX, nextY, 0, -1, bounds);
            } else {
                perpSpace = this.countFreeSpace(nextX, nextY, 1, 0, bounds) +
                           this.countFreeSpace(nextX, nextY, -1, 0, bounds);
            }
            
            const score = space * 2 + perpSpace;
            
            if (score > bestScore) {
                bestScore = score;
                bestOption = opt;
            }
        }
        
        cycle.dx = bestOption.dx;
        cycle.dy = bestOption.dy;
    }
    
    /**
     * Get valid turn options (perpendicular directions that are safe)
     */
    getValidTurnOptions(cycle, bounds) {
        const options = [];
        
        // Perpendicular directions
        const turns = cycle.dx !== 0 
            ? [{ dx: 0, dy: -1 }, { dx: 0, dy: 1 }]
            : [{ dx: -1, dy: 0 }, { dx: 1, dy: 0 }];
        
        for (const turn of turns) {
            const nextX = cycle.x + turn.dx;
            const nextY = cycle.y + turn.dy;
            if (this.isPositionSafe(nextX, nextY, bounds)) {
                options.push(turn);
            }
        }
        
        return options;
    }
    
    /**
     * Turn toward the opponent to pressure them
     */
    turnTowardOpponent(cycle, opponent, index, bounds) {
        const options = this.getValidTurnOptions(cycle, bounds);
        if (options.length === 0) return;
        
        // Find which option gets us closer to opponent
        let bestOption = options[0];
        let bestDist = Infinity;
        
        for (const opt of options) {
            const nextX = cycle.x + opt.dx;
            const nextY = cycle.y + opt.dy;
            const dist = Math.abs(nextX - opponent.x) + Math.abs(nextY - opponent.y);
            
            if (dist < bestDist) {
                bestDist = dist;
                bestOption = opt;
            }
        }
        
        cycle.dx = bestOption.dx;
        cycle.dy = bestOption.dy;
    }
    
    /**
     * Try to cut off the opponent's path
     */
    tryToCutOff(cycle, opponent, index, bounds) {
        // Predict where opponent will be
        const predictSteps = 5;
        const futureX = opponent.x + opponent.dx * predictSteps;
        const futureY = opponent.y + opponent.dy * predictSteps;
        
        const options = this.getValidTurnOptions(cycle, bounds);
        if (options.length === 0) return;
        
        // Find turn that heads toward opponent's future position
        let bestOption = null;
        let bestScore = -Infinity;
        
        for (const opt of options) {
            const nextX = cycle.x + opt.dx;
            const nextY = cycle.y + opt.dy;
            
            // Distance to opponent's predicted position
            const distToFuture = Math.abs(nextX - futureX) + Math.abs(nextY - futureY);
            
            // Bonus for being in same row/column (potential cut-off)
            let cutOffBonus = 0;
            if (opt.dx !== 0 && Math.abs(nextY - futureY) < 3) cutOffBonus = 10;
            if (opt.dy !== 0 && Math.abs(nextX - futureX) < 3) cutOffBonus = 10;
            
            // Make sure we have room to maneuver
            const space = this.countFreeSpace(nextX, nextY, opt.dx, opt.dy, bounds);
            if (space < 5) continue; // Not enough room
            
            const score = cutOffBonus - distToFuture * 0.5 + space;
            
            if (score > bestScore) {
                bestScore = score;
                bestOption = opt;
            }
        }
        
        if (bestOption) {
            cycle.dx = bestOption.dx;
            cycle.dy = bestOption.dy;
        }
    }
    
    /**
     * Turn in a random perpendicular direction
     */
    turnRandom(cycle) {
        if (cycle.dx !== 0) {
            cycle.dy = Math.random() > 0.5 ? 1 : -1;
            cycle.dx = 0;
        } else {
            cycle.dx = Math.random() > 0.5 ? 1 : -1;
            cycle.dy = 0;
        }
    }
    
    /**
     * Turn away from danger
     */
    turnAway(cycle, gridW, gridH) {
        const options = [];
        
        if (cycle.dx !== 0) {
            // Moving horizontally, try vertical
            if (cycle.y > 5) options.push({ dx: 0, dy: -1 });
            if (cycle.y < gridH - 5) options.push({ dx: 0, dy: 1 });
        } else {
            // Moving vertically, try horizontal
            if (cycle.x > 5) options.push({ dx: -1, dy: 0 });
            if (cycle.x < gridW - 5) options.push({ dx: 1, dy: 0 });
        }
        
        if (options.length > 0) {
            const choice = options[Math.floor(Math.random() * options.length)];
            cycle.dx = choice.dx;
            cycle.dy = choice.dy;
        }
    }
    
    /**
     * Create explosion effect, track winner, and reset game
     */
    explode(losingCycle) {
        const x = losingCycle.x * this.gridSize + this.gridSize / 2;
        const y = losingCycle.y * this.gridSize + this.gridSize / 2;
        
        // Determine winner (the other cycle)
        const winnerName = losingCycle.name === 'cyan' ? 'orange' : 'cyan';
        this.scores[winnerName]++;
        this.lastWinner = winnerName;
        this.showingWinner = true;
        this.winnerDisplayTime = 1200; // Show for 1.2 seconds (shorter)
        
        // Create explosion particles (fewer, faster decay)
        for (let i = 0; i < 30; i++) {
            const angle = (Math.PI * 2 / 30) * i + Math.random() * 0.3;
            const speed = 3 + Math.random() * 4;
            this.particles.push({
                x,
                y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                life: 0.8,
                color: losingCycle.color,
                size: 2 + Math.random() * 4
            });
        }
        
        // Freeze the cycles
        for (const cycle of this.cycles) {
            cycle.dx = 0;
            cycle.dy = 0;
        }
        
        // Reset after shorter delay
        setTimeout(() => {
            if (this.isRunning) {
                this.showingWinner = false;
                this.resetGame();
            }
        }, 1500);
    }
    
    /**
     * Update particle positions and life
     */
    updateParticles(deltaTime) {
        const decay = deltaTime * 0.001;
        
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.vx *= 0.98;
            p.vy *= 0.98;
            p.life -= decay;
            
            if (p.life <= 0) {
                this.particles.splice(i, 1);
            }
        }
    }
    
    /**
     * Render everything
     */
    render() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        
        // Clear with dark background
        ctx.fillStyle = 'rgba(13, 13, 26, 0.15)';
        ctx.fillRect(0, 0, w, h);
        
        // Draw grid
        this.drawGrid();
        
        // Draw target (if set)
        if (this.target) {
            this.drawTarget();
        }
        
        // Draw trails
        this.drawTrails();
        
        // Draw cycles (heads)
        this.drawCycles();
        
        // Draw particles
        this.drawParticles();
        
        // Draw score
        this.drawScore();
        
        // Draw winner announcement
        if (this.showingWinner) {
            this.drawWinnerAnnouncement();
        }
    }
    
    /**
     * Draw the race target
     */
    drawTarget() {
        const ctx = this.ctx;
        const x = this.target.x * this.gridSize + this.gridSize / 2;
        const y = this.target.y * this.gridSize + this.gridSize / 2;
        
        // Animate pulse
        this.targetPulse += 0.05;
        const pulse = Math.sin(this.targetPulse) * 0.3 + 0.7;
        const size = this.gridSize * 0.4 * pulse;
        
        // Outer glow
        ctx.beginPath();
        ctx.arc(x, y, size + 8, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${0.1 * pulse})`;
        ctx.fill();
        
        // Diamond shape
        ctx.beginPath();
        ctx.moveTo(x, y - size);
        ctx.lineTo(x + size, y);
        ctx.lineTo(x, y + size);
        ctx.lineTo(x - size, y);
        ctx.closePath();
        
        // Fill with gradient
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, size);
        gradient.addColorStop(0, `rgba(255, 255, 255, ${0.9 * pulse})`);
        gradient.addColorStop(1, `rgba(255, 215, 0, ${0.6 * pulse})`);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        // Border
        ctx.strokeStyle = `rgba(255, 255, 255, ${pulse})`;
        ctx.lineWidth = 2;
        ctx.stroke();
    }
    
    /**
     * Draw the score in the corner
     */
    drawScore() {
        const ctx = this.ctx;
        const padding = 15;
        
        ctx.font = 'bold 14px monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        
        // Cyan score
        ctx.fillStyle = `rgba(0, 200, 200, 0.6)`;
        ctx.fillText(`CYAN: ${this.scores.cyan}`, padding, padding);
        
        // Orange score
        ctx.fillStyle = `rgba(255, 140, 0, 0.6)`;
        ctx.fillText(`ORANGE: ${this.scores.orange}`, padding, padding + 18);
    }
    
    /**
     * Draw winner announcement
     */
    drawWinnerAnnouncement() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        
        const winnerColor = this.lastWinner === 'cyan' 
            ? this.colors.cyan 
            : this.colors.orange;
        
        // Draw glowing text
        ctx.font = 'bold 32px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Glow effect
        ctx.shadowBlur = 20;
        ctx.shadowColor = `rgb(${winnerColor.r}, ${winnerColor.g}, ${winnerColor.b})`;
        
        // Draw text
        ctx.fillStyle = `rgb(${winnerColor.r}, ${winnerColor.g}, ${winnerColor.b})`;
        const winnerText = `${this.lastWinner.toUpperCase()} WINS!`;
        ctx.fillText(winnerText, w / 2, h / 2 - 20);
        
        // Score line
        ctx.font = 'bold 18px monospace';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.fillText(`${this.scores.cyan} - ${this.scores.orange}`, w / 2, h / 2 + 20);
        
        ctx.shadowBlur = 0;
    }
    
    /**
     * Draw the background grid
     */
    drawGrid() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        
        ctx.strokeStyle = this.gridColor;
        ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x < w; x += this.gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, h);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y < h; y += this.gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
            ctx.stroke();
        }
    }
    
    /**
     * Draw the light trails
     */
    drawTrails() {
        const ctx = this.ctx;
        const gs = this.gridSize;
        
        for (let t = 0; t < this.trails.length; t++) {
            const trail = this.trails[t];
            const color = this.cycles[t]?.color || this.colors.cyan;
            
            if (trail.length < 2) continue;
            
            // Draw trail with glow
            ctx.shadowBlur = 10;
            ctx.shadowColor = `rgb(${color.r}, ${color.g}, ${color.b})`;
            ctx.strokeStyle = `rgba(${color.r}, ${color.g}, ${color.b}, 0.8)`;
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            
            ctx.beginPath();
            ctx.moveTo(trail[0].x * gs + gs/2, trail[0].y * gs + gs/2);
            
            for (let i = 1; i < trail.length; i++) {
                ctx.lineTo(trail[i].x * gs + gs/2, trail[i].y * gs + gs/2);
            }
            
            ctx.stroke();
            ctx.shadowBlur = 0;
        }
    }
    
    /**
     * Draw the cycle heads
     */
    drawCycles() {
        const ctx = this.ctx;
        const gs = this.gridSize;
        
        for (const cycle of this.cycles) {
            const x = cycle.x * gs + gs/2;
            const y = cycle.y * gs + gs/2;
            const color = cycle.color;
            
            // Glow effect
            ctx.shadowBlur = 15;
            ctx.shadowColor = `rgb(${color.r}, ${color.g}, ${color.b})`;
            
            // Draw cycle head
            ctx.fillStyle = `rgb(${color.r}, ${color.g}, ${color.b})`;
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fill();
            
            // Bright center
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(x, y, 2, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.shadowBlur = 0;
        }
    }
    
    /**
     * Draw explosion particles
     */
    drawParticles() {
        const ctx = this.ctx;
        
        for (const p of this.particles) {
            const alpha = p.life;
            ctx.fillStyle = `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${alpha})`;
            ctx.shadowBlur = 8;
            ctx.shadowColor = `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${alpha})`;
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
            ctx.fill();
        }
        
        ctx.shadowBlur = 0;
    }
    
    /**
     * Check if animation is enabled in settings
     */
    static isEnabled() {
        return localStorage.getItem('tron_background_enabled') === 'true';
    }
    
    /**
     * Enable/disable the animation
     */
    static setEnabled(enabled) {
        localStorage.setItem('tron_background_enabled', enabled ? 'true' : 'false');
        
        if (enabled) {
            if (!window.tronBackground) {
                window.tronBackground = new TronBackground();
            }
            window.tronBackground.start();
        } else {
            if (window.tronBackground) {
                window.tronBackground.stop();
            }
        }
    }
}

// Auto-start if enabled
document.addEventListener('DOMContentLoaded', () => {
    if (TronBackground.isEnabled()) {
        window.tronBackground = new TronBackground();
        window.tronBackground.start();
    }
});

// Export for settings panel
window.TronBackground = TronBackground;
