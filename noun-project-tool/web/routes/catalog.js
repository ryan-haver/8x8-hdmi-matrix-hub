/**
 * Catalog Routes
 * Handles catalog management, export, and icon retrieval
 */

import { Router } from 'express';
import * as state from '../../lib/state.js';
import { validatePath } from '../../lib/security.js';

const router = Router();

/**
 * GET /api/catalog
 * Get icons from local catalog
 */
router.get('/', (req, res) => {
  try {
    const { q = '', limit = 100, offset = 0, downloaded } = req.query;
    
    const icons = state.catalog.search(q, {
      limit: parseInt(limit),
      offset: parseInt(offset),
      downloadedOnly: downloaded === 'true'
    });
    
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
 * GET /api/catalog/export
 * Export catalog as JSON or CSV
 */
router.get('/export', (req, res) => {
  try {
    const format = req.query.format || 'json';
    const icons = state.catalog.getAll();
    
    if (format === 'csv') {
      const headers = ['id', 'term', 'creator', 'iconUrl', 'downloaded', 'tags'];
      const rows = icons.map(icon => [
        icon.id,
        icon.term || '',
        icon.creator || '',
        icon.iconUrl || '',
        icon.downloaded ? 'true' : 'false',
        (icon.tags || []).join(';')
      ]);
      const csv = [headers.join(','), ...rows.map(r => r.map(v => `"${v}"`).join(','))].join('\n');
      
      res.type('text/csv');
      res.attachment('catalog.csv');
      return res.send(csv);
    }
    
    res.json({ success: true, count: icons.length, icons });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/catalog/clear
 * Clear entire catalog
 */
router.delete('/clear', async (req, res) => {
  try {
    const { confirm } = req.query;
    
    if (confirm !== 'yes') {
      return res.status(400).json({ error: 'Add ?confirm=yes to clear catalog' });
    }
    
    await state.catalog.clear();
    res.json({ success: true, message: 'Catalog cleared' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/catalog/:id
 * Get a specific icon from catalog
 */
router.get('/:id', (req, res) => {
  try {
    const icon = state.catalog.getIcon(req.params.id);
    
    if (!icon) {
      return res.status(404).json({ error: 'Icon not found' });
    }
    
    res.json({ success: true, icon });
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/catalog/batch
 * Add multiple icons to catalog
 */
router.post('/batch', async (req, res) => {
  try {
    const { icons } = req.body;
    
    if (!icons || !Array.isArray(icons)) {
      return res.status(400).json({ error: 'icons array required' });
    }
    
    let added = 0;
    for (const icon of icons) {
      if (icon.id) {
        state.catalog.addIcon(icon);
        added++;
      }
    }
    
    await state.catalog.save();
    res.json({ success: true, added, total: state.catalog.getStats().totalIcons });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/catalog/import
 * Import catalog data (merge or replace)
 */
router.post('/import', async (req, res) => {
  try {
    const { icons, merge = true } = req.body;
    
    if (!icons || !Array.isArray(icons)) {
      return res.status(400).json({ error: 'icons array required' });
    }
    
    if (!merge) {
      await state.catalog.clear();
    }
    
    let imported = 0;
    for (const icon of icons) {
      if (icon.id) {
        state.catalog.addIcon(icon);
        imported++;
      }
    }
    
    await state.catalog.save();
    res.json({ success: true, imported, total: state.catalog.getStats().totalIcons });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/catalog/:id
 * Remove single icon from catalog
 */
router.delete('/:id', async (req, res) => {
  try {
    const deleted = state.catalog.deleteIcon(req.params.id);
    
    if (!deleted) {
      return res.status(404).json({ error: 'Icon not found' });
    }
    
    await state.catalog.save();
    res.json({ success: true, message: 'Icon deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
