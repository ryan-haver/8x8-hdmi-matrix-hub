/**
 * OREI Matrix Control - Skeleton Loader Component
 * Provides animated loading placeholders for async content
 */

class SkeletonLoader {
    /**
     * Create a skeleton loader
     * @param {Object} options - Configuration options
     * @param {string} options.type - Type of skeleton: 'card', 'grid', 'text', 'avatar', 'button'
     * @param {number} options.count - Number of skeleton items (default: 1)
     * @param {string} options.width - Custom width (optional)
     * @param {string} options.height - Custom height (optional)
     */
    constructor(options = {}) {
        this.type = options.type || 'card';
        this.count = options.count || 1;
        this.width = options.width;
        this.height = options.height;
    }

    /**
     * Render skeleton HTML
     * @returns {string} HTML string
     */
    render() {
        const items = [];
        for (let i = 0; i < this.count; i++) {
            items.push(this.renderItem());
        }
        return items.join('');
    }

    /**
     * Render a single skeleton item based on type
     */
    renderItem() {
        switch (this.type) {
            case 'card':
                return this.renderCard();
            case 'io-card':
                return this.renderIOCard();
            case 'scene-card':
                return this.renderSceneCard();
            case 'grid-cell':
                return this.renderGridCell();
            case 'text':
                return this.renderText();
            case 'text-block':
                return this.renderTextBlock();
            case 'avatar':
                return this.renderAvatar();
            case 'button':
                return this.renderButton();
            default:
                return this.renderCard();
        }
    }

    /**
     * Base skeleton element with shimmer animation
     */
    skeleton(className = '', style = '') {
        const styleAttr = style ? ` style="${style}"` : '';
        return `<div class="skeleton ${className}"${styleAttr}></div>`;
    }

    /**
     * Generic card skeleton
     */
    renderCard() {
        const style = this.getCustomStyle();
        return `
            <div class="skeleton-card"${style ? ` style="${style}"` : ''}>
                <div class="skeleton skeleton-header"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text skeleton-text--short"></div>
            </div>
        `;
    }

    /**
     * IO Card skeleton (matches io-card component)
     */
    renderIOCard() {
        return `
            <div class="skeleton-io-card">
                <div class="skeleton skeleton-avatar"></div>
                <div class="skeleton-io-info">
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text skeleton-text--short"></div>
                </div>
                <div class="skeleton skeleton-button"></div>
            </div>
        `;
    }

    /**
     * Scene card skeleton (matches scene-card component)
     */
    renderSceneCard() {
        return `
            <div class="skeleton-scene-card">
                <div class="skeleton skeleton-icon"></div>
                <div class="skeleton-scene-info">
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text skeleton-text--short"></div>
                </div>
                <div class="skeleton skeleton-button skeleton-button--sm"></div>
            </div>
        `;
    }

    /**
     * Matrix grid cell skeleton
     */
    renderGridCell() {
        return `<div class="skeleton skeleton-grid-cell"></div>`;
    }

    /**
     * Single line text skeleton
     */
    renderText() {
        const style = this.getCustomStyle();
        return this.skeleton('skeleton-text', style);
    }

    /**
     * Multi-line text block skeleton
     */
    renderTextBlock() {
        return `
            <div class="skeleton-text-block">
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text skeleton-text--short"></div>
            </div>
        `;
    }

    /**
     * Avatar/icon skeleton
     */
    renderAvatar() {
        const style = this.getCustomStyle();
        return this.skeleton('skeleton-avatar', style);
    }

    /**
     * Button skeleton
     */
    renderButton() {
        const style = this.getCustomStyle();
        return this.skeleton('skeleton-button', style);
    }

    /**
     * Get custom style string from width/height options
     */
    getCustomStyle() {
        const styles = [];
        if (this.width) styles.push(`width: ${this.width}`);
        if (this.height) styles.push(`height: ${this.height}`);
        return styles.join('; ');
    }

    /**
     * Static helper to create and mount skeleton
     * @param {HTMLElement} container - Container element
     * @param {Object} options - Skeleton options
     */
    static show(container, options = {}) {
        if (!container) return;
        const skeleton = new SkeletonLoader(options);
        container.innerHTML = skeleton.render();
        container.classList.add('skeleton-container');
    }

    /**
     * Static helper to remove skeleton from container
     * @param {HTMLElement} container - Container element
     */
    static hide(container) {
        if (!container) return;
        container.classList.remove('skeleton-container');
        // Content will be replaced by actual data
    }

    /**
     * Create matrix grid skeleton
     * @param {number} rows - Number of rows
     * @param {number} cols - Number of columns
     */
    static matrixGrid(rows = 8, cols = 8) {
        const cells = [];
        // Header row
        cells.push('<div class="skeleton skeleton-grid-header"></div>');
        for (let c = 0; c < cols; c++) {
            cells.push('<div class="skeleton skeleton-grid-header"></div>');
        }
        // Data rows
        for (let r = 0; r < rows; r++) {
            cells.push('<div class="skeleton skeleton-grid-label"></div>');
            for (let c = 0; c < cols; c++) {
                cells.push('<div class="skeleton skeleton-grid-cell"></div>');
            }
        }
        return `<div class="skeleton-matrix-grid">${cells.join('')}</div>`;
    }
}

// Export for use
window.SkeletonLoader = SkeletonLoader;
