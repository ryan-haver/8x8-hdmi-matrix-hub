/**
 * Settings Routes
 * Handles configuration, proxy, and PIA credential management
 */

import { Router } from 'express';
import * as state from '../../lib/state.js';
import ConfigService from '../../lib/config-service.js';
import ProxyPool from '../../lib/proxy-pool.js';

const router = Router();

// Helper to add deprecation headers
function deprecated(res, successor) {
  res.setHeader('Deprecation', 'true');
  res.setHeader('Sunset', '2026-06-01');
  res.setHeader('Link', `<${successor}>; rel="successor-version"`);
}

/**
 * GET /api/settings
 * Get all current settings (sanitized)
 */
router.get('/', async (req, res) => {
  try {
    const settings = await ConfigService.getSanitized();
    res.json({ success: true, settings });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * PUT /api/settings
 * Update settings (partial merge)
 */
router.put('/', async (req, res) => {
  try {
    const { proxy, outputDir } = req.body;
    const updates = {};
    
    if (proxy) updates.proxy = proxy;
    if (outputDir) updates.outputDir = outputDir;
    
    await ConfigService.set(updates);
    
    // Apply to running instance
    if (state.proxyPool && proxy?.strategy) {
      state.proxyPool.strategy = proxy.strategy;
    }
    
    res.json({ success: true, message: 'Settings updated' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/settings/proxy
 * Get proxy configuration
 */
router.get('/proxy', async (req, res) => {
  try {
    const config = await ConfigService.get();
    const piaUsername = config.proxy?.pia?.username || null;
    const piaConfigured = !!(piaUsername && config.proxy?.pia?.password);
    
    res.json({
      success: true,
      proxy: {
        enabled: state.proxyPool?.hasProxies() || false,
        count: state.proxyPool?.count || 0,
        strategy: state.proxyPool?.strategy || 'smart',
        stats: state.proxyPool?.getStats() || [],
        piaConfigured,
        piaUsername
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * PUT /api/settings/proxy
 * Update proxy settings
 */
router.put('/proxy', async (req, res) => {
  try {
    const { strategy } = req.body;
    
    if (strategy && state.proxyPool) {
      state.proxyPool.strategy = strategy;
    }
    
    await ConfigService.set({ proxy: { strategy } });
    
    res.json({ 
      success: true, 
      message: 'Proxy settings updated',
      strategy: state.proxyPool?.strategy
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/settings/proxy/stats
 * Reset all proxy usage statistics
 */
router.delete('/proxy/stats', async (req, res) => {
  try {
    if (state.proxyPool) {
      for (const proxy of state.proxyPool.proxies) {
        state.proxyPool.usageMap.set(proxy, { success: 0, failure: 0, lastUsed: null, lastError: null });
      }
      await state.proxyPool.saveStats();
    }
    
    res.json({ success: true, message: 'Proxy statistics reset' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/settings/pia
 * Get PIA configuration status
 */
router.get('/pia', async (req, res) => {
  try {
    const config = await ConfigService.get();
    const piaConfig = {
      configured: !!(config.proxy?.pia?.username && config.proxy?.pia?.password),
      username: config.proxy?.pia?.username || null
    };
    
    res.json({ success: true, pia: piaConfig });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * PUT /api/settings/pia
 * Set PIA credentials
 */
router.put('/pia', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }
    
    // Initialize or update proxy pool
    let pool = state.proxyPool;
    if (!pool) {
      pool = new ProxyPool({ strategy: 'smart' });
      state.setProxyPool(pool);
    }
    
    await pool.addPIA(username, password);
    await ConfigService.savePiaCredentials(username, password);
    
    res.json({ 
      success: true, 
      message: 'PIA credentials saved',
      proxies: pool.count
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/settings/pia
 * Remove PIA credentials
 */
router.delete('/pia', async (req, res) => {
  try {
    await ConfigService.removePiaCredentials();
    
    if (state.proxyPool) {
      state.proxyPool.clear();
    }
    
    res.json({ success: true, message: 'PIA credentials removed' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// LEGACY ENDPOINTS (Deprecated)
// ============================================

/**
 * GET /api/proxy (DEPRECATED)
 * Use GET /api/settings/proxy instead
 */
router.get('/legacy/proxy', async (req, res) => {
  deprecated(res, '/api/settings/proxy');
  
  const config = await ConfigService.get();
  const piaConfigured = !!(config.proxy?.pia?.username && config.proxy?.pia?.password);
  
  if (!state.proxyPool?.hasProxies()) {
    return res.json({ 
      success: true, 
      enabled: false, 
      proxies: [], 
      piaConfigured,
      _deprecated: 'Use /api/settings/proxy'
    });
  }
  
  res.json({
    success: true,
    enabled: true,
    count: state.proxyPool.count,
    strategy: state.proxyPool.strategy,
    proxies: state.proxyPool.getStats(),
    piaConfigured,
    _deprecated: 'Use /api/settings/proxy'
  });
});

/**
 * POST /api/config (DEPRECATED)
 * Use PUT /api/settings instead
 */
router.post('/legacy/config', async (req, res) => {
  deprecated(res, '/api/settings');
  
  try {
    const { proxyStrategy, outputDir } = req.body;
    
    if (proxyStrategy && state.proxyPool) {
      state.proxyPool.strategy = proxyStrategy;
    }
    
    await ConfigService.set({
      proxy: proxyStrategy ? { strategy: proxyStrategy } : undefined,
      outputDir
    });
    
    res.json({ 
      success: true, 
      _deprecated: 'Use PUT /api/settings'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
