#!/usr/bin/env node
// Run the visual suite inside the pinned Playwright container, so baselines
// never depend on the host's fonts or rendering (docs/REMEDIATION_PLAN.md §5.3).
//
//   node tools/ui/run-in-container.mjs test   [-- <playwright args>]   compare against baselines
//   node tools/ui/run-in-container.mjs update [-- <playwright args>]   write new/changed baselines
//   node tools/ui/run-in-container.mjs smoke  [-- <playwright args>]   smoke E2E in the container
//   node tools/ui/run-in-container.mjs shell                           interactive shell
//
// npm scripts: visual:test, visual:update. Extra args after `--` go to
// Playwright, e.g. `npm run visual:test -- --grep "drawer/theme"`.
//
// Works on Windows (Docker Desktop, PowerShell or Git Bash), macOS and Linux.
// The repo is bind-mounted at /work. node_modules inside the container is a
// named volume (the host's node_modules may hold Windows binaries), and pip,
// npm and the Python venv are cached in a second named volume.
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const IMAGE = 'mcr.microsoft.com/playwright:v1.63.0-noble';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const VOLUME_NODE_MODULES = 'hdmi-hub-ui-node-modules';
const VOLUME_CACHE = 'hdmi-hub-ui-cache';
const CONFIG = 'tests/e2e/playwright.config.ts';
const VISUAL_PROJECTS = ['desktop', 'tablet', 'phone', 'kiosk'];

const [mode = 'test', ...rest] = process.argv.slice(2);
const passthrough = rest[0] === '--' ? rest.slice(1) : rest;

const quote = (s) => `'${String(s).replace(/'/g, `'\\''`)}'`;

let playwright;
switch (mode) {
  case 'test':
  case 'update': {
    const args = ['npx', 'playwright', 'test', '-c', CONFIG, ...VISUAL_PROJECTS.map((p) => `--project=${p}`)];
    if (mode === 'update') args.push('--update-snapshots=changed');
    playwright = [...args, ...passthrough].map(quote).join(' ');
    break;
  }
  case 'smoke':
    playwright = ['npx', 'playwright', 'test', '-c', CONFIG, '--project=smoke', ...passthrough].map(quote).join(' ');
    break;
  case 'shell':
    playwright = 'bash';
    break;
  default:
    console.error(`unknown mode "${mode}" (expected test | update | smoke | shell)`);
    process.exit(2);
}

// On Linux/macOS hosts the container's root-owned output would be awkward to
// delete; hand it back to the invoking user afterwards.
const uid = typeof process.getuid === 'function' ? process.getuid() : null;
const gid = typeof process.getgid === 'function' ? process.getgid() : null;
const chown =
  uid !== null && uid !== 0
    ? `chown -R ${uid}:${gid} tests/e2e/visual test-results playwright-report 2>/dev/null || true`
    : 'true';

const script = [
  'set -eo pipefail',
  'cd /work',
  'setup_out=$(bash tools/ui/container-setup.sh | tee /dev/stderr)',
  'export E2E_PYTHON="${setup_out##*E2E_PYTHON=}"',
  'export PLAYWRIGHT_CONTAINER=1',
  'status=0',
  `${playwright} || status=$?`,
  chown,
  'exit $status',
].join('\n');

const tty = process.stdin.isTTY && process.stdout.isTTY;
const dockerArgs = [
  'run',
  '--rm',
  '--init',
  '--ipc=host',
  ...(tty ? ['-it'] : []),
  '-v', `${ROOT}:/work`,
  '-v', `${VOLUME_NODE_MODULES}:/work/node_modules`,
  '-v', `${VOLUME_CACHE}:/cache`,
  '-w', '/work',
  '-e', 'CI',
  '-e', 'UI_CACHE_DIR=/cache',
  '-e', 'E2E_LOG_LEVEL',
  '-e', 'E2E_WORKERS',
  '-e', 'npm_config_update_notifier=false',
  IMAGE,
  'bash', '-c', script,
];

console.log(`[ui-container] ${IMAGE}: ${mode}${passthrough.length ? ` ${passthrough.join(' ')}` : ''}`);
const result = spawnSync('docker', dockerArgs, {
  stdio: 'inherit',
  // Git Bash rewrites /work-style arguments into Windows paths; disable that.
  env: { ...process.env, MSYS_NO_PATHCONV: '1', MSYS2_ARG_CONV_EXCL: '*' },
});
if (result.error) {
  console.error(`[ui-container] could not run docker: ${result.error.message}`);
  process.exit(1);
}
process.exit(result.status ?? 1);
