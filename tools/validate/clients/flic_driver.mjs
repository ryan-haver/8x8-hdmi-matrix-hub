/**
 * Dedicated Flic Bridge & Node Driver (WP-D1 / R6).
 *
 * Provides authoritative execution of updateFlicOutput and updateFlicSdkSnippet
 * from web/js/components/integrations-drawer.js using minimal DOM and state stubs.
 * Also provides Hub SDK callback execution harness for event evaluation.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '../../..');
export const DEFAULT_DRAWER_PATH = path.resolve(REPO_ROOT, 'web/js/components/integrations-drawer.js');

/**
 * Creates minimal DOM, window, and state stubs needed to run IntegrationsDrawer.
 */
export function createMinimalDomState(origin = 'http://127.0.0.1:8080') {
  const elements = {};

  function getOrCreate(sel) {
    if (!elements[sel]) {
      elements[sel] = {
        tagName: 'DIV',
        id: sel.startsWith('#') ? sel.slice(1) : '',
        className: '',
        textContent: '',
        innerText: '',
        innerHTML: '',
        classList: {
          classes: new Set(),
          add: function (c) { this.classes.add(c); },
          remove: function (c) { this.classes.delete(c); },
          contains: function (c) { return this.classes.has(c); },
          toggle: function (c, force) {
            if (force === undefined) {
              if (this.classes.has(c)) this.classes.delete(c);
              else this.classes.add(c);
            } else if (force) {
              this.classes.add(c);
            } else {
              this.classes.delete(c);
            }
          }
        },
        attributes: {},
        setAttribute: function (k, v) { this.attributes[k] = v; },
        getAttribute: function (k) { return this.attributes[k]; },
        addEventListener: function () {},
        appendChild: function (c) { return c; },
        querySelector: (s) => getOrCreate(s),
        querySelectorAll: () => []
      };
    }
    return elements[sel];
  }

  const windowMock = {
    location: { origin },
    overlayManager: null
  };

  const documentMock = {
    createElement: (tag) => getOrCreate(tag),
    body: getOrCreate('body'),
    addEventListener: () => {}
  };

  const stateMock = {
    info: { model: 'HDMI Matrix' },
    presets: { 1: { name: 'Preset 1' } },
    profiles: [{ id: 'p1', name: 'Profile 1' }],
    getInputName: (n) => `Input ${n}`,
    getOutputName: (n) => `Output ${n}`,
    on: () => {}
  };

  const HelpersMock = {
    escapeHtml: (s) => String(s)
  };

  return { store: elements, getOrCreate, windowMock, documentMock, stateMock, HelpersMock };
}

/**
 * Loads IntegrationsDrawer from source file with stubs and returns instance and DOM store.
 */
export function loadIntegrationsDrawer(sourcePath = DEFAULT_DRAWER_PATH, origin = 'http://127.0.0.1:8080') {
  const { store, getOrCreate, windowMock, documentMock, stateMock, HelpersMock } = createMinimalDomState(origin);
  const code = fs.readFileSync(sourcePath, 'utf8');
  const fn = new Function('window', 'document', 'state', 'Helpers', code);
  fn(windowMock, documentMock, stateMock, HelpersMock);
  const drawer = windowMock.integrationsDrawer;
  return { drawer, store, getOrCreate };
}

/**
 * Executes updateFlicOutput and updateFlicSdkSnippet on IntegrationsDrawer.
 */
export function generateOutput(config = {}, options = {}) {
  const sourcePath = options.sourcePath || DEFAULT_DRAWER_PATH;
  const origin = options.origin || 'http://127.0.0.1:8080';
  const { drawer, getOrCreate } = loadIntegrationsDrawer(sourcePath, origin);

  if (config) {
    Object.assign(drawer.flicConfig, config);
  }

  drawer.updateFlicOutput();

  const method = getOrCreate('#flic-out-method').textContent || 'POST';
  const fullUrl = getOrCreate('#flic-out-url').textContent || '';
  const urlPath = fullUrl.startsWith(origin) ? fullUrl.slice(origin.length) : fullUrl;
  const bodyText = getOrCreate('#flic-out-body').textContent || '';
  const bodyRow = getOrCreate('#flic-out-body-row');
  const hasBody = !bodyRow.classList.contains('hidden') && bodyText.trim().length > 0;

  let bodyObj = null;
  if (hasBody) {
    try {
      bodyObj = JSON.parse(bodyText);
    } catch {
      bodyObj = bodyText;
    }
  }
  const snippet = getOrCreate('#flic-sdk-code-block').textContent || '';

  return {
    method,
    url: fullUrl,
    urlPath,
    body: bodyObj,
    hasBody,
    snippet
  };
}

/**
 * Executes a generated Flic Hub SDK script in a CommonJS-compatible sandbox
 * with buttonManager and http module stubs.
 */
export function runSdkHarness({ script, scriptPath, buttons = [], events = [] }) {
  const requests = [];
  const eventListeners = {};

  const buttonManager = {
    getButtons: function () {
      return buttons.map((b) => ({
        name: b.name,
        bdaddr: b.bdaddr,
        serialNumber: b.serial || b.serialNumber || ''
      }));
    },
    getButton: function (bdaddr) {
      const found = buttons.find((b) => b.bdaddr === bdaddr);
      if (!found) return null;
      return {
        name: found.name,
        bdaddr: found.bdaddr,
        serialNumber: found.serial || found.serialNumber || ''
      };
    },
    on: function (eventName, cb) {
      if (!eventListeners[eventName]) {
        eventListeners[eventName] = [];
      }
      eventListeners[eventName].push(cb);
    }
  };

  const http = {
    makeRequest: function (opts, cb) {
      requests.push({
        url: opts.url,
        method: opts.method,
        headers: opts.headers || {},
        content: opts.content || null
      });
      if (typeof cb === 'function') {
        cb(null, { statusCode: 200, content: '{"success":true}' });
      }
    }
  };

  function customRequire(mod) {
    if (mod === 'buttons') return buttonManager;
    if (mod === 'http') return http;
    throw new Error('Unknown module: ' + mod);
  }

  const scriptCode = script || (scriptPath ? fs.readFileSync(scriptPath, 'utf8') : '');
  if (!scriptCode) {
    throw new Error('No script or scriptPath provided to runSdkHarness');
  }

  const wrapper = new Function('require', 'console', `\n${scriptCode}\n`);
  wrapper(customRequire, { log: () => {}, error: () => {} });
  const startupRequestsCount = requests.length;

  const eventResults = [];
  for (const evt of events) {
    const preCount = requests.length;
    const listeners = eventListeners[evt.eventName] || [];
    for (const cb of listeners) {
      cb(evt.payload);
    }
    const postCount = requests.length;
    eventResults.push({
      event: evt,
      requestsTriggered: postCount - preCount,
      requests: requests.slice(preCount)
    });
  }

  return {
    allRequests: requests,
    startupRequestsCount,
    eventResults
  };
}

// ==========================================
// CLI ENTRY POINT
// ==========================================
async function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || '--generate';

  if (mode === '--info') {
    const result = {
      nodeVersion: process.version,
      defaultSource: DEFAULT_DRAWER_PATH
    };
    process.stdout.write(JSON.stringify(result));
    return;
  }

  // Read payload from stdin
  const inputChunks = [];
  for await (const chunk of process.stdin) {
    inputChunks.push(chunk);
  }
  const inputStr = Buffer.concat(inputChunks).toString('utf8').trim();
  const input = inputStr ? JSON.parse(inputStr) : {};

  if (mode === '--generate') {
    const out = generateOutput(input.config || {}, {
      sourcePath: input.sourcePath,
      origin: input.origin
    });
    process.stdout.write(JSON.stringify(out));
  } else if (mode === '--harness') {
    const out = runSdkHarness({
      script: input.script,
      scriptPath: input.scriptPath,
      buttons: input.buttons || [],
      events: input.events || []
    });
    process.stdout.write(JSON.stringify(out));
  } else {
    process.stderr.write(`Unknown mode: ${mode}\n`);
    process.exit(1);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(__filename)) {
  main().catch((err) => {
    process.stderr.write(String(err?.stack || err) + '\n');
    process.exit(1);
  });
}
