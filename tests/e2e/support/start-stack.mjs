#!/usr/bin/env node
// Start the BK-808 simulator + hub for Playwright (the `webServer` command in
// tests/e2e/playwright.config.ts), with a fresh copy of the seeded hub data.
//
//   node tests/e2e/support/start-stack.mjs
//
// - Copies tests/e2e/fixtures/data/ into a new temp dir for every run, so a
//   run never sees data written by a previous one.
// - Runs tools/dev_stack.py (simulator seeded from
//   tools/simulator/states/default.json, hub via run.py in modular API mode)
//   on the fixed E2E ports from tests/e2e/support/ports.mjs.
// - Hub env tuned for deterministic captures, without changing the UI:
//     OREI_STATUS_CACHE_TTL=0      /api/status always reflects the simulator
//     TRUST_PROXY_HEADERS=true +   each test sends its own X-Forwarded-For,
//     TRUSTED_PROXY_IPS=127.0.0.1  so it gets its own rate-limit bucket
//                                  (60 req / 10 s per client IP, see
//                                  src/rest_api/utils.py)
// Python: $E2E_PYTHON, else .venv in this checkout or the main checkout,
// else python3/python on PATH.
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PORTS } from './ports.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const FIXTURE_DATA = path.join(ROOT, 'tests', 'e2e', 'fixtures', 'data');
const TMP_PREFIX = 'hub-e2e-data-';

function findPython() {
  if (process.env.E2E_PYTHON) return process.env.E2E_PYTHON;
  const roots = [ROOT];
  const common = spawnSync('git', ['rev-parse', '--path-format=absolute', '--git-common-dir'], {
    cwd: ROOT,
    encoding: 'utf8',
  });
  if (common.status === 0 && common.stdout.trim()) roots.push(path.dirname(common.stdout.trim()));
  for (const r of roots) {
    for (const rel of [['.venv', 'Scripts', 'python.exe'], ['.venv', 'bin', 'python']]) {
      const p = path.join(r, ...rel);
      if (fs.existsSync(p)) return p;
    }
  }
  for (const name of ['python3', 'python']) {
    if (spawnSync(name, ['--version']).status === 0) return name;
  }
  throw new Error('No Python found; set E2E_PYTHON');
}

// Playwright on Windows kills the webServer process tree without a signal, so
// cleanup handlers may not run. Remove leftovers from earlier runs instead.
function removeStaleDataDirs() {
  const cutoff = Date.now() - 6 * 3600 * 1000;
  for (const name of fs.readdirSync(os.tmpdir())) {
    if (!name.startsWith(TMP_PREFIX)) continue;
    const full = path.join(os.tmpdir(), name);
    try {
      if (fs.statSync(full).mtimeMs < cutoff) fs.rmSync(full, { recursive: true, force: true });
    } catch {
      /* in use or already gone */
    }
  }
}

removeStaleDataDirs();
const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), TMP_PREFIX));
fs.cpSync(FIXTURE_DATA, dataDir, { recursive: true });
console.log(`[e2e-stack] seeded hub data: ${dataDir}`);

const python = findPython();
const child = spawn(
  python,
  [
    path.join('tools', 'dev_stack.py'),
    '--host', '127.0.0.1',
    '--api-port', String(PORTS.api),
    '--https-port', String(PORTS.https),
    '--telnet-port', String(PORTS.telnet),
    '--control-port', String(PORTS.control),
    '--data-dir', dataDir,
    '--log-level', process.env.E2E_LOG_LEVEL ?? 'WARNING',
  ],
  {
    cwd: ROOT,
    stdio: 'inherit',
    env: {
      ...process.env,
      OREI_STATUS_CACHE_TTL: '0',
      TRUST_PROXY_HEADERS: 'true',
      TRUSTED_PROXY_IPS: '127.0.0.1',
      PYTHONDONTWRITEBYTECODE: '1',
    },
  },
);

let stopping = false;
function stop(code) {
  if (stopping) return;
  stopping = true;
  if (child.exitCode === null) child.kill('SIGTERM');
  setTimeout(() => {
    fs.rmSync(dataDir, { recursive: true, force: true });
    process.exit(code);
  }, 1500).unref();
}
for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) process.on(sig, () => stop(0));
child.on('exit', (code) => {
  fs.rmSync(dataDir, { recursive: true, force: true });
  if (!stopping) process.exit(code ?? 1);
});
