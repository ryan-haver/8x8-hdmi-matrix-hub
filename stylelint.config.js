// Stylelint config (dev-only tooling; see package.json).
//
// `hub/no-raw-colors` (tools/ui/stylelint-no-raw-colors.mjs) enforces that
// colours come from the tokens in web/css/theme.css (docs/ui/LOOK_AND_FEEL.md).
//
// Existing violations: web/ is frozen until the Phase 0 UI baseline is signed
// off, so current findings are recorded per file and rule in
// tools/ui/stylelint-baseline.json. `npm run lint:css` prints every finding
// but fails only when a file/rule count goes UP (a new violation);
// `npm run lint:css:strict` fails on any finding. After fixing CSS, run
// `npm run lint:css:baseline` to lower the recorded counts.
export default {
  extends: ['stylelint-config-recommended'],
  plugins: ['./tools/ui/stylelint-no-raw-colors.mjs'],
  rules: {
    'hub/no-raw-colors': true,
  },
  overrides: [
    {
      // The token source of truth may (must) contain literal colours.
      files: ['web/css/theme.css'],
      rules: { 'hub/no-raw-colors': null },
    },
  ],
};
