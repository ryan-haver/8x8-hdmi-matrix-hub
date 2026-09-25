// ESLint flat config (dev-only tooling; see package.json).
//
// The web UI is ~50 classic <script> files that share state through top-level
// declarations and window.* properties. Those cross-file globals are derived
// from the source at lint time (see appGlobals below), so the list never goes
// stale and `no-undef` still catches genuinely undefined names.
//
// Existing violations: web/ is frozen until the Phase 0 UI baseline is signed
// off, so current findings are recorded in eslint-suppressions.json (ESLint
// bulk suppressions) instead of being fixed. `npm run lint:js` therefore
// fails only on NEW violations; `npm run lint:js:all` reports everything.
// After fixing code, run `npm run lint:js:prune` to shrink the baseline.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import js from '@eslint/js';
import globals from 'globals';

const root = path.dirname(fileURLToPath(import.meta.url));

/** Collect names declared at the top level of the classic scripts or assigned to window.*. */
function appGlobals() {
  const names = new Set();
  const walk = (dir) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name.endsWith('.js')) {
        const src = fs.readFileSync(full, 'utf8');
        for (const m of src.matchAll(/^(?:async\s+)?(?:function\*?|class|const|let|var)\s+([A-Za-z_$][\w$]*)/gm)) {
          names.add(m[1]);
        }
        for (const m of src.matchAll(/\bwindow\.([A-Za-z_$][\w$]*)\s*=(?!=)/g)) names.add(m[1]);
      }
    }
  };
  walk(path.join(root, 'web', 'js'));
  return Object.fromEntries([...names].sort().map((n) => [n, 'writable']));
}

export default [
  {
    ignores: [
      'node_modules/**',
      'playwright-report/**',
      'test-results/**',
      'ui-gallery/**',
      'web/assets/**',
      '**/*.ts', // Playwright specs are type-checked by Playwright's own TS transform
    ],
  },
  js.configs.recommended,
  {
    // The browser app: classic scripts sharing one global scope.
    files: ['web/js/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'script',
      globals: { ...globals.browser, ...appGlobals() },
    },
    rules: {
      // Each file declares globals that the others use; that is the app's
      // module system today, not an accidental redeclaration or unused var.
      'no-redeclare': ['error', { builtinGlobals: false }],
      'no-unused-vars': ['error', { vars: 'local', args: 'none', caughtErrors: 'none' }],
    },
  },
  {
    // One-off CommonJS maintenance scripts.
    files: ['scripts/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: { ...globals.node },
    },
  },
  {
    // Node tooling (configs, tools/ui, test support scripts).
    files: ['*.js', '*.mjs', 'tools/**/*.mjs', 'tests/**/*.mjs'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      globals: { ...globals.node },
    },
  },
];
