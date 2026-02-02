/**
 * Theme Drawer Component
 * Enhanced slide-out panel for theme customization
 * Features: Swatch grid picker, 4 customizable presets, save/reset, advanced settings
 */

class ThemeDrawer {
    constructor() {
        this.drawer = null;
        this.overlay = null;
        this.isOpen = false;
        
        // Curated 8-color Tron-centric palette
        this.colorPalette = [
            { name: 'Cyan', hue: 187 },
            { name: 'Orange', hue: 25 },
            { name: 'Magenta', hue: 300 },
            { name: 'Lime', hue: 80 },
            { name: 'Purple', hue: 280 },
            { name: 'Gold', hue: 45 },
            { name: 'Teal', hue: 170 },
            { name: 'Pink', hue: 330 }
        ];
        
        // Default theme presets (user can customize these)
        this.defaultPresets = [
            { id: 'preset-1', name: 'Tron Classic', primaryH: 187, secondaryH: 25 },
            { id: 'preset-2', name: 'Neon', primaryH: 300, secondaryH: 80 },
            { id: 'preset-3', name: 'Royal', primaryH: 280, secondaryH: 45 },
            { id: 'preset-4', name: 'Vaporwave', primaryH: 170, secondaryH: 330 }
        ];
        
        // Load saved presets or use defaults
        this.presets = this.loadPresets();
        this.activePresetIndex = parseInt(localStorage.getItem('active_preset_index')) || 0;
        this.cardOpacity = parseFloat(localStorage.getItem('card_opacity')) || 0.8;
        this.hoverPreference = localStorage.getItem('hover_preference') || 'primary';
        
        // Editing state
        this.editingPreset = null;
        
        this.init();
    }
    
    loadPresets() {
        const saved = localStorage.getItem('theme_presets');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch (e) {
                console.warn('Failed to parse saved presets, using defaults');
            }
        }
        return JSON.parse(JSON.stringify(this.defaultPresets));
    }
    
    savePresets() {
        localStorage.setItem('theme_presets', JSON.stringify(this.presets));
        localStorage.setItem('active_preset_index', this.activePresetIndex.toString());
    }
    
    init() {
        this.createDrawerHTML();
        this.setupEventListeners();
        this.applyPreset(this.activePresetIndex, false);
        this.applyOpacity(this.cardOpacity, false);
        this.applyHoverPreference(this.hoverPreference, false);
    }
    
    getColorName(hue) {
        const color = this.colorPalette.find(c => c.hue === hue);
        return color ? color.name : `Hue ${hue}`;
    }
    
    createDrawerHTML() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'theme-drawer-overlay';
        this.overlay.setAttribute('aria-hidden', 'true');
        
        // Create drawer
        this.drawer = document.createElement('div');
        this.drawer.className = 'theme-drawer';
        this.drawer.setAttribute('aria-hidden', 'true');
        this.drawer.innerHTML = this.getDrawerHTML();
        
        document.body.appendChild(this.overlay);
        document.body.appendChild(this.drawer);
    }
    
    getDrawerHTML() {
        return `
            <div class="theme-drawer-header">
                <h3>Theme Settings</h3>
                <button class="theme-drawer-close btn-icon" aria-label="Close drawer">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                </button>
            </div>
            <div class="theme-drawer-body">
                <!-- Preset Slots -->
                <div class="theme-section">
                    <label class="theme-label">Theme Presets</label>
                    <div class="theme-preset-grid">
                        ${this.presets.map((preset, i) => `
                            <button class="theme-preset-slot ${i === this.activePresetIndex ? 'active' : ''}" 
                                    data-preset-index="${i}"
                                    title="${preset.name}">
                                <div class="preset-colors">
                                    <span class="preset-color primary" style="--hue: ${preset.primaryH}"></span>
                                    <span class="preset-color secondary" style="--hue: ${preset.secondaryH}"></span>
                                </div>
                                <span class="preset-slot-name">${preset.name}</span>
                                <button class="preset-edit-btn" data-edit-index="${i}" title="Edit preset">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                    </svg>
                                </button>
                            </button>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Color Customization (shown when editing) -->
                <div id="color-customization" class="theme-section color-customization hidden">
                    <div class="customization-header">
                        <label class="theme-label">Customize Preset</label>
                        <button class="customization-close btn-icon-sm" title="Done editing">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="20 6 9 17 4 12"/>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="color-picker-group">
                        <label class="color-picker-label">Primary Color</label>
                        <div class="color-swatch-grid" data-color-target="primary">
                            ${this.colorPalette.map(c => `
                                <button class="color-swatch" data-hue="${c.hue}" title="${c.name}"
                                        style="--hue: ${c.hue}"></button>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="color-picker-group">
                        <label class="color-picker-label">Secondary Color</label>
                        <div class="color-swatch-grid" data-color-target="secondary">
                            ${this.colorPalette.map(c => `
                                <button class="color-swatch" data-hue="${c.hue}" title="${c.name}"
                                        style="--hue: ${c.hue}"></button>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="preset-name-input-group">
                        <label class="color-picker-label">Preset Name</label>
                        <input type="text" class="preset-name-input input-unified" 
                               placeholder="Enter preset name" maxlength="20">
                    </div>
                </div>
                
                <!-- Advanced Settings -->
                <div class="theme-section">
                    <label class="theme-label">Advanced</label>
                    
                    <div class="advanced-setting">
                        <span class="setting-label">Hover Effect</span>
                        <select class="hover-preference-select select-unified">
                            <option value="primary" ${this.hoverPreference === 'primary' ? 'selected' : ''}>Primary Color</option>
                            <option value="secondary" ${this.hoverPreference === 'secondary' ? 'selected' : ''}>Secondary Color</option>
                        </select>
                    </div>
                    
                    <div class="advanced-setting">
                        <span class="setting-label">
                            Card Opacity
                            <span class="opacity-value">${Math.round(this.cardOpacity * 100)}%</span>
                        </span>
                        <input type="range" 
                               class="theme-opacity-slider" 
                               min="0" max="100" 
                               value="${Math.round(this.cardOpacity * 100)}"
                               aria-label="Card opacity">
                    </div>
                </div>
                
                <!-- Reset Button -->
                <div class="theme-section theme-actions">
                    <button class="reset-defaults-btn btn-unified-secondary">
                        Reset to Defaults
                    </button>
                </div>
            </div>
        `;
    }
    
    setupEventListeners() {
        // Close button
        this.drawer.querySelector('.theme-drawer-close').addEventListener('click', () => this.close());
        
        // Overlay click
        this.overlay.addEventListener('click', () => this.close());
        
        // Preset slot click (activate preset)
        this.drawer.querySelectorAll('.theme-preset-slot').forEach(slot => {
            slot.addEventListener('click', (e) => {
                // Don't activate if clicking edit button
                if (e.target.closest('.preset-edit-btn')) return;
                const index = parseInt(slot.dataset.presetIndex);
                this.activatePreset(index);
            });
        });
        
        // Edit preset buttons
        this.drawer.querySelectorAll('.preset-edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(btn.dataset.editIndex);
                this.startEditing(index);
            });
        });
        
        // Color swatch clicks
        this.drawer.querySelectorAll('.color-swatch-grid').forEach(grid => {
            grid.addEventListener('click', (e) => {
                const swatch = e.target.closest('.color-swatch');
                if (!swatch) return;
                const hue = parseInt(swatch.dataset.hue);
                const target = grid.dataset.colorTarget;
                this.setPresetColor(target, hue);
            });
        });
        
        // Done editing button
        this.drawer.querySelector('.customization-close').addEventListener('click', () => {
            this.stopEditing();
        });
        
        // Preset name input
        this.drawer.querySelector('.preset-name-input').addEventListener('input', (e) => {
            if (this.editingPreset !== null) {
                this.presets[this.editingPreset].name = e.target.value || `Preset ${this.editingPreset + 1}`;
                this.updatePresetSlot(this.editingPreset);
                this.savePresets();
            }
        });
        
        // Hover preference
        this.drawer.querySelector('.hover-preference-select').addEventListener('change', (e) => {
            this.applyHoverPreference(e.target.value, true);
        });
        
        // Opacity slider
        this.drawer.querySelector('.theme-opacity-slider').addEventListener('input', (e) => {
            const opacity = parseInt(e.target.value) / 100;
            this.applyOpacity(opacity, true);
            this.drawer.querySelector('.opacity-value').textContent = `${e.target.value}%`;
        });
        
        // Reset defaults
        this.drawer.querySelector('.reset-defaults-btn').addEventListener('click', () => {
            this.resetToDefaults();
        });
        
        // Escape key closes drawer
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                if (this.editingPreset !== null) {
                    this.stopEditing();
                } else {
                    this.close();
                }
            }
        });
    }
    
    activatePreset(index) {
        this.activePresetIndex = index;
        this.applyPreset(index, true);
        
        // Update UI
        this.drawer.querySelectorAll('.theme-preset-slot').forEach((slot, i) => {
            slot.classList.toggle('active', i === index);
        });
    }
    
    startEditing(index) {
        this.editingPreset = index;
        const preset = this.presets[index];
        
        // Show customization panel
        const panel = this.drawer.querySelector('#color-customization');
        panel.classList.remove('hidden');
        
        // Set name input
        this.drawer.querySelector('.preset-name-input').value = preset.name;
        
        // Highlight selected swatches
        this.updateSwatchSelection('primary', preset.primaryH);
        this.updateSwatchSelection('secondary', preset.secondaryH);
        
        // Also activate this preset
        this.activatePreset(index);
    }
    
    stopEditing() {
        this.editingPreset = null;
        this.drawer.querySelector('#color-customization').classList.add('hidden');
    }
    
    setPresetColor(target, hue) {
        if (this.editingPreset === null) return;
        
        const preset = this.presets[this.editingPreset];
        if (target === 'primary') {
            preset.primaryH = hue;
        } else {
            preset.secondaryH = hue;
        }
        
        this.updateSwatchSelection(target, hue);
        this.updatePresetSlot(this.editingPreset);
        this.savePresets();
        
        // Apply live
        if (this.editingPreset === this.activePresetIndex) {
            this.applyPreset(this.activePresetIndex, false);
        }
    }
    
    updateSwatchSelection(target, selectedHue) {
        const grid = this.drawer.querySelector(`.color-swatch-grid[data-color-target="${target}"]`);
        grid.querySelectorAll('.color-swatch').forEach(swatch => {
            swatch.classList.toggle('selected', parseInt(swatch.dataset.hue) === selectedHue);
        });
    }
    
    updatePresetSlot(index) {
        const preset = this.presets[index];
        const slot = this.drawer.querySelector(`.theme-preset-slot[data-preset-index="${index}"]`);
        if (!slot) return;
        
        slot.querySelector('.preset-slot-name').textContent = preset.name;
        slot.querySelector('.preset-color.primary').style.setProperty('--hue', preset.primaryH);
        slot.querySelector('.preset-color.secondary').style.setProperty('--hue', preset.secondaryH);
    }
    
    applyPreset(index, save = true) {
        const preset = this.presets[index];
        if (!preset) return;
        
        const root = document.documentElement;
        
        // Primary accent
        root.style.setProperty('--accent-h', preset.primaryH);
        root.style.setProperty('--accent-s', '92%');
        root.style.setProperty('--accent-l', '50%');
        
        // Secondary accent
        root.style.setProperty('--secondary-h', preset.secondaryH);
        
        // Update status-active to use accent
        root.style.setProperty('--status-active-h', preset.primaryH);
        
        // Dispatch theme change event
        document.dispatchEvent(new CustomEvent('themechange', { 
            detail: { 
                presetIndex: index, 
                preset,
                primaryH: preset.primaryH,
                secondaryH: preset.secondaryH
            } 
        }));
        
        if (save) {
            this.savePresets();
        }
    }
    
    applyHoverPreference(preference, save = true) {
        this.hoverPreference = preference;
        const root = document.documentElement;
        
        if (preference === 'secondary') {
            root.style.setProperty('--hover-glow-h', 'var(--secondary-h)');
        } else {
            root.style.setProperty('--hover-glow-h', 'var(--accent-h)');
        }
        
        if (save) {
            localStorage.setItem('hover_preference', preference);
        }
    }
    
    applyOpacity(opacity, save = true) {
        this.cardOpacity = opacity;
        document.documentElement.style.setProperty('--card-opacity', opacity);
        
        if (save) {
            localStorage.setItem('card_opacity', opacity.toString());
        }
    }
    
    resetToDefaults() {
        // Reset presets to defaults
        this.presets = JSON.parse(JSON.stringify(this.defaultPresets));
        this.activePresetIndex = 0;
        this.cardOpacity = 0.8;
        this.hoverPreference = 'primary';
        
        // Save
        this.savePresets();
        localStorage.setItem('card_opacity', '0.8');
        localStorage.setItem('hover_preference', 'primary');
        
        // Apply
        this.applyPreset(0, false);
        this.applyOpacity(0.8, false);
        this.applyHoverPreference('primary', false);
        
        // Rebuild drawer UI
        this.drawer.innerHTML = this.getDrawerHTML();
        this.setupEventListeners();
        
        // Show feedback
        if (window.showToast) {
            window.showToast('Theme reset to defaults', 'success');
        }
    }
    
    open() {
        // Notify overlay manager to close other overlays
        if (window.overlayManager) {
            window.overlayManager.onOpen('theme-drawer');
        }
        this.isOpen = true;
        this.drawer.setAttribute('aria-hidden', 'false');
        this.overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        // Notify overlay manager
        if (window.overlayManager) {
            window.overlayManager.onClose('theme-drawer');
        }
        this.isOpen = false;
        this.stopEditing();
        this.drawer.setAttribute('aria-hidden', 'true');
        this.overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
}

// Initialize and expose globally
document.addEventListener('DOMContentLoaded', () => {
    window.themeDrawer = new ThemeDrawer();
    
    // Register with overlay manager
    if (window.overlayManager) {
        window.overlayManager.register('theme-drawer', {
            close: () => window.themeDrawer.close(),
            isOpen: () => window.themeDrawer.isOpen
        });
    }
    
    // Hook up theme toggle button
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => window.themeDrawer.toggle());
    }
});
