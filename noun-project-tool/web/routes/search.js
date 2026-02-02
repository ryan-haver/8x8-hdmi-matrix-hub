/**
 * Search Routes
 * Handles icon search and search history
 */

import { Router } from 'express';
import * as state from '../../lib/state.js';
import ApiClient from '../../lib/api-client.js';

const router = Router();

/**
 * Get or create ApiClient (uses singleton if available)
 */
function getClient() {
  return state.getApiClient() || new ApiClient({ proxyPool: state.proxyPool });
}

/**
 * GET /api/search
 * Search for icons via the upstream API
 */
router.get('/', async (req, res) => {
  try {
    const { q, limit = 30, style, page } = req.query;
    
    if (!q) {
      return res.status(400).json({ error: 'Query parameter "q" is required' });
    }
    
    const client = getClient();
    const result = await client.search(q, {
      limit: parseInt(limit),
      style,
      nextPage: page
    });
    
    // Track search history
    if (state.searchHistory.length >= 100) {
      state.searchHistory.shift(); // Keep last 100
    }
    state.searchHistory.push({ 
      query: q, 
      timestamp: new Date().toISOString(), 
      resultCount: result.icons.length 
    });
    
    res.json({
      success: true,
      query: q,
      total: result.total,
      icons: result.icons,
      nextPage: result.nextPage,
      usage: result.usage
    });
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/search/save
 * Search and save results to catalog
 */
router.post('/save', async (req, res) => {
  try {
    const { query, limit = 50, style } = req.body;
    
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }
    
    const client = getClient();
    const result = await client.search(query, { limit: parseInt(limit), style });
    
    // Save to catalog
    const icons = result.icons || [];
    for (const icon of icons) {
      state.catalog.saveIcon(icon, query);
    }
    
    // Log search
    state.catalog.logSearch(query, result.total, icons.length);
    
    res.json({
      success: true,
      count: icons.length,
      icons
    });
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/search/history
 * Get search history
 */
router.get('/history', (req, res) => {
  const { limit = 50 } = req.query;
  const history = state.searchHistory.slice(-parseInt(limit)).reverse();
  res.json({ success: true, history });
});

/**
 * DELETE /api/search/history
 * Clear search history
 */
router.delete('/history', (req, res) => {
  state.searchHistory.length = 0;
  res.json({ success: true, message: 'Search history cleared' });
});

export default router;
