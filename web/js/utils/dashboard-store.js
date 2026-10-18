/**
 * DashboardStore
 *
 * Provides a single server-backed store for dashboard widgets and layout
 * (per DI-5 & UI-08).
 *
 * - Loads and saves layout via GET /api/dashboard/layout and POST/PUT /api/dashboard/layout.
 * - Performs a one-time idempotent migration of legacy localStorage keys
 *   (orei_dashboard_widgets, orei_pinned_scenes, matrix_dashboard_layout) to the server API
 *   on first load, sets orei_dashboard_migrated_v1 = 'true', and clears legacy keys so
 *   deleted defaults never resurrect (fixing UI-08).
 * - Supports widget add, remove, reorder, and resize with debounced server persistence.
 */

class DashboardStore {
    /**
     * @param {Object} [options]
     * @param {string} [options.apiBase='/api'] - Base URL for REST API calls
     * @param {Object} [options.apiClient] - Optional ApiClient instance
     * @param {Storage} [options.storage] - LocalStorage interface (defaults to window.localStorage)
     * @param {number} [options.debounceMs=250] - Debounce delay in ms for server saves
     */
    constructor(options = {}) {
        this.apiBase = options.apiBase || '/api';
        this.apiClient = options.apiClient || (typeof window !== 'undefined' && window.apiClient ? window.apiClient : null);
        this.storage = options.storage || (typeof window !== 'undefined' && window.localStorage ? window.localStorage : null);
        this.debounceMs = options.debounceMs !== undefined ? options.debounceMs : 250;

        this.widgets = [];
        this.version = 1;
        this.listeners = new Set();
        this._isLoaded = false;

        // Debounced persistence state
        this._saveTimeout = null;
        this._pendingSavePromise = null;
        this._pendingResolve = null;
        this._pendingReject = null;

        this._migratedKey = 'orei_dashboard_migrated_v1';
        this.legacyKeys = [
            'orei_dashboard_widgets',
            'orei_pinned_scenes',
            'matrix_dashboard_layout',
            'orei_dashboard_config'
        ];
    }

    /**
     * Check if one-time legacy migration has already occurred
     * @returns {boolean}
     */
    isMigrated() {
        if (!this.storage) return false;
        try {
            return this.storage.getItem(this._migratedKey) === 'true';
        } catch (e) {
            return false;
        }
    }

    /**
     * Perform one-time idempotent migration of legacy localStorage keys
     * (orei_dashboard_widgets, orei_pinned_scenes, matrix_dashboard_layout)
     * to the server API on first load, then sets orei_dashboard_migrated_v1 = 'true'
     * and clears the legacy keys so deleted defaults never resurrect (fixing UI-08).
     *
     * @returns {Promise<Object>} Migration result
     */
    async migrateLegacyStorage() {
        if (this.isMigrated()) {
            return { migrated: false, alreadyMigrated: true };
        }
        if (!this.storage) {
            return { migrated: false, error: 'No storage available' };
        }

        const migratedCards = [];
        const seenKeys = new Set();
        let order = 0;

        const addCard = (card) => {
            if (!card) return;
            const id = card.id ? String(card.id) : null;
            if (!id) return;
            const type = card.type || 'preset';
            const key = `${type}:${id}`;
            if (seenKeys.has(key)) return;
            seenKeys.add(key);

            migratedCards.push({
                type,
                id,
                order: card.order !== undefined ? card.order : order++,
                ...(card.size ? { size: card.size } : {}),
                ...(card.width ? { width: card.width } : {}),
                ...(card.height ? { height: card.height } : {})
            });
        };

        try {
            // 1. Check orei_pinned_scenes (array of scene/profile IDs or objects)
            const rawScenes = this.storage.getItem('orei_pinned_scenes');
            if (rawScenes) {
                try {
                    const scenes = JSON.parse(rawScenes);
                    if (Array.isArray(scenes)) {
                        scenes.forEach((s) => {
                            if (typeof s === 'string') {
                                addCard({ type: 'profile', id: s });
                            } else if (s && (s.id || s.profile_id)) {
                                addCard({ type: 'profile', id: s.id || s.profile_id, ...s });
                            }
                        });
                    }
                } catch (e) {
                    // Ignore malformed JSON
                }
            }

            // 2. Check orei_dashboard_widgets (array of widget IDs or configs)
            const rawWidgets = this.storage.getItem('orei_dashboard_widgets');
            if (rawWidgets) {
                try {
                    const widgets = JSON.parse(rawWidgets);
                    if (Array.isArray(widgets)) {
                        widgets.forEach((w) => {
                            if (typeof w === 'string') {
                                // Default numeric strings to preset, others to custom card
                                const isNum = /^\d+$/.test(w);
                                addCard({ type: isNum ? 'preset' : 'preset', id: w });
                            } else if (w && w.id) {
                                addCard(w);
                            }
                        });
                    }
                } catch (e) {
                    // Ignore malformed JSON
                }
            }

            // 3. Check matrix_dashboard_layout (layout object or array)
            const rawLayout = this.storage.getItem('matrix_dashboard_layout');
            if (rawLayout) {
                try {
                    const layout = JSON.parse(rawLayout);
                    const cards = Array.isArray(layout) ? layout : (layout.cards || []);
                    cards.forEach(addCard);
                } catch (e) {
                    // Ignore malformed JSON
                }
            }

            // 4. Check orei_dashboard_config (pinnedWidgets array)
            const rawConfig = this.storage.getItem('orei_dashboard_config');
            if (rawConfig) {
                try {
                    const config = JSON.parse(rawConfig);
                    const pinned = config.pinnedWidgets || [];
                    if (Array.isArray(pinned)) {
                        pinned.forEach((p) => {
                            if (typeof p === 'string') {
                                addCard({ type: 'preset', id: p });
                            } else if (p && p.id) {
                                addCard(p);
                            }
                        });
                    }
                } catch (e) {
                    // Ignore malformed JSON
                }
            }

            // If any cards were collected from legacy storage, persist them to the server API
            if (migratedCards.length > 0) {
                await this._sendLayoutToServer({
                    version: 1,
                    cards: migratedCards
                });
            }

            // Mark migration as complete
            this.storage.setItem(this._migratedKey, 'true');

            // Clear legacy keys so deleted defaults never resurrect (fixing UI-08)
            this.legacyKeys.forEach((key) => {
                try {
                    this.storage.removeItem(key);
                } catch (e) {
                    // Ignore remove error
                }
            });

            return { migrated: true, count: migratedCards.length };
        } catch (err) {
            // Even on error, mark migration flag if legacy keys were touched to prevent loop
            try {
                this.storage.setItem(this._migratedKey, 'true');
            } catch (e) {
                // Ignore
            }
            return { migrated: false, error: err.message };
        }
    }

    /**
     * Load layout from server API (GET /api/dashboard/layout).
     * Automatically triggers one-time migration on first load if needed.
     *
     * @returns {Promise<Array>} Current widgets array
     */
    async loadLayout() {
        if (!this.isMigrated()) {
            await this.migrateLegacyStorage();
        }

        try {
            let data = null;
            if (this.apiClient && typeof this.apiClient.getDashboardLayout === 'function') {
                const res = await this.apiClient.getDashboardLayout();
                data = res?.data || res;
            } else if (typeof fetch !== 'undefined') {
                const res = await fetch(`${this.apiBase}/dashboard/layout`);
                if (res.ok) {
                    const json = await res.json();
                    data = json.data || json;
                }
            }

            if (data && Array.isArray(data.cards)) {
                this.version = data.version || 1;
                this.widgets = data.cards.map((c, idx) => ({
                    id: String(c.id),
                    type: c.type || 'preset',
                    order: c.order !== undefined ? c.order : idx,
                    ...(c.size ? { size: c.size } : {}),
                    ...(c.width ? { width: c.width } : {}),
                    ...(c.height ? { height: c.height } : {})
                }));
            } else {
                this.widgets = [];
            }

            this._isLoaded = true;
            this._notify('load', this.getWidgets());
            return this.getWidgets();
        } catch (err) {
            this._isLoaded = true;
            return this.getWidgets();
        }
    }

    /**
     * Send layout to server API (POST or PUT /api/dashboard/layout)
     * @private
     * @param {Object} payload - { version, cards }
     * @returns {Promise<Object>}
     */
    async _sendLayoutToServer(payload) {
        if (this.apiClient && typeof this.apiClient.replaceDashboardLayout === 'function') {
            return this.apiClient.replaceDashboardLayout(payload);
        }

        // Try POST first, then PUT if method not allowed
        const methods = ['POST', 'PUT'];
        let lastErr = null;

        for (const method of methods) {
            try {
                const res = await fetch(`${this.apiBase}/dashboard/layout`, {
                    method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.status === 405) {
                    continue; // try next HTTP verb
                }

                if (res.ok) {
                    return res.json().catch(() => ({ success: true }));
                }

                const errText = await res.text().catch(() => '');
                throw new Error(`Failed to save dashboard layout (${method}): HTTP ${res.status} ${errText}`);
            } catch (err) {
                lastErr = err;
            }
        }

        throw lastErr || new Error('Failed to save dashboard layout');
    }

    /**
     * Schedule a debounced save to server persistence
     * @returns {Promise<Object>} Resolves when the save completes
     */
    scheduleSave() {
        if (this._saveTimeout) {
            clearTimeout(this._saveTimeout);
            this._saveTimeout = null;
        }

        if (!this._pendingSavePromise) {
            this._pendingSavePromise = new Promise((resolve, reject) => {
                this._pendingResolve = resolve;
                this._pendingReject = reject;
            });
        }

        this._saveTimeout = setTimeout(async () => {
            this._saveTimeout = null;
            const resolve = this._pendingResolve;
            const reject = this._pendingReject;
            this._pendingSavePromise = null;
            this._pendingResolve = null;
            this._pendingReject = null;

            try {
                const result = await this.saveLayout();
                if (resolve) resolve(result);
            } catch (err) {
                if (reject) reject(err);
            }
        }, this.debounceMs);

        return this._pendingSavePromise;
    }

    /**
     * Immediately execute any pending or immediate save to the server
     * @returns {Promise<Object>}
     */
    async flush() {
        if (this._saveTimeout) {
            clearTimeout(this._saveTimeout);
            this._saveTimeout = null;
        }

        const resolve = this._pendingResolve;
        const reject = this._pendingReject;
        this._pendingSavePromise = null;
        this._pendingResolve = null;
        this._pendingReject = null;

        try {
            const result = await this.saveLayout();
            if (resolve) resolve(result);
            return result;
        } catch (err) {
            if (reject) reject(err);
            throw err;
        }
    }

    /**
     * Directly save the current layout to server API
     * @returns {Promise<Object>}
     */
    async saveLayout() {
        const payload = {
            version: this.version || 1,
            cards: this.widgets.map((w, index) => ({
                type: w.type || 'preset',
                id: String(w.id),
                order: w.order !== undefined ? w.order : index,
                ...(w.size ? { size: w.size } : {}),
                ...(w.width ? { width: w.width } : {}),
                ...(w.height ? { height: w.height } : {})
            }))
        };

        const result = await this._sendLayoutToServer(payload);
        this._notify('save', this.getWidgets());
        return result;
    }

    // ===== Widget & Card Management Methods =====

    /**
     * Add a widget or card to the layout with debounced server persistence
     * @param {Object|string} widget - Widget definition or ID
     * @returns {Object} Added widget
     */
    addWidget(widget) {
        if (!widget) throw new Error('Widget is required');

        const item = typeof widget === 'string'
            ? { id: widget, type: 'preset' }
            : { ...widget };

        item.id = String(item.id);
        item.type = item.type || 'preset';

        // Check for existing widget by id (or type:id)
        const existingIdx = this.widgets.findIndex(
            (w) => w.id === item.id && (w.type === item.type || !item.type)
        );

        if (existingIdx !== -1) {
            // Update existing widget properties
            this.widgets[existingIdx] = {
                ...this.widgets[existingIdx],
                ...item
            };
            this._normalizeOrders();
            this.scheduleSave();
            this._notify('update', this.widgets[existingIdx]);
            return this.widgets[existingIdx];
        }

        if (item.order === undefined) {
            item.order = this.widgets.length;
        }

        this.widgets.push(item);
        this._normalizeOrders();
        this.scheduleSave();
        this._notify('add', item);
        return item;
    }

    /**
     * Alias for addWidget
     * @param {Object|string} card
     * @returns {Object}
     */
    addCard(card) {
        return this.addWidget(card);
    }

    /**
     * Remove a widget or card from the layout with debounced server persistence
     * @param {string} id - Widget or card ID
     * @param {string} [type] - Optional card type filter
     * @returns {boolean} True if removed
     */
    removeWidget(id, type = null) {
        const strId = String(id);
        const prevLen = this.widgets.length;

        this.widgets = this.widgets.filter((w) => {
            if (type) {
                return !(w.id === strId && w.type === type);
            }
            return w.id !== strId;
        });

        if (this.widgets.length !== prevLen) {
            this._normalizeOrders();
            this.scheduleSave();
            this._notify('remove', { id: strId, type });
            return true;
        }

        return false;
    }

    /**
     * Alias for removeWidget
     * @param {string} id
     * @param {string} [type]
     * @returns {boolean}
     */
    removeCard(id, type = null) {
        return this.removeWidget(id, type);
    }

    /**
     * Reorder widgets to match the given ordered list of IDs or objects
     * with debounced server persistence.
     *
     * @param {Array<string|Object>} orderedItems - List of IDs or widget objects in desired order
     * @returns {Array} Updated widgets list
     */
    reorderWidgets(orderedItems) {
        if (!Array.isArray(orderedItems)) return this.getWidgets();

        const orderedIds = orderedItems.map((item) => {
            if (typeof item === 'string') return item;
            return item && item.id ? String(item.id) : '';
        }).filter(Boolean);

        const newWidgets = [];
        const remaining = [...this.widgets];

        orderedIds.forEach((id) => {
            const idx = remaining.findIndex((w) => w.id === id);
            if (idx !== -1) {
                newWidgets.push(remaining.splice(idx, 1)[0]);
            }
        });

        // Append any items that were not mentioned in orderedIds
        newWidgets.push(...remaining);

        this.widgets = newWidgets;
        this._normalizeOrders();
        this.scheduleSave();
        this._notify('reorder', this.getWidgets());
        return this.getWidgets();
    }

    /**
     * Alias for reorderWidgets
     * @param {Array} orderedItems
     * @returns {Array}
     */
    reorderCards(orderedItems) {
        return this.reorderWidgets(orderedItems);
    }

    /**
     * Resize a widget (update its size, width, height, or dimensions)
     * with debounced server persistence.
     *
     * @param {string} id - Widget ID
     * @param {string|number|Object} sizeOrDimensions - Size string ('small', 'medium', 'large') or object { width, height }
     * @returns {Object|null} Updated widget or null if not found
     */
    resizeWidget(id, sizeOrDimensions) {
        const strId = String(id);
        const widget = this.widgets.find((w) => w.id === strId);
        if (!widget) return null;

        if (typeof sizeOrDimensions === 'object' && sizeOrDimensions !== null) {
            Object.assign(widget, sizeOrDimensions);
        } else {
            widget.size = sizeOrDimensions;
        }

        this.scheduleSave();
        this._notify('resize', widget);
        return { ...widget };
    }

    /**
     * Re-index the order property across all widgets sequentially from 0
     * @private
     */
    _normalizeOrders() {
        this.widgets.forEach((w, index) => {
            w.order = index;
        });
    }

    /**
     * Return a copy of the current widgets array
     * @returns {Array<Object>}
     */
    getWidgets() {
        return this.widgets.map((w) => ({ ...w }));
    }

    /**
     * Alias for getWidgets
     * @returns {Array<Object>}
     */
    getCards() {
        return this.getWidgets();
    }

    /**
     * Return the full layout object
     * @returns {Object}
     */
    getLayout() {
        return {
            version: this.version || 1,
            cards: this.getWidgets()
        };
    }

    /**
     * Subscribe to changes in the store
     * @param {Function} listener - Callback (event, data, store) => {}
     * @returns {Function} Unsubscribe function
     */
    subscribe(listener) {
        if (typeof listener === 'function') {
            this.listeners.add(listener);
        }
        return () => {
            this.listeners.delete(listener);
        };
    }

    /**
     * Notify subscribers of an event
     * @private
     * @param {string} event
     * @param {*} data
     */
    _notify(event, data) {
        this.listeners.forEach((fn) => {
            try {
                fn(event, data, this);
            } catch (err) {
                // Ignore listener exceptions
            }
        });
    }
}

// Expose both window.DashboardStore and window.dashboardStore
if (typeof window !== 'undefined') {
    window.DashboardStore = DashboardStore;
    if (!window.dashboardStore) {
        window.dashboardStore = new DashboardStore();
    }
}
