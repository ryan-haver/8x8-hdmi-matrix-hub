/**
 * NounProject Icon Tool - API Client
 * Lightweight client for integration with other tools (e.g., HDMI Matrix)
 * 
 * Usage:
 *   import { NounProjectClient } from './noun-project-tool/client.js';
 *   const client = new NounProjectClient('http://localhost:3000');
 *   const icons = await client.search('television', { limit: 10 });
 */

export class NounProjectClient {
  /**
   * Create a new client instance
   * @param {string} baseUrl - Base URL of the NounProject Icon Tool server
   */
  constructor(baseUrl = 'http://localhost:3000') {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
  }

  /**
   * Make an API request
   * @private
   */
  async _request(method, endpoint, data = null) {
    const url = `${this.baseUrl}${endpoint}`;
    const options = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    
    if (data) {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    const json = await response.json();
    
    if (!response.ok) {
      throw new Error(json.error || `HTTP ${response.status}`);
    }
    
    return json;
  }

  // ============================================
  // CORE FUNCTIONALITY
  // ============================================

  /**
   * Check if the service is healthy
   * @returns {Promise<{status: string, version: string, services: object}>}
   */
  async health() {
    return this._request('GET', '/api/health');
  }

  /**
   * Search for icons
   * @param {string} query - Search query
   * @param {object} options - Search options
   * @param {number} options.limit - Max results (default: 30)
   * @param {string} options.style - Icon style filter
   * @param {number} options.page - Page number
   * @returns {Promise<{icons: object[]}>}
   */
  async search(query, options = {}) {
    const params = new URLSearchParams({ q: query, ...options });
    const result = await this._request('GET', `/api/search?${params}`);
    return result.icons || [];
  }

  /**
   * Get API usage statistics
   * @returns {Promise<{usage: number, limit: number, percentUsed: number}>}
   */
  async getUsage() {
    return this._request('GET', '/api/usage');
  }

  /**
   * Get overall statistics
   * @returns {Promise<{catalog: object, api: object, proxy: object}>}
   */
  async getStats() {
    return this._request('GET', '/api/stats');
  }

  /**
   * Download icons
   * @param {string|string[]} query - Search query or array of icon IDs
   * @param {string} outputDir - Output directory path
   * @param {number} limit - Max icons to download (if query)
   * @returns {Promise<{jobId: string, queued: number}>}
   */
  async download(query, outputDir = './icons', limit = 50) {
    const body = typeof query === 'string' 
      ? { query, outputDir, limit }
      : { ids: query, outputDir };
    return this._request('POST', '/api/download', body);
  }

  /**
   * Get download job status
   * @param {string} jobId - Job ID from download()
   * @returns {Promise<{status: string, progress: object}>}
   */
  async getDownloadStatus(jobId) {
    return this._request('GET', `/api/download/${jobId}`);
  }

  // ============================================
  // SETTINGS MANAGEMENT
  // ============================================

  /**
   * Get all settings
   * @returns {Promise<{settings: object}>}
   */
  async getSettings() {
    return this._request('GET', '/api/settings');
  }

  /**
   * Update settings
   * @param {object} settings - Settings to update
   * @returns {Promise<{success: boolean}>}
   */
  async updateSettings(settings) {
    return this._request('PUT', '/api/settings', settings);
  }

  /**
   * Get proxy configuration
   * @returns {Promise<{proxy: object}>}
   */
  async getProxyConfig() {
    return this._request('GET', '/api/settings/proxy');
  }

  /**
   * Update proxy settings
   * @param {object} options - Proxy options
   * @param {string} options.strategy - Rotation strategy (smart, round-robin, random, least-used)
   * @returns {Promise<{success: boolean}>}
   */
  async setProxyStrategy(strategy) {
    return this._request('PUT', '/api/settings/proxy', { strategy });
  }

  /**
   * Reset proxy usage statistics
   * @returns {Promise<{success: boolean}>}
   */
  async resetProxyStats() {
    return this._request('DELETE', '/api/settings/proxy/stats');
  }

  /**
   * Get PIA configuration status
   * @returns {Promise<{pia: {configured: boolean, username: string|null}}>}
   */
  async getPiaStatus() {
    return this._request('GET', '/api/settings/pia');
  }

  /**
   * Set PIA credentials
   * @param {string} username - PIA username
   * @param {string} password - PIA password
   * @returns {Promise<{success: boolean, proxies: number}>}
   */
  async setPiaCredentials(username, password) {
    return this._request('PUT', '/api/settings/pia', { username, password });
  }

  /**
   * Remove PIA credentials
   * @returns {Promise<{success: boolean}>}
   */
  async removePiaCredentials() {
    return this._request('DELETE', '/api/settings/pia');
  }

  /**
   * Hot-reload configuration from disk
   * @returns {Promise<{success: boolean, proxy: object}>}
   */
  async reloadConfig() {
    return this._request('POST', '/api/reload');
  }

  // ============================================
  // CATALOG
  // ============================================

  /**
   * Get a specific icon from catalog
   * @param {string} id - Icon ID
   * @returns {Promise<{icon: object}>}
   */
  async getIcon(id) {
    return this._request('GET', `/api/catalog/${id}`);
  }

  /**
   * Search and save results to catalog
   * @param {string} query - Search query
   * @param {number} limit - Max results
   * @returns {Promise<{count: number, icons: object[]}>}
   */
  async searchAndSave(query, limit = 50) {
    return this._request('POST', '/api/search/save', { query, limit });
  }

  // ============================================
  // API v2.0 - ICON CONTENT
  // ============================================

  /**
   * Get full icon with SVG content
   * @param {string} id - Icon ID
   * @returns {Promise<{icon: object, svg: string}>}
   */
  async getIconFull(id) {
    return this._request('GET', `/api/icon/${id}`);
  }

  /**
   * Get raw SVG content
   * @param {string} id - Icon ID
   * @returns {Promise<string>}
   */
  async getIconSvg(id) {
    const response = await fetch(`${this.baseUrl}/api/icon/${id}/svg`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.text();
  }

  /**
   * Get PNG at specified size
   * @param {string} id - Icon ID
   * @param {number} size - Size in pixels (default: 64)
   * @returns {Promise<ArrayBuffer>}
   */
  async getIconPng(id, size = 64) {
    const response = await fetch(`${this.baseUrl}/api/icon/${id}/png?size=${size}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.arrayBuffer();
  }

  // ============================================
  // API v2.0 - CATALOG MANAGEMENT
  // ============================================

  /**
   * List all icons in catalog
   * @param {object} options - Pagination options
   * @returns {Promise<{icons: object[], count: number}>}
   */
  async getCatalog(options = {}) {
    const params = new URLSearchParams(options);
    return this._request('GET', `/api/catalog?${params}`);
  }

  /**
   * Export catalog
   * @param {string} format - 'json' or 'csv'
   * @returns {Promise<{icons: object[]}>}
   */
  async exportCatalog(format = 'json') {
    return this._request('GET', `/api/catalog/export?format=${format}`);
  }

  /**
   * Add multiple icons to catalog
   * @param {object[]} icons - Array of icon objects
   * @returns {Promise<{added: number}>}
   */
  async batchAddIcons(icons) {
    return this._request('POST', '/api/catalog/batch', { icons });
  }

  /**
   * Import catalog from JSON
   * @param {object[]} icons - Array of icon objects
   * @param {boolean} merge - Merge with existing (true) or replace (false)
   * @returns {Promise<{imported: number, total: number}>}
   */
  async importCatalog(icons, merge = true) {
    return this._request('POST', '/api/catalog/import', { icons, merge });
  }

  /**
   * Delete icon from catalog
   * @param {string} id - Icon ID
   * @returns {Promise<{success: boolean}>}
   */
  async deleteIcon(id) {
    return this._request('DELETE', `/api/catalog/${id}`);
  }

  /**
   * Clear entire catalog
   * @returns {Promise<{success: boolean}>}
   */
  async clearCatalog() {
    return this._request('DELETE', '/api/catalog/clear?confirm=yes');
  }

  // ============================================
  // API v2.0 - COLLECTIONS
  // ============================================

  /**
   * List all collections
   * @returns {Promise<{collections: object[]}>}
   */
  async getCollections() {
    return this._request('GET', '/api/collections');
  }

  /**
   * Create a new collection
   * @param {string} name - Collection name
   * @param {string} description - Collection description
   * @returns {Promise<{success: boolean}>}
   */
  async createCollection(name, description = '') {
    return this._request('POST', '/api/collections', { name, description });
  }

  /**
   * Get a collection with its icons
   * @param {string} name - Collection name
   * @returns {Promise<{name: string, icons: object[]}>}
   */
  async getCollection(name) {
    return this._request('GET', `/api/collections/${encodeURIComponent(name)}`);
  }

  /**
   * Update collection metadata
   * @param {string} name - Collection name
   * @param {object} updates - Fields to update
   * @returns {Promise<{success: boolean}>}
   */
  async updateCollection(name, updates) {
    return this._request('PUT', `/api/collections/${encodeURIComponent(name)}`, updates);
  }

  /**
   * Delete a collection
   * @param {string} name - Collection name
   * @returns {Promise<{success: boolean}>}
   */
  async deleteCollection(name) {
    return this._request('DELETE', `/api/collections/${encodeURIComponent(name)}`);
  }

  /**
   * Add icons to a collection
   * @param {string} name - Collection name
   * @param {string[]} iconIds - Array of icon IDs
   * @returns {Promise<{added: number, total: number}>}
   */
  async addToCollection(name, iconIds) {
    return this._request('POST', `/api/collections/${encodeURIComponent(name)}/icons`, { iconIds });
  }

  /**
   * Remove icon from collection
   * @param {string} name - Collection name
   * @param {string} iconId - Icon ID
   * @returns {Promise<{success: boolean}>}
   */
  async removeFromCollection(name, iconId) {
    return this._request('DELETE', `/api/collections/${encodeURIComponent(name)}/icons/${iconId}`);
  }

  /**
   * Download all icons in a collection
   * @param {string} name - Collection name
   * @param {string} outputDir - Output directory
   * @returns {Promise<{jobId: string, queued: number}>}
   */
  async downloadCollection(name, outputDir = './icons') {
    return this._request('POST', `/api/collections/${encodeURIComponent(name)}/download`, { outputDir });
  }

  // ============================================
  // API v2.0 - TAGS
  // ============================================

  /**
   * Get all unique tags
   * @returns {Promise<{tags: string[]}>}
   */
  async getAllTags() {
    return this._request('GET', '/api/tags');
  }

  /**
   * Get tags for an icon
   * @param {string} id - Icon ID
   * @returns {Promise<{tags: string[]}>}
   */
  async getIconTags(id) {
    return this._request('GET', `/api/icon/${id}/tags`);
  }

  /**
   * Add tag to icon
   * @param {string} id - Icon ID
   * @param {string} tag - Tag to add
   * @returns {Promise<{tags: string[]}>}
   */
  async addTag(id, tag) {
    return this._request('POST', `/api/icon/${id}/tags`, { tag });
  }

  /**
   * Remove tag from icon
   * @param {string} id - Icon ID
   * @param {string} tag - Tag to remove
   * @returns {Promise<{tags: string[]}>}
   */
  async removeTag(id, tag) {
    return this._request('DELETE', `/api/icon/${id}/tags/${encodeURIComponent(tag)}`);
  }

  // ============================================
  // API v2.0 - FAVORITES
  // ============================================

  /**
   * Get all favorite icons
   * @returns {Promise<{icons: object[]}>}
   */
  async getFavorites() {
    return this._request('GET', '/api/favorites');
  }

  /**
   * Mark icon as favorite
   * @param {string} id - Icon ID
   * @returns {Promise<{success: boolean}>}
   */
  async addFavorite(id) {
    return this._request('POST', `/api/icon/${id}/favorite`);
  }

  /**
   * Remove icon from favorites
   * @param {string} id - Icon ID
   * @returns {Promise<{success: boolean}>}
   */
  async removeFavorite(id) {
    return this._request('DELETE', `/api/icon/${id}/favorite`);
  }

  // ============================================
  // API v2.0 - SEARCH HISTORY
  // ============================================

  /**
   * Get search history
   * @param {number} limit - Max results
   * @returns {Promise<{history: object[]}>}
   */
  async getSearchHistory(limit = 50) {
    return this._request('GET', `/api/search/history?limit=${limit}`);
  }

  /**
   * Clear search history
   * @returns {Promise<{success: boolean}>}
   */
  async clearSearchHistory() {
    return this._request('DELETE', '/api/search/history');
  }

  // ============================================
  // API v2.0 - WEBHOOKS
  // ============================================

  /**
   * List registered webhooks
   * @returns {Promise<{webhooks: object[]}>}
   */
  async getWebhooks() {
    return this._request('GET', '/api/webhooks');
  }

  /**
   * Register a webhook
   * @param {string} url - Webhook URL
   * @param {string[]} events - Events to subscribe to
   * @returns {Promise<{id: string, success: boolean}>}
   */
  async registerWebhook(url, events = ['download.complete', 'search.complete']) {
    return this._request('POST', '/api/webhooks', { url, events });
  }

  /**
   * Remove a webhook
   * @param {string} id - Webhook ID
   * @returns {Promise<{success: boolean}>}
   */
  async removeWebhook(id) {
    return this._request('DELETE', `/api/webhooks/${id}`);
  }
}

// Default export for convenience
export default NounProjectClient;

