/**
 * Collections Routes
 * Handles user collections management
 */

import { Router } from 'express';
import * as state from '../../lib/state.js';
import DownloadQueue from '../../lib/download-queue.js';
import ApiClient from '../../lib/api-client.js';
import crypto from 'crypto';

const router = Router();

/**
 * GET /api/collections
 * List all collections
 */
router.get('/', (req, res) => {
  const list = Array.from(state.collections.entries()).map(([name, col]) => ({
    name,
    description: col.description,
    iconCount: col.icons.length
  }));
  res.json({ success: true, collections: list });
});

/**
 * POST /api/collections
 * Create a new collection
 */
router.post('/', (req, res) => {
  try {
    const { name, description = '' } = req.body;
    
    if (!name) {
      return res.status(400).json({ error: 'Collection name required' });
    }
    
    if (state.collections.has(name)) {
      return res.status(409).json({ error: 'Collection already exists' });
    }
    
    state.collections.set(name, {
      description,
      icons: [],
      createdAt: new Date().toISOString()
    });
    
    res.json({ success: true, message: 'Collection created' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/collections/:name
 * Get a collection with its icons
 */
router.get('/:name', (req, res) => {
  const { name } = req.params;
  const collection = state.collections.get(name);
  
  if (!collection) {
    return res.status(404).json({ error: 'Collection not found' });
  }
  
  // Get full icon data for each icon in collection
  const icons = collection.icons
    .map(id => state.catalog.getIcon(id))
    .filter(Boolean);
  
  res.json({
    success: true,
    name,
    description: collection.description,
    createdAt: collection.createdAt,
    icons
  });
});

/**
 * PUT /api/collections/:name
 * Update collection metadata
 */
router.put('/:name', (req, res) => {
  const { name } = req.params;
  const collection = state.collections.get(name);
  
  if (!collection) {
    return res.status(404).json({ error: 'Collection not found' });
  }
  
  const { description } = req.body;
  if (description !== undefined) collection.description = description;
  
  res.json({ success: true, message: 'Collection updated' });
});

/**
 * DELETE /api/collections/:name
 * Delete a collection
 */
router.delete('/:name', (req, res) => {
  const { name } = req.params;
  
  if (!state.collections.has(name)) {
    return res.status(404).json({ error: 'Collection not found' });
  }
  
  state.collections.delete(name);
  res.json({ success: true, message: 'Collection deleted' });
});

/**
 * POST /api/collections/:name/icons
 * Add icons to a collection
 */
router.post('/:name/icons', (req, res) => {
  try {
    const { name } = req.params;
    const { iconIds } = req.body;
    
    const collection = state.collections.get(name);
    if (!collection) {
      return res.status(404).json({ error: 'Collection not found' });
    }
    
    if (!iconIds || !Array.isArray(iconIds)) {
      return res.status(400).json({ error: 'iconIds array required' });
    }
    
    let added = 0;
    for (const id of iconIds) {
      if (!collection.icons.includes(id)) {
        collection.icons.push(id);
        added++;
      }
    }
    
    res.json({ success: true, added, total: collection.icons.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/collections/:name/icons/:id
 * Remove icon from collection
 */
router.delete('/:name/icons/:id', (req, res) => {
  const { name, id } = req.params;
  
  const collection = state.collections.get(name);
  if (!collection) {
    return res.status(404).json({ error: 'Collection not found' });
  }
  
  const index = collection.icons.indexOf(id);
  if (index === -1) {
    return res.status(404).json({ error: 'Icon not in collection' });
  }
  
  collection.icons.splice(index, 1);
  res.json({ success: true, message: 'Icon removed from collection' });
});

/**
 * POST /api/collections/:name/download
 * Download all icons in a collection
 */
router.post('/:name/download', async (req, res) => {
  try {
    const { name } = req.params;
    const { outputDir = './icons' } = req.body;
    
    const collection = state.collections.get(name);
    if (!collection) {
      return res.status(404).json({ error: 'Collection not found' });
    }
    
    // Get icons to download
    const icons = collection.icons
      .map(id => state.catalog.getIcon(id))
      .filter(icon => icon && icon.iconUrl);
    
    if (icons.length === 0) {
      return res.status(400).json({ error: 'No downloadable icons in collection' });
    }
    
    // Create download job
    const jobId = crypto.randomUUID();
    const client = new ApiClient({ proxyPool: state.proxyPool });
    const queue = new DownloadQueue(client);
    await queue.setOutputDir(outputDir);
    
    state.activeDownloads.set(jobId, {
      status: 'running',
      collection: name,
      queue
    });
    
    queue.addAll(icons);
    
    res.json({
      success: true,
      jobId,
      queued: icons.length,
      message: `Downloading ${icons.length} icons from collection "${name}"`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
