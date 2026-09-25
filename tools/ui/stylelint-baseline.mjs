#!/usr/bin/env node
// Stylelint with a checked-in baseline (the CSS counterpart of ESLint's
// eslint-suppressions.json).
//
//   node tools/ui/stylelint-baseline.mjs            report all findings; exit 1 only if a
//                                                   file/rule count exceeds the baseline
//   node tools/ui/stylelint-baseline.mjs --update   rewrite the baseline from the current findings
//   node tools/ui/stylelint-baseline.mjs --strict   exit 1 on any finding (the end goal)
//
// Baseline: tools/ui/stylelint-baseline.json  { "<file>": { "<rule>": count } }
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import stylelint from 'stylelint';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const baselinePath = path.join(root, 'tools', 'ui', 'stylelint-baseline.json');
const argv = new Set(process.argv.slice(2));
const verbose = argv.has('--verbose');

const { results } = await stylelint.lint({
  cwd: root,
  files: ['web/css/**/*.css'],
  configFile: path.join(root, 'stylelint.config.js'),
});

const current = {};
let total = 0;
for (const r of results) {
  const file = path.relative(root, r.source).split(path.sep).join('/');
  for (const w of r.warnings) {
    total++;
    ((current[file] ??= {})[w.rule] ??= 0);
    current[file][w.rule]++;
    if (verbose) console.log(`${file}:${w.line}:${w.column}  ${w.text}`);
  }
  for (const e of r.parseErrors ?? []) console.error(`${file}: parse error ${e.text}`);
}

if (argv.has('--update')) {
  const sorted = Object.fromEntries(
    Object.keys(current)
      .sort()
      .map((f) => [f, Object.fromEntries(Object.entries(current[f]).sort())]),
  );
  fs.writeFileSync(baselinePath, `${JSON.stringify(sorted, null, 2)}\n`);
  console.log(`stylelint baseline written: ${total} findings in ${Object.keys(sorted).length} files`);
  process.exit(0);
}

const baseline = fs.existsSync(baselinePath) ? JSON.parse(fs.readFileSync(baselinePath, 'utf8')) : {};
const rows = [];
const regressions = [];
let improved = 0;
for (const file of new Set([...Object.keys(current), ...Object.keys(baseline)])) {
  for (const rule of new Set([...Object.keys(current[file] ?? {}), ...Object.keys(baseline[file] ?? {})])) {
    const now = current[file]?.[rule] ?? 0;
    const was = baseline[file]?.[rule] ?? 0;
    rows.push({ file, rule, now, was });
    if (now > was) regressions.push({ file, rule, now, was });
    if (now < was) improved++;
  }
}
rows.sort((a, b) => b.now - a.now);
console.log(`stylelint: ${total} findings (baseline ${Object.values(baseline).flatMap(Object.values).reduce((a, b) => a + b, 0)})`);
for (const { file, rule, now, was } of rows) {
  const flag = now > was ? '  <-- NEW' : now < was ? '  (improved: run npm run lint:css:baseline)' : '';
  console.log(`  ${String(now).padStart(4)}  ${rule.padEnd(40)} ${file}${flag}`);
}
if (!verbose) console.log('  (run with --verbose for every finding with line numbers)');

if (argv.has('--strict') && total > 0) {
  console.error(`\nstylelint --strict: ${total} findings`);
  process.exit(1);
}
if (regressions.length) {
  console.error('\nNew stylelint violations above the baseline:');
  for (const r of regressions) console.error(`  ${r.file}  ${r.rule}: ${r.was} -> ${r.now}`);
  console.error('Fix them (see --verbose). Only if intentional, update tools/ui/stylelint-baseline.json via --update.');
  process.exit(1);
}
if (improved) console.log(`\n${improved} file/rule counts went down; lower the baseline with npm run lint:css:baseline.`);
