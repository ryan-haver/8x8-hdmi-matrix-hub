/**
 * NounProject Icon Tool - REST API Server (Refactored)
 * Provides HTTP endpoints for external app integration
 * 
 * Architecture:
 * - Routes extracted to /routes/*.js
 * - State managed in lib/state.js
 * - Config managed by lib/config-service.js
 * - Security utilities in lib/security.js
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import rateLimit from 'express-rate-limit';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';

// Library imports
import Catalog from '../lib/catalog.js';
import ProxyPool from '../lib/proxy-pool.js';
import DownloadQueue from '../lib/download-queue.js';
import ApiClient from '../lib/api-client.js';
import ConfigService from '../lib/config-service.js';
import { getCorsConfig, validatePath } from '../lib/security.js';
import { SECURITY, WEBSOCKET } from '../lib/constants.js';
import { decrypt, isEncrypted } from '../lib/crypto-utils.js';

// State management
import * as state from '../lib/state.js';

// Route modules
import catalogRoutes from './routes/catalog.js';
import collectionsRoutes from './routes/collections.js';
import settingsRoutes from './routes/settings.js';
import searchRoutes from './routes/search.js';
import iconsRoutes, { iconTags } from './routes/icons.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());

// Rate limiting - configurable via constants
const limiter = rateLimit({
  windowMs: SECURITY.RATE_LIMIT_WINDOW,
  max: SECURITY.RATE_LIMIT_MAX,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later' },
  skip: (req) => req.path === '/api/health' // Skip health checks
});
app.use('/api', limiter);

// ============================================
// INITIALIZATION
// ============================================

async function initServices() {
  // Initialize catalog
  const catalog = new Catalog();
  await catalog.init();
  state.setCatalog(catalog);
  
  // Load config and initialize proxy pool
  const config = await ConfigService.get();
  
  if (config.proxy?.enabled || config.proxy?.pia?.username) {
    const pool = new ProxyPool({ strategy: config.proxy?.strategy || 'smart' });
    
    if (config.proxy?.pia?.username && config.proxy?.pia?.password) {
      const password = isEncrypted(config.proxy.pia.password) 
        ? decrypt(config.proxy.pia.password) 
        : config.proxy.pia.password;
      await pool.addPIA(config.proxy.pia.username, password);
    }
    
    if (config.proxy?.custom?.length) {
      pool.addAll(config.proxy.custom);
    }
    
    await pool.loadStats();
    state.setProxyPool(pool);
  }
  
  // Initialize singleton ApiClient with proxy pool
  const client = new ApiClient({ proxyPool: state.proxyPool });
  state.setApiClient(client);
  
  console.log('Services initialized');
}

// ============================================
// MIDDLEWARE
// ============================================

// CORS - configurable based on environment
app.use((req, res, next) => {
  const corsConfig = getCorsConfig();
  
  if (corsConfig.origin === '*') {
    res.header('Access-Control-Allow-Origin', '*');
  } else if (Array.isArray(corsConfig.origin)) {
    const requestOrigin = req.headers.origin;
    if (corsConfig.origin.includes(requestOrigin)) {
      res.header('Access-Control-Allow-Origin', requestOrigin);
    }
  }
  
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  
  next();
});

// ============================================
// HEALTH & STATS
// ============================================

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    version: '2.0.0',
    timestamp: new Date().toISOString(),
    services: {
      catalog: !!state.catalog,
      proxy: state.proxyPool?.hasProxies() || false,
      proxyCount: state.proxyPool?.count || 0
    }
  });
});

app.get('/api/stats', async (req, res) => {
  try {
    const catalogStats = state.catalog.getStats();
    
    let apiUsage = null;
    try {
      const client = new ApiClient({ proxyPool: state.proxyPool });
      apiUsage = await client.getUsage();
    } catch {
      // Ignore usage fetch errors
    }
    
    let proxyStats = null;
    if (state.proxyPool?.hasProxies()) {
      proxyStats = {
        enabled: true,
        count: state.proxyPool.count,
        strategy: state.proxyPool.strategy,
        usage: state.proxyPool.getStats()
      };
    }
    
    res.json({
      success: true,
      catalog: catalogStats,
      api: apiUsage,
      proxy: proxyStats,
      activeDownloads: state.activeDownloads.size
    });
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/usage', async (req, res) => {
  try {
    const client = new ApiClient({ proxyPool: state.proxyPool });
    const usage = await client.getUsage();
    
    res.json({
      success: true,
      usage: usage?.usage || 0,
      limit: usage?.limit || 0,
      remaining: (usage?.limit || 0) - (usage?.usage || 0),
      percentUsed: usage?.limit ? ((usage.usage / usage.limit) * 100).toFixed(2) : '0'
    });
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// MOUNT ROUTE MODULES
// ============================================

app.use('/api/catalog', catalogRoutes);
app.use('/api/collections', collectionsRoutes);
app.use('/api/settings', settingsRoutes);
app.use('/api/search', searchRoutes);
app.use('/api/icon', iconsRoutes);

// ============================================
// ADDITIONAL ENDPOINTS
// ============================================

// Tags listing
app.get('/api/tags', (req, res) => {
  const allTags = new Set();
  for (const tags of iconTags.values()) {
    tags.forEach(tag => allTags.add(tag));
  }
  res.json({ success: true, tags: Array.from(allTags) });
});

// Favorites listing
app.get('/api/favorites', (req, res) => {
  const icons = Array.from(state.favorites)
    .map(id => state.catalog.getIcon(id))
    .filter(Boolean);
  res.json({ success: true, count: icons.length, icons });
});

// Webhooks
app.get('/api/webhooks', (req, res) => {
  const list = Array.from(state.webhooks.entries()).map(([id, wh]) => ({
    id,
    url: wh.url,
    events: wh.events,
    createdAt: wh.createdAt
  }));
  res.json({ success: true, webhooks: list });
});

app.post('/api/webhooks', (req, res) => {
  try {
    const { url, events = ['download.complete'] } = req.body;
    
    if (!url) {
      return res.status(400).json({ error: 'Webhook URL required' });
    }
    
    // Validate URL format
    try {
      const parsed = new URL(url);
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        return res.status(400).json({ error: 'Webhook URL must use http or https protocol' });
      }
    } catch {
      return res.status(400).json({ error: 'Invalid webhook URL format' });
    }
    
    // Validate events array
    const validEvents = ['download.complete', 'download.failed', 'search.complete', 'catalog.update'];
    const invalidEvents = events.filter(e => !validEvents.includes(e));
    if (invalidEvents.length > 0) {
      return res.status(400).json({ 
        error: `Invalid event types: ${invalidEvents.join(', ')}`,
        validEvents 
      });
    }
    
    const id = crypto.randomUUID();
    state.webhooks.set(id, {
      url,
      events,
      createdAt: new Date().toISOString()
    });
    
    res.json({ success: true, id, message: 'Webhook registered' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/webhooks/:id', (req, res) => {
  const { id } = req.params;
  
  if (!state.webhooks.has(id)) {
    return res.status(404).json({ error: 'Webhook not found' });
  }
  
  state.webhooks.delete(id);
  res.json({ success: true, message: 'Webhook removed' });
});

// Download endpoints
app.post('/api/download', async (req, res) => {
  try {
    const { query, ids, outputDir = './icons', limit = 50 } = req.body;
    
    // Validate output path
    const pathCheck = validatePath(outputDir);
    if (!pathCheck.valid) {
      return res.status(400).json({ error: pathCheck.error });
    }
    
    const jobId = crypto.randomUUID();
    const client = new ApiClient({ proxyPool: state.proxyPool });
    const queue = new DownloadQueue(client);
    await queue.setOutputDir(pathCheck.resolved);
    
    state.activeDownloads.set(jobId, {
      status: 'running',
      query: query || null,
      queue,
      createdAt: new Date().toISOString()
    });
    
    let icons = [];
    if (ids && Array.isArray(ids)) {
      icons = ids.map(id => state.catalog.getIcon(id)).filter(Boolean);
    } else if (query) {
      const result = await client.search(query, { limit });
      icons = result.icons || [];
    }
    
    queue.addAll(icons);
    
    res.json({
      success: true,
      jobId,
      queued: icons.length
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/download/:jobId', (req, res) => {
  const { jobId } = req.params;
  const job = state.activeDownloads.get(jobId);
  
  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  res.json({
    success: true,
    status: job.status,
    progress: job.queue?.getProgress() || null
  });
});

// Config reload
app.post('/api/reload', async (req, res) => {
  try {
    const config = await ConfigService.reload();
    
    if (config.proxy?.enabled) {
      const pool = new ProxyPool({ strategy: config.proxy.strategy || 'smart' });
      
      const creds = await ConfigService.getPiaCredentials();
      if (creds) {
        await pool.addPIA(creds.username, creds.password);
      }
      
      if (config.proxy.custom?.length) {
        pool.addAll(config.proxy.custom);
      }
      
      await pool.loadStats();
      state.setProxyPool(pool);
    }
    
    res.json({ 
      success: true, 
      message: 'Configuration reloaded',
      proxy: {
        enabled: state.proxyPool?.hasProxies() || false,
        count: state.proxyPool?.count || 0
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Legacy endpoints - redirect to new settings routes
app.get('/api/proxy', (req, res) => res.redirect(301, '/api/settings/proxy'));
app.post('/api/proxy', (req, res, next) => { req.url = '/api/settings/proxy'; settingsRoutes(req, res, next); });
app.delete('/api/proxy', (req, res, next) => { req.url = '/api/settings/proxy'; settingsRoutes(req, res, next); });
app.post('/api/config', (req, res, next) => { req.url = '/api/settings'; settingsRoutes(req, res, next); });

// Serve static files for web UI
app.use(express.static(path.join(__dirname, 'public')));

// ============================================
// START SERVER
// ============================================

const PORT = process.env.PORT || 3000;

async function start() {
  await initServices();
  
  const server = app.listen(PORT, () => {
    console.log(`\n🎨 NounProject Icon Tool API v2.0`);
    console.log(`   REST API: http://localhost:${PORT}/api`);
    console.log(`   Web UI:   http://localhost:${PORT}`);
    console.log('');
  });
  
  // WebSocket for real-time updates
  const wss = new WebSocketServer({ server, path: WEBSOCKET.PATH });
  
  wss.on('connection', (ws) => {
    console.log('WebSocket client connected');
    ws.on('close', () => console.log('WebSocket client disconnected'));
  });
  
  // Broadcast download progress (only when clients connected)
  setInterval(() => {
    if (wss.clients.size === 0) return; // Skip if no clients
    
    const updates = [];
    for (const [jobId, job] of state.activeDownloads) {
      if (job.status === 'running' && job.queue) {
        updates.push({ jobId, progress: job.queue.getProgress() });
      }
    }
    
    if (updates.length > 0) {
      const message = JSON.stringify({ type: 'progress', downloads: updates });
      wss.clients.forEach(client => {
        if (client.readyState === 1) client.send(message);
      });
    }
  }, WEBSOCKET.POLL_INTERVAL);
  
  // Periodic cleanup of stale downloads (every 5 minutes)
  setInterval(() => {
    const cleaned = state.cleanupDownloads();
    if (cleaned > 0) {
      console.log(`[Cleanup] Removed ${cleaned} stale download job(s)`);
    }
  }, 5 * 60 * 1000);
  
  // Graceful shutdown
  process.on('SIGINT', () => {
    console.log('\nShutting down...');
    state.catalog?.close();
    server.close();
    process.exit(0);
  });
}

start();
