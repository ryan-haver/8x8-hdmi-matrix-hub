/**
 * OREI Matrix Control - Icon Picker Modal Component
 * Allows users to select device icons for inputs/outputs
 * Matches Phase 1 Design Mockups
 */

class IconPicker {
    constructor() {
        this.modal = null;
        this.callback = null;
        this.selectedIcon = null;
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.searchTimer = null;
        this.recentIcons = [];
        
        this.createModal();
        this.loadRecentIcons();
    }

    /**
     * Create the modal DOM structure
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'icon-picker-overlay';
        this.modal.id = 'icon-picker-modal';
        
        this.modal.innerHTML = `
            <div class="icon-picker-modal">
                <!-- Header -->
                <div class="icon-picker-header">
                    <h3>Choose Icon</h3>
                    <button class="icon-picker-close" aria-label="Close">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                
                <!-- Search -->
                <div class="icon-picker-search">
                    <div class="icon-picker-search-wrapper">
                        <svg class="icon-picker-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"/>
                            <path d="m21 21-4.35-4.35"/>
                        </svg>
                        <input type="text" 
                               class="icon-picker-search-input" 
                               placeholder="Search icons..."
                               id="icon-picker-search">
                    </div>
                </div>
                
                <!-- Categories -->
                <div class="icon-picker-categories" id="icon-picker-categories">
                    <button class="icon-picker-category-btn active" data-category="all">All</button>
                </div>
                
                <!-- Recently Used -->
                <div class="icon-picker-recent hidden" id="icon-picker-recent">
                    <div class="icon-picker-recent-label">Recently Used</div>
                    <div class="icon-picker-recent-grid" id="icon-picker-recent-grid"></div>
                </div>
                
                <!-- Icon Grid -->
                <div class="icon-picker-content">
                    <div class="icon-picker-grid" id="icon-picker-grid"></div>
                </div>
                
                <!-- Footer with Preview -->
                <div class="icon-picker-footer">
                    <div class="icon-picker-preview">
                        <div class="icon-picker-preview-icon" id="icon-picker-preview-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <rect x="4" y="4" width="16" height="16" rx="2"/>
                                <circle cx="12" cy="12" r="3"/>
                            </svg>
                        </div>
                        <span class="icon-picker-preview-label" id="icon-picker-preview-label">Select an icon</span>
                    </div>
                    <div class="icon-picker-actions">
                        <button class="icon-picker-btn icon-picker-btn-cancel">Cancel</button>
                        <button class="icon-picker-btn icon-picker-btn-select" id="icon-picker-select-btn" disabled>Select</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.modal);
        this.attachEventListeners();
        this.renderCategories();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Close button
        this.modal.querySelector('.icon-picker-close').addEventListener('click', () => this.close());
        
        // Cancel button
        this.modal.querySelector('.icon-picker-btn-cancel').addEventListener('click', () => this.close());
        
        // Select button
        this.modal.querySelector('#icon-picker-select-btn').addEventListener('click', () => this.confirm());
        
        // Overlay click to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        // Search input
        const searchInput = this.modal.querySelector('#icon-picker-search');
        searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        
        // Keyboard navigation
        this.modal.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Escape to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('visible')) {
                this.close();
            }
        });
    }

    renderCategories() {
        const container = this.modal.querySelector('#icon-picker-categories');
        const categories = IconLibrary.getCategories();
        
        const categoryLabels = {
            'all': 'All',
            'gaming': 'Gaming',
            'streaming': 'Streaming',
            'computer': 'Computer',
            'display': 'Display',
            'media': 'Media',
            'generic': 'Generic'
        };
        
        container.innerHTML = categories.map(cat => `
            <button class="icon-picker-category-btn ${cat === 'all' ? 'active' : ''}" data-category="${cat}">${categoryLabels[cat] || cat}</button>
        `).join('');
        
        // Category click handlers
        container.querySelectorAll('.icon-picker-category-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                container.querySelectorAll('.icon-picker-category-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentCategory = btn.dataset.category;
                this.renderIcons();
            });
        });
    }



    /**
     * Load recently used icons from localStorage
     */
    loadRecentIcons() {
        try {
            this.recentIcons = JSON.parse(localStorage.getItem('orei_recent_icons')) || [];
        } catch {
            this.recentIcons = [];
        }
    }

    /**
     * Save icon to recent list
     */
    addRecentIcon(iconId) {
        this.recentIcons = [iconId, ...this.recentIcons.filter(i => i !== iconId)].slice(0, 8);
        localStorage.setItem('orei_recent_icons', JSON.stringify(this.recentIcons));
    }

    renderRecentIcons() {
        const container = this.modal.querySelector('#icon-picker-recent');
        const grid = this.modal.querySelector('#icon-picker-recent-grid');
        
        if (this.recentIcons.length === 0) {
            container.classList.add('hidden');
            return;
        }
        
        container.classList.remove('hidden');
        grid.innerHTML = this.recentIcons.map(iconId => {
            const meta = IconLibrary.getMeta(iconId);
            return `
                <button class="icon-picker-grid-item ${iconId === this.selectedIcon ? 'selected' : ''}"
                        data-icon="${iconId}"
                        tabindex="0"
                        title="${meta.label}">
                    ${IconLibrary.getIconHtml(iconId, 28, '', 'detailed')}
                </button>
            `;
        }).join('');
        
        // Click handlers for recent icons
        grid.querySelectorAll('.icon-picker-grid-item').forEach(item => {
            item.addEventListener('click', () => this.selectIcon(item.dataset.icon));
        });
    }

    /**
     * Show skeleton loading state
     */
    showSkeleton() {
        const grid = this.modal.querySelector('#icon-picker-grid');
        grid.innerHTML = Array(12).fill(0).map(() => 
            '<div class="icon-picker-skeleton"></div>'
        ).join('');
    }

    renderIcons() {
        const grid = this.modal.querySelector('#icon-picker-grid');
        
        // Get icon IDs based on search/category
        let iconIds;
        if (this.searchQuery) {
            iconIds = IconLibrary.search(this.searchQuery);
        } else if (this.currentCategory === 'all') {
            iconIds = IconLibrary.getAllIcons();
        } else {
            iconIds = IconLibrary.getByCategory(this.currentCategory);
        }
        
        // Empty state
        if (iconIds.length === 0) {
            grid.innerHTML = `
                <div class="icon-picker-empty">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="11" cy="11" r="8"/>
                        <path d="m21 21-4.35-4.35"/>
                    </svg>
                    <span class="icon-picker-empty-text">No icons found</span>
                </div>
            `;
            return;
        }
        
        // Render icons with detailed style
        grid.innerHTML = iconIds.map(iconId => {
            const meta = IconLibrary.getMeta(iconId);
            return `
                <button class="icon-picker-grid-item ${iconId === this.selectedIcon ? 'selected' : ''}"
                        data-icon="${iconId}"
                        tabindex="0"
                        title="${meta.label}">
                    ${IconLibrary.getIconHtml(iconId, 28, '', 'detailed')}
                    <span class="icon-picker-grid-item-label">${meta.label}</span>
                </button>
            `;
        }).join('');
        
        // Click handlers
        grid.querySelectorAll('.icon-picker-grid-item').forEach(item => {
            item.addEventListener('click', () => this.selectIcon(item.dataset.icon));
        });
    }

    /**
     * Handle search input with debounce
     */
    handleSearch(query) {
        clearTimeout(this.searchTimer);
        this.searchTimer = setTimeout(() => {
            this.searchQuery = query.trim();
            
            // Reset category to 'all' when searching
            if (this.searchQuery) {
                this.modal.querySelectorAll('.icon-picker-category-btn').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.category === 'all');
                });
                this.currentCategory = 'all';
            }
            
            this.renderIcons();
        }, 200);
    }

    /**
     * Handle keyboard navigation
     */
    handleKeydown(e) {
        const grid = this.modal.querySelector('#icon-picker-grid');
        const items = Array.from(grid.querySelectorAll('.icon-picker-grid-item'));
        
        if (items.length === 0) return;
        
        const currentFocus = document.activeElement;
        const currentIndex = items.indexOf(currentFocus);
        
        // Calculate grid columns
        const gridWidth = grid.offsetWidth;
        const itemWidth = items[0]?.offsetWidth || 72;
        const columns = Math.floor(gridWidth / (itemWidth + 10)); // 10px gap
        
        let newIndex = -1;
        
        switch (e.key) {
            case 'ArrowRight':
                if (currentIndex < items.length - 1) {
                    newIndex = currentIndex + 1;
                }
                break;
            case 'ArrowLeft':
                if (currentIndex > 0) {
                    newIndex = currentIndex - 1;
                }
                break;
            case 'ArrowDown':
                if (currentIndex + columns < items.length) {
                    newIndex = currentIndex + columns;
                }
                break;
            case 'ArrowUp':
                if (currentIndex - columns >= 0) {
                    newIndex = currentIndex - columns;
                }
                break;
            case 'Enter':
            case ' ':
                if (currentFocus.classList.contains('icon-picker-grid-item')) {
                    e.preventDefault();
                    this.selectIcon(currentFocus.dataset.icon);
                }
                break;
            default:
                return;
        }
        
        if (newIndex >= 0 && newIndex < items.length) {
            e.preventDefault();
            items[newIndex].focus();
        }
    }

    /**
     * Select an icon
     */
    selectIcon(iconId) {
        this.selectedIcon = iconId;
        
        // Update visual selection
        this.modal.querySelectorAll('.icon-picker-grid-item').forEach(item => {
            item.classList.toggle('selected', item.dataset.icon === iconId);
        });
        
        // Update preview
        const previewIcon = this.modal.querySelector('#icon-picker-preview-icon');
        const previewLabel = this.modal.querySelector('#icon-picker-preview-label');
        const selectBtn = this.modal.querySelector('#icon-picker-select-btn');
        
        const meta = IconLibrary.getMeta(iconId);
        previewIcon.innerHTML = IconLibrary.getIconHtml(iconId, 32, '', 'detailed');
        previewLabel.textContent = meta.label;
        selectBtn.disabled = false;
    }

    /**
     * Confirm selection and call callback
     */
    confirm() {
        if (this.selectedIcon && this.callback) {
            this.addRecentIcon(this.selectedIcon);
            this.callback(this.selectedIcon);
        }
        this.close();
    }

    /**
     * Open the icon picker
     * @param {string} currentIcon - Currently selected icon ID
     * @param {Function} callback - Called with selected icon ID
     */
    open(currentIcon = null, callback = null) {
        this.callback = callback;
        this.selectedIcon = currentIcon;
        this.searchQuery = '';
        this.currentCategory = 'all';
        
        // Reset UI state
        const searchInput = this.modal.querySelector('#icon-picker-search');
        searchInput.value = '';
        
        this.modal.querySelectorAll('.icon-picker-category-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.category === 'all');
        });
        
        // Update preview
        const previewIcon = this.modal.querySelector('#icon-picker-preview-icon');
        const previewLabel = this.modal.querySelector('#icon-picker-preview-label');
        const selectBtn = this.modal.querySelector('#icon-picker-select-btn');
        
        if (currentIcon && IconLibrary.isValid(currentIcon)) {
            const meta = IconLibrary.getMeta(currentIcon);
            previewIcon.innerHTML = IconLibrary.getIconHtml(currentIcon, 32, '', 'detailed');
            previewLabel.textContent = meta.label;
            selectBtn.disabled = false;
        } else {
            previewIcon.innerHTML = IconLibrary.getIconHtml('generic-device', 32, '', 'detailed');
            previewLabel.textContent = 'Select an icon';
            selectBtn.disabled = true;
        }
        
        // Render content
        this.loadRecentIcons();
        this.renderRecentIcons();
        this.renderIcons();
        
        // Show modal
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';
        
        // Focus search input
        setTimeout(() => searchInput.focus(), 100);
    }

    /**
     * Close the icon picker
     */
    close() {
        this.modal.classList.remove('visible');
        document.body.style.overflow = '';
        this.callback = null;
    }
}

// Create singleton instance
window.iconPicker = new IconPicker();
