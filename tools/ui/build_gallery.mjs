#!/usr/bin/env node
// Build the UI review gallery from the visual baselines (docs/REMEDIATION_PLAN.md §5.3).
//
//   node tools/ui/build_gallery.mjs                       walkthrough of the current baselines
//   node tools/ui/build_gallery.mjs --base origin/main    before/after review against a git ref
//   node tools/ui/build_gallery.mjs --base HEAD           uncommitted baseline changes (e.g. after visual:update)
//
// Options:
//   --base <ref>        compare the working-tree baselines with the baselines at <ref>
//   --changed-only      (with --base) only include entries that differ
//   --out <dir>         output directory (default ui-gallery/)
//   --thumb <px>        thumbnail width (default 360)
//
// Output (ui-gallery/ is gitignored):
//   index.html          one self-contained page: thumbnails inlined (WebP), grouped by catalog
//                       entry with viewport/theme tabs, a filter box, before/after/diff in
//                       compare mode. Click a thumbnail to enlarge.
//   full/*.webp         full-size images for click-to-enlarge (referenced relatively; the page
//                       falls back to the inlined thumbnail when they are missing)
//   changed.json        (compare mode) machine-readable list of changed images and entries
//
// Baselines are in Git LFS; run `git lfs pull` first if the PNGs are pointer files.
import { execFileSync, spawnSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import pixelmatch from 'pixelmatch';
import { PNG } from 'pngjs';
import sharp from 'sharp';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const SNAP_REL = 'tests/e2e/visual/__snapshots__';
const SNAP_DIR = path.join(ROOT, SNAP_REL);
const VIEWPORT_ORDER = ['desktop', 'tablet', 'phone', 'kiosk'];
const THEME_ORDER = ['tron-classic', 'neon', 'royal', 'vaporwave'];
const LFS_POINTER = Buffer.from('version https://git-lfs');

// --- args --------------------------------------------------------------------
const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : fallback;
};
const baseRef = opt('--base', null);
const changedOnly = args.includes('--changed-only');
const outDir = path.resolve(ROOT, opt('--out', 'ui-gallery'));
const thumbWidth = Number(opt('--thumb', 360));

// --- load image sets ---------------------------------------------------------
function git(argv, input) {
  return execFileSync('git', argv, { cwd: ROOT, input, maxBuffer: 256 * 1024 * 1024 });
}

function smudgeIfPointer(buf, where) {
  if (!buf.subarray(0, LFS_POINTER.length).equals(LFS_POINTER)) return buf;
  const r = spawnSync('git', ['lfs', 'smudge'], { cwd: ROOT, input: buf, maxBuffer: 256 * 1024 * 1024 });
  if (r.status !== 0 || r.stdout.subarray(0, LFS_POINTER.length).equals(LFS_POINTER)) {
    throw new Error(`${where} is a Git LFS pointer and the object is not available; run: git lfs fetch --all (or git lfs pull)`);
  }
  return r.stdout;
}

/** key -> Buffer, key = path relative to __snapshots__ with forward slashes. */
function loadWorkingTree() {
  const out = new Map();
  const walk = (dir) => {
    if (!fs.existsSync(dir)) return;
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) walk(full);
      else if (e.name.endsWith('.png')) {
        const key = path.relative(SNAP_DIR, full).split(path.sep).join('/');
        out.set(key, smudgeIfPointer(fs.readFileSync(full), full));
      }
    }
  };
  walk(SNAP_DIR);
  return out;
}

function loadRef(ref) {
  const out = new Map();
  const list = git(['ls-tree', '-r', '--name-only', ref, '--', SNAP_REL]).toString().split('\n').filter(Boolean);
  for (const file of list) {
    if (!file.endsWith('.png')) continue;
    const blob = git(['cat-file', 'blob', `${ref}:${file}`]);
    out.set(file.slice(SNAP_REL.length + 1), smudgeIfPointer(blob, `${ref}:${file}`));
  }
  return out;
}

function loadManifest(ref) {
  try {
    const text = ref
      ? git(['show', `${ref}:${SNAP_REL}/catalog.json`]).toString()
      : fs.readFileSync(path.join(SNAP_DIR, 'catalog.json'), 'utf8');
    return JSON.parse(text);
  } catch {
    return { entries: [] };
  }
}

/** "desktop/themes/neon/matrix/grid/default.png" -> {viewport, theme, entry} */
function parseKey(key) {
  const parts = key.replace(/\.png$/, '').split('/');
  const viewport = parts.shift();
  let theme = 'tron-classic';
  if (parts[0] === 'themes') {
    parts.shift();
    theme = parts.shift();
  }
  return { viewport, theme, entry: parts.join('/') };
}

// --- image processing --------------------------------------------------------
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(path.join(outDir, 'full'), { recursive: true });

async function thumb(buf) {
  const b = await sharp(buf).resize({ width: thumbWidth, withoutEnlargement: true }).webp({ quality: 62 }).toBuffer();
  return `data:image/webp;base64,${b.toString('base64')}`;
}

async function full(buf) {
  const name = `${crypto.createHash('sha1').update(buf).digest('hex').slice(0, 16)}.webp`;
  const file = path.join(outDir, 'full', name);
  if (!fs.existsSync(file)) await sharp(buf).webp({ quality: 82 }).toFile(file);
  return `full/${name}`;
}

/** Pixel diff: returns {pixels, image} with changed pixels in red over a dimmed "after". */
function diff(beforeBuf, afterBuf) {
  const a = PNG.sync.read(beforeBuf);
  const b = PNG.sync.read(afterBuf);
  if (a.width !== b.width || a.height !== b.height) {
    return { pixels: Math.max(a.width * a.height, b.width * b.height), sizeChanged: `${a.width}x${a.height} -> ${b.width}x${b.height}`, image: null };
  }
  const out = new PNG({ width: a.width, height: a.height });
  const pixels = pixelmatch(a.data, b.data, out.data, a.width, a.height, {
    threshold: 0.1,
    alpha: 0.25,
    diffColor: [255, 0, 64],
    diffColorAlt: [0, 200, 255],
  });
  return { pixels, image: PNG.sync.write(out) };
}

// --- build -------------------------------------------------------------------
const current = loadWorkingTree();
const base = baseRef ? loadRef(baseRef) : null;
const manifest = loadManifest(null);
const baseManifest = baseRef ? loadManifest(baseRef) : { entries: [] };
const meta = new Map([...baseManifest.entries, ...manifest.entries].map((e) => [e.name, e]));

const keys = new Set([...current.keys(), ...(base ? base.keys() : [])]);
const entries = new Map(); // entry name -> {name, meta, shots: []}
const changed = [];
let totalBytes = 0;

for (const key of [...keys].sort()) {
  const { viewport, theme, entry } = parseKey(key);
  const after = current.get(key) ?? null;
  const before = base ? (base.get(key) ?? null) : null;
  let status = 'baseline';
  let d = null;
  if (base) {
    if (!before) status = 'added';
    else if (!after) status = 'removed';
    else if (before.equals(after)) status = 'unchanged';
    else {
      d = diff(before, after);
      status = d.pixels === 0 ? 'unchanged' : 'changed';
    }
  }
  if (base && status !== 'unchanged') changed.push({ entry, viewport, theme, status, diffPixels: d?.pixels ?? null, sizeChanged: d?.sizeChanged ?? null });
  if (changedOnly && status === 'unchanged') continue;

  const shot = { key, viewport, theme, status, diffPixels: d?.pixels ?? null, sizeChanged: d?.sizeChanged ?? null };
  if (after) {
    shot.after = { thumb: await thumb(after), full: await full(after) };
    totalBytes += after.length;
  }
  if (before && status !== 'unchanged') shot.before = { thumb: await thumb(before), full: await full(before) };
  if (d?.image) shot.diff = { thumb: await thumb(d.image), full: await full(d.image) };
  if (!entries.has(entry)) entries.set(entry, { name: entry, meta: meta.get(entry) ?? null, shots: [] });
  entries.get(entry).shots.push(shot);
}

// Catalog entries that have no images at all (e.g. "not capturable").
for (const e of manifest.entries) {
  if (!entries.has(e.name) && !changedOnly) entries.set(e.name, { name: e.name, meta: e, shots: [] });
}

const list = [...entries.values()].sort((a, b) => a.name.localeCompare(b.name));
for (const e of list) {
  e.shots.sort(
    (a, b) =>
      THEME_ORDER.indexOf(a.theme) - THEME_ORDER.indexOf(b.theme) || VIEWPORT_ORDER.indexOf(a.viewport) - VIEWPORT_ORDER.indexOf(b.viewport),
  );
  e.changed = e.shots.some((s) => s.status !== 'unchanged' && s.status !== 'baseline');
}

const changedEntries = [...new Set(changed.map((c) => c.entry))].sort();
if (base) {
  fs.writeFileSync(
    path.join(outDir, 'changed.json'),
    `${JSON.stringify({ base: baseRef, changedEntries, images: changed }, null, 2)}\n`,
  );
}

const data = {
  title: base ? `UI review: ${changedEntries.length} changed entr${changedEntries.length === 1 ? 'y' : 'ies'} vs ${baseRef}` : 'UI baseline gallery',
  compare: !!base,
  baseRef,
  generated: new Date().toISOString(),
  imageCount: [...current.keys()].length,
  entryCount: list.length,
  changedEntries,
  entries: list,
};

fs.writeFileSync(path.join(outDir, 'index.html'), renderHtml(data));
const htmlSize = fs.statSync(path.join(outDir, 'index.html')).size;
console.log(
  `[gallery] ${data.entryCount} entries, ${data.imageCount} images (${(totalBytes / 1e6).toFixed(1)} MB PNG)` +
    (base ? `, ${changedEntries.length} changed entries / ${changed.length} images vs ${baseRef}` : '') +
    `\n[gallery] ${path.relative(ROOT, path.join(outDir, 'index.html'))} (${(htmlSize / 1e6).toFixed(1)} MB) + full/`,
);

// --- HTML --------------------------------------------------------------------
function renderHtml(data) {
  const json = JSON.stringify(data).replace(/</g, '\\u003c');
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${data.compare ? 'UI Review' : 'UI Baseline Gallery'}</title>
<style>
:root { --bg:#0b0f15; --panel:#131a24; --line:#243042; --text:#e8eef5; --muted:#8a9bb0; --accent:#22d3ee; --add:#34d399; --del:#f87171; --chg:#fbbf24; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:14px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
header { position:sticky; top:0; z-index:5; background:rgba(11,15,21,.96); border-bottom:1px solid var(--line); padding:12px 16px; display:flex; flex-wrap:wrap; gap:10px 16px; align-items:center; }
h1 { font-size:16px; margin:0; font-weight:600; }
.meta { color:var(--muted); font-size:12px; }
input[type=search] { background:var(--panel); color:var(--text); border:1px solid var(--line); border-radius:8px; padding:7px 10px; min-width:260px; flex:1; max-width:420px; }
label.chk { color:var(--muted); font-size:13px; display:flex; gap:6px; align-items:center; }
main { padding:16px; max-width:1800px; margin:0 auto; }
.group { margin:0 0 28px; }
.group > h2 { font-size:13px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin:0 0 10px; border-bottom:1px solid var(--line); padding-bottom:6px; }
.entries { display:grid; grid-template-columns:repeat(auto-fill, minmax(380px, 1fr)); gap:14px; }
.entry { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:12px; display:flex; flex-direction:column; gap:8px; }
.entry.changed { border-color:var(--chg); }
.entry h3 { margin:0; font:600 13px/1.3 ui-monospace, SFMono-Regular, Consolas, monospace; word-break:break-all; }
.desc { color:var(--muted); font-size:12.5px; margin:0; }
.note { font-size:12px; margin:0; padding:6px 8px; border-left:3px solid var(--chg); background:rgba(251,191,36,.07); color:#f3dfa6; }
.tabs { display:flex; flex-wrap:wrap; gap:4px; }
.tabs button { background:transparent; color:var(--muted); border:1px solid var(--line); border-radius:6px; padding:2px 8px; font-size:12px; cursor:pointer; }
.tabs button.on { color:var(--bg); background:var(--accent); border-color:var(--accent); }
.tabs button.chg::after { content:" \\25CF"; color:var(--chg); }
.tabs button.on.chg::after { color:#7c2d12; }
.shots { display:grid; gap:6px; }
.shots.cmp { grid-template-columns:repeat(3, 1fr); }
figure { margin:0; }
figure img { width:100%; display:block; border-radius:6px; border:1px solid var(--line); cursor:zoom-in; background:#000; }
figcaption { font-size:11px; color:var(--muted); margin-top:2px; }
.badge { display:inline-block; font-size:11px; border-radius:999px; padding:0 7px; margin-left:6px; vertical-align:middle; }
.b-changed { background:rgba(251,191,36,.18); color:var(--chg); }
.b-added { background:rgba(52,211,153,.15); color:var(--add); }
.b-removed { background:rgba(248,113,113,.15); color:var(--del); }
.empty { color:var(--muted); font-size:12px; font-style:italic; }
#lightbox { position:fixed; inset:0; background:rgba(0,0,0,.92); display:none; z-index:10; flex-direction:column; }
#lightbox.on { display:flex; }
#lightbox .bar { display:flex; gap:8px; align-items:center; padding:10px 14px; color:var(--muted); font-size:13px; }
#lightbox .bar .tabs { margin-left:auto; }
#lightbox .view { flex:1; overflow:auto; display:flex; justify-content:center; align-items:flex-start; padding:0 12px 12px; }
#lightbox img { max-width:100%; height:auto; border:1px solid var(--line); cursor:zoom-out; }
#lightbox img.natural { max-width:none; }
@media (max-width:600px) { .entries { grid-template-columns:1fr; } .shots.cmp { grid-template-columns:1fr; } input[type=search] { min-width:0; } }
</style>
</head>
<body>
<header>
  <h1 id="title"></h1>
  <span class="meta" id="summary"></span>
  <input type="search" id="filter" placeholder="Filter entries (e.g. drawer/theme, kiosk, long-names)" autocomplete="off">
  <label class="chk" id="changed-wrap" hidden><input type="checkbox" id="only-changed"> changed only</label>
</header>
<main id="main"></main>
<div id="lightbox" role="dialog" aria-modal="true">
  <div class="bar"><span id="lb-title"></span><div class="tabs" id="lb-tabs"></div><button id="lb-close" class="tabs" style="background:none;border:0;color:var(--text);font-size:20px;cursor:pointer" aria-label="Close">&times;</button></div>
  <div class="view"><img id="lb-img" alt=""></div>
</div>
<script id="data" type="application/json">${json}</script>
<script>
(() => {
  const data = JSON.parse(document.getElementById('data').textContent);
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  $('#title').textContent = data.title;
  $('#summary').textContent = data.entryCount + ' entries · ' + data.imageCount + ' images' + (data.compare ? ' · base ' + data.baseRef : '') + ' · generated ' + data.generated.slice(0, 16).replace('T', ' ') + ' UTC';
  if (data.compare) { $('#changed-wrap').hidden = false; $('#only-changed').checked = data.changedEntries.length > 0; }

  const groups = new Map();
  for (const e of data.entries) {
    const g = e.name.split('/')[0];
    if (!groups.has(g)) groups.set(g, []);
    groups.get(g).push(e);
  }
  const main = $('#main');
  const cards = [];
  for (const [g, list] of groups) {
    const sec = document.createElement('section');
    sec.className = 'group';
    sec.innerHTML = '<h2>' + esc(g) + ' <span class="meta">(' + list.length + ')</span></h2><div class="entries"></div>';
    const wrap = sec.querySelector('.entries');
    for (const e of list) {
      const el = document.createElement('article');
      el.className = 'entry' + (e.changed ? ' changed' : '');
      el.dataset.search = (e.name + ' ' + (e.meta?.description ?? '') + ' ' + (e.meta?.note ?? '')).toLowerCase();
      el.dataset.changed = e.changed ? '1' : '';
      const status = e.shots.find((s) => s.status === 'changed' || s.status === 'added' || s.status === 'removed');
      el.innerHTML =
        '<h3>' + esc(e.name) + (status ? '<span class="badge b-' + status.status + '">' + status.status + '</span>' : '') + '</h3>' +
        (e.meta?.description ? '<p class="desc">' + esc(e.meta.description) + '</p>' : '') +
        (e.meta?.note ? '<p class="note">' + esc(e.meta.note) + '</p>' : '') +
        '<div class="tabs themes"></div><div class="tabs vps"></div><div class="shots"></div>';
      wrap.appendChild(el);
      cards.push({ el, e });
      setupEntry(el, e);
    }
    main.appendChild(sec);
  }

  function setupEntry(el, e) {
    const shotsEl = el.querySelector('.shots');
    if (!e.shots.length) { shotsEl.innerHTML = '<p class="empty">No screenshots (not capturable; see note).</p>'; return; }
    const themes = [...new Set(e.shots.map((s) => s.theme))];
    const first = e.shots.find((s) => s.status === 'changed' || s.status === 'added' || s.status === 'removed') || e.shots[0];
    let theme = first.theme, vp = first.viewport;
    const tabRow = (row, values, current, onPick, changedSet) => {
      row.innerHTML = '';
      if (values.length < 2 && row.classList.contains('themes')) return;
      for (const v of values) {
        const b = document.createElement('button');
        b.textContent = v;
        b.className = (v === current ? 'on' : '') + (changedSet.has(v) ? ' chg' : '');
        b.onclick = () => onPick(v);
        row.appendChild(b);
      }
    };
    const render = () => {
      const vps = e.shots.filter((s) => s.theme === theme).map((s) => s.viewport);
      if (!vps.includes(vp)) vp = vps[0];
      const chg = (s) => s.status === 'changed' || s.status === 'added' || s.status === 'removed';
      tabRow(el.querySelector('.themes'), themes, theme, (v) => { theme = v; render(); }, new Set(e.shots.filter(chg).map((s) => s.theme)));
      tabRow(el.querySelector('.vps'), vps, vp, (v) => { vp = v; render(); }, new Set(e.shots.filter((s) => s.theme === theme && chg(s)).map((s) => s.viewport)));
      const s = e.shots.find((x) => x.theme === theme && x.viewport === vp);
      const figs = [];
      const fig = (img, cap, kind) => img ? '<figure><img loading="lazy" src="' + img.thumb + '" data-kind="' + kind + '" alt="' + esc(e.name + ' ' + cap) + '"><figcaption>' + esc(cap) + '</figcaption></figure>' : '';
      if (data.compare && (s.before || s.diff || s.status === 'removed')) {
        shotsEl.className = 'shots cmp';
        figs.push(fig(s.before, 'before (' + data.baseRef + ')', 'before') || '<figure><p class="empty">new</p></figure>');
        figs.push(fig(s.after, 'after', 'after') || '<figure><p class="empty">removed</p></figure>');
        figs.push(fig(s.diff, s.sizeChanged ? 'size changed ' + s.sizeChanged : 'diff: ' + (s.diffPixels ?? 0).toLocaleString() + ' px', 'diff') || '<figure><p class="empty">' + (s.sizeChanged ? 'size changed ' + esc(s.sizeChanged) : '') + '</p></figure>');
      } else {
        shotsEl.className = 'shots';
        figs.push(fig(s.after, theme + ' · ' + vp + (data.compare ? ' · unchanged' : ''), 'after'));
      }
      shotsEl.innerHTML = figs.join('');
      shotsEl.querySelectorAll('img').forEach((img) => img.onclick = () => openLightbox(e, s, img.dataset.kind));
    };
    render();
  }

  // Lightbox with before/after/diff switching (keys: 1/2/3, Esc).
  let lb = null;
  function openLightbox(e, s, kind) {
    lb = { e, s, kind };
    $('#lightbox').classList.add('on');
    showLb();
  }
  function showLb() {
    const { e, s, kind } = lb;
    const kinds = ['before', 'after', 'diff'].filter((k) => s[k]);
    $('#lb-title').textContent = e.name + ' · ' + s.theme + ' · ' + s.viewport;
    const tabs = $('#lb-tabs');
    tabs.innerHTML = '';
    kinds.forEach((k, i) => {
      const b = document.createElement('button');
      b.textContent = (i + 1) + ' ' + k;
      b.className = k === kind ? 'on' : '';
      b.onclick = () => { lb.kind = k; showLb(); };
      tabs.appendChild(b);
    });
    const img = $('#lb-img');
    img.className = '';
    img.onerror = () => { img.onerror = null; img.src = s[kind].thumb; };
    img.src = s[kind].full;
  }
  $('#lb-img').onclick = (ev) => ev.currentTarget.classList.toggle('natural');
  $('#lb-close').onclick = () => $('#lightbox').classList.remove('on');
  $('#lightbox').onclick = (ev) => { if (ev.target.id === 'lightbox' || ev.target.classList.contains('view')) $('#lightbox').classList.remove('on'); };
  document.addEventListener('keydown', (ev) => {
    if (!$('#lightbox').classList.contains('on')) return;
    if (ev.key === 'Escape') $('#lightbox').classList.remove('on');
    const kinds = ['before', 'after', 'diff'].filter((k) => lb.s[k]);
    const n = Number(ev.key);
    if (n >= 1 && n <= kinds.length) { lb.kind = kinds[n - 1]; showLb(); }
  });

  // Filter
  const apply = () => {
    const q = $('#filter').value.trim().toLowerCase();
    const only = data.compare && $('#only-changed').checked;
    for (const { el } of cards) el.hidden = (q && !el.dataset.search.includes(q)) || (only && !el.dataset.changed);
    document.querySelectorAll('section.group').forEach((sec) => { sec.hidden = ![...sec.querySelectorAll('.entry')].some((x) => !x.hidden); });
  };
  $('#filter').addEventListener('input', apply);
  $('#only-changed').addEventListener('change', apply);
  const initial = new URLSearchParams(location.search).get('q');
  if (initial) $('#filter').value = initial;
  apply();
})();
</script>
</body>
</html>
`;
}
