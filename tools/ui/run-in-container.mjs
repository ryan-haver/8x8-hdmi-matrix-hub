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
// Playwright, e.g. `npm run visual:test -- --grep "drawer/theme"`. Passing
// `--project=<name>` runs only those projects instead of every visual
// project, e.g. `npm run visual:update -- --project=kiosk-tab-a11`.
//
// Works on Windows (Docker Desktop, PowerShell or Git Bash), macOS and Linux.
// The repo is bind-mounted at /work. node_modules inside the container is a
// named volume (the host's node_modules may hold Windows binaries), and pip,
// npm and the Python venv are cached in a second named volume.
import { spawn, spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const IMAGE = 'mcr.microsoft.com/playwright:v1.63.0-noble';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const VOLUME_NODE_MODULES = 'hdmi-hub-ui-node-modules';
const VOLUME_CACHE = 'hdmi-hub-ui-cache';
const CONFIG = 'tests/e2e/playwright.config.ts';
// Keep in sync with tests/e2e/support/viewports.ts (VIEWPORTS) and the CI ui job.
const VISUAL_PROJECTS = ['desktop', 'tablet', 'phone', 'kiosk-tab-a11', 'kiosk-iphone16promax'];

const [mode = 'test', ...rest] = process.argv.slice(2);
const passthrough = rest[0] === '--' ? rest.slice(1) : rest;

const quote = (s) => `'${String(s).replace(/'/g, `'\\''`)}'`;

let playwright;
switch (mode) {
  case 'test':
  case 'update': {
    const ownProjects = passthrough.some((a) => a === '--project' || a.startsWith('--project='));
    const projects = ownProjects ? [] : VISUAL_PROJECTS.map((p) => `--project=${p}`);
    const args = ['npx', 'playwright', 'test', '-c', CONFIG, ...projects];
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
  // Write everything inside the container and copy it back once at the end:
  // Docker Desktop bind mounts (Windows) intermittently fail concurrent
  // writes with ENOMEM. `cp -a -u` only copies files that are new or newer.
  'SNAP=tests/e2e/visual/__snapshots__',
  'export E2E_SNAPSHOT_DIR=/tmp/ui/snapshots E2E_OUTPUT_DIR=/tmp/ui/test-results E2E_REPORT_DIR=/tmp/ui/playwright-report',
  'mkdir -p "$E2E_SNAPSHOT_DIR"',
  'if [ -d "$SNAP" ]; then cp -a "$SNAP/." "$E2E_SNAPSHOT_DIR/"; fi',
  'copy_back() { for i in 1 2 3 4 5; do mkdir -p "$2" && cp -a -u "$1/." "$2/" && return 0; echo "[ui-container] copy to $2 failed (attempt $i), retrying" >&2; sleep 3; done; return 1; }',
  'status=0',
  `${playwright} || status=$?`,
  'if ! copy_back "$E2E_SNAPSHOT_DIR" "$SNAP"; then status=1; fi',
  'rm -rf test-results playwright-report',
  'if [ -d "$E2E_OUTPUT_DIR" ]; then copy_back "$E2E_OUTPUT_DIR" test-results || status=1; fi',
  'if [ -d "$E2E_REPORT_DIR" ]; then copy_back "$E2E_REPORT_DIR" playwright-report || status=1; fi',
  chown,
  'exit $status',
].join('\n');

const tty = process.stdin.isTTY && process.stdout.isTTY;
// Unique name so an interrupted run can be stopped (killing the docker CLI
// alone leaves the container running).
const name = `hdmi-hub-ui-${process.pid}-${Date.now()}`;
// Docker Desktop VMs are often small (a few GB); four Chromium workers plus
// the stack can exhaust them. Default to 2 locally; CI sets its own.
const workers = process.env.E2E_WORKERS ?? '2';
const dockerArgs = [
  'run',
  '--rm',
  '--init',
  '--name', name,
  '--shm-size=1g',
  ...(tty ? ['-it'] : []),
  '-v', `${ROOT}:/work`,
  '-v', `${VOLUME_NODE_MODULES}:/work/node_modules`,
  '-v', `${VOLUME_CACHE}:/cache`,
  '-w', '/work',
  '-e', 'CI',
  '-e', 'UI_CACHE_DIR=/cache',
  '-e', 'E2E_LOG_LEVEL',
  '-e', `E2E_WORKERS=${workers}`,
  '-e', 'npm_config_update_notifier=false',
  IMAGE,
  'bash', '-c', script,
];

// Git Bash rewrites /work-style arguments into Windows paths; disable that.
const env = { ...process.env, MSYS_NO_PATHCONV: '1', MSYS2_ARG_CONV_EXCL: '*' };
console.log(
  `[ui-container] ${IMAGE}: ${mode}${passthrough.length ? ` ${passthrough.join(' ')}` : ''} (workers: ${workers})`,
);
const child = spawn('docker', dockerArgs, { stdio: 'inherit', env });
let stopping = false;
const stop = () => {
  if (stopping) return;
  stopping = true;
  console.error(`\n[ui-container] stopping ${name}`);
  spawnSync('docker', ['stop', '-t', '5', name], { stdio: 'ignore', env });
};
for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
  process.on(sig, () => {
    stop();
    process.exit(130);
  });
}
child.on('error', (err) => {
  console.error(`[ui-container] could not run docker: ${err.message}`);
  process.exit(1);
});
child.on('exit', (code) => process.exit(code ?? 1));
