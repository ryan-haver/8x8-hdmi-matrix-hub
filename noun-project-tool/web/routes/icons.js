/**
 * Icon Routes
 * Handles individual icon operations (tags, favorites, SVG/PNG)
 */

import { Router } from 'express';
import sharp from 'sharp';
import * as state from '../../lib/state.js';
import ApiClient from '../../lib/api-client.js';

const router = Router();

// In-memory tag storage (per icon)
const iconTags = new Map();

/**
 * Get or create ApiClient (uses singleton if available)
 */
function getClient() {
  return state.getApiClient() || new ApiClient({ proxyPool: state.proxyPool });
}

/**
 * GET /api/icon/:id
 * Get full icon with SVG content
 */
router.get('/:id', async (req, res) => {
  try {
    const icon = state.catalog.getIcon(req.params.id);
    
    if (!icon) {
      return res.status(404).json({ error: 'Icon not found' });
    }
    
    let svg = null;
    if (icon.iconUrl) {
      try {
        const client = getClient();
        svg = await client.downloadSvg(icon.iconUrl);
      } catch {
        // SVG fetch failed, continue without it
      }
    }
    
    res.json({ success: true, icon, svg });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/icon/:id/svg
 * Get raw SVG content
 */
router.get('/:id/svg', async (req, res) => {
  try {
    const icon = state.catalog.getIcon(req.params.id);
    if (!icon) {
      return res.status(404).json({ error: 'Icon not found' });
    }
    
    if (!icon.iconUrl) {
      return res.status(404).json({ error: 'Icon has no SVG URL' });
    }
    
    const client = getClient();
    const svg = await client.downloadSvg(icon.iconUrl);
    
    res.type('image/svg+xml');
    res.send(svg);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/icon/:id/png
 * Get PNG at specified size
 */
router.get('/:id/png', async (req, res) => {
  try {
    const icon = state.catalog.getIcon(req.params.id);
    if (!icon) {
      return res.status(404).json({ error: 'Icon not found' });
    }
    
    if (!icon.iconUrl) {
      return res.status(404).json({ error: 'Icon has no SVG URL' });
    }
    
    const size = parseInt(req.query.size) || 64;
    const client = getClient();
    const svg = await client.downloadSvg(icon.iconUrl);
    
    const png = await sharp(Buffer.from(svg))
      .resize(size, size)
      .png()
      .toBuffer();
    
    res.type('image/png');
    res.send(png);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/icon/:id/tags
 * Get tags for an icon
 */
router.get('/:id/tags', (req, res) => {
  const { id } = req.params;
  const tags = iconTags.get(id) || [];
  res.json({ success: true, tags });
});

/**
 * POST /api/icon/:id/tags
 * Add tag to icon
 */
router.post('/:id/tags', (req, res) => {
  try {
    const { id } = req.params;
    const { tag } = req.body;
    
    if (!tag) {
      return res.status(400).json({ error: 'Tag is required' });
    }
    
    let tags = iconTags.get(id);
    if (!tags) {
      tags = [];
      iconTags.set(id, tags);
    }
    
    if (!tags.includes(tag)) {
      tags.push(tag);
    }
    
    res.json({ success: true, tags });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/icon/:id/tags/:tag
 * Remove tag from icon
 */
router.delete('/:id/tags/:tag', (req, res) => {
  const { id, tag } = req.params;
  
  const tags = iconTags.get(id);
  if (!tags) {
    return res.status(404).json({ error: 'Icon has no tags' });
  }
  
  const index = tags.indexOf(tag);
  if (index === -1) {
    return res.status(404).json({ error: 'Tag not found' });
  }
  
  tags.splice(index, 1);
  res.json({ success: true, tags });
});

/**
 * POST /api/icon/:id/favorite
 * Mark icon as favorite
 */
router.post('/:id/favorite', (req, res) => {
  const { id } = req.params;
  state.favorites.add(id);
  res.json({ success: true, message: 'Added to favorites' });
});

/**
 * DELETE /api/icon/:id/favorite
 * Remove icon from favorites
 */
router.delete('/:id/favorite', (req, res) => {
  const { id } = req.params;
  state.favorites.delete(id);
  res.json({ success: true, message: 'Removed from favorites' });
});

export default router;

// Export iconTags for use in /api/tags endpoint
export { iconTags };
