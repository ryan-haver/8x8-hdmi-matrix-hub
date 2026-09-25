// Stylelint plugin: `hub/no-raw-colors`.
//
// Colours must come from the design tokens in web/css/theme.css
// (docs/ui/LOOK_AND_FEEL.md §2, §10). This rule flags literal colour values
// anywhere else:
//   - hex colours (#fff, #0a0e14, #00e5cc80)
//   - colour functions whose arguments reference no custom property
//     (rgba(0, 200, 200, .3) is raw; hsla(var(--accent-h), 92%, 50%, .3) is
//     token-derived and allowed)
//   - common named colours (white, black, red, ...) in colour-bearing properties
// `transparent`, `currentColor`, `inherit` and friends are always allowed.
// theme.css is exempted in stylelint.config.js, since it defines the tokens.
import stylelint from 'stylelint';

const {
  createPlugin,
  utils: { report, ruleMessages, validateOptions },
} = stylelint;

const ruleName = 'hub/no-raw-colors';
const messages = ruleMessages(ruleName, {
  rejected: (value) => `Unexpected raw colour "${value}"; use a token from web/css/theme.css`,
});
const meta = { url: 'docs/ui/LOOK_AND_FEEL.md' };

const HEX = /#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4})\b/gi;
const COLOR_FN = /\b(rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\(/gi;
const NAMED = /(?<![\w-])(white|black|red|green|blue|yellow|orange|purple|gray|grey|cyan|magenta|pink|lime|navy|teal|silver|gold|crimson|indigo)(?![\w-])/gi;
const COLOR_PROPS = /(color|background|border|shadow|fill|stroke|outline|caret|gradient|^--)/i;

/** Blank out url(...), strings and comments so their contents are never matched. */
function mask(value) {
  return value
    .replace(/url\([^)]*\)/gi, (m) => ' '.repeat(m.length))
    .replace(/"[^"]*"|'[^']*'/g, (m) => ' '.repeat(m.length))
    .replace(/\/\*[\s\S]*?\*\//g, (m) => ' '.repeat(m.length));
}

/** Return the balanced argument text of a function call starting at `open` (index of "("). */
function args(value, open) {
  let depth = 0;
  for (let i = open; i < value.length; i++) {
    if (value[i] === '(') depth++;
    else if (value[i] === ')' && --depth === 0) return value.slice(open + 1, i);
  }
  return value.slice(open + 1);
}

const ruleFunction = (primary) => (root, result) => {
  if (!validateOptions(result, ruleName, { actual: primary, possible: [true] })) return;

  root.walkDecls((decl) => {
    const value = mask(decl.value);
    const found = [];
    for (const m of value.matchAll(HEX)) found.push([m.index, m[0]]);
    for (const m of value.matchAll(COLOR_FN)) {
      const inner = args(value, m.index + m[0].length - 1);
      if (!/var\(/i.test(inner)) found.push([m.index, `${m[0]}${inner})`]);
    }
    if (COLOR_PROPS.test(decl.prop)) {
      for (const m of value.matchAll(NAMED)) found.push([m.index, m[0]]);
    }
    for (const [, word] of found) {
      report({ ruleName, result, node: decl, message: messages.rejected(word), word });
    }
  });
};

ruleFunction.ruleName = ruleName;
ruleFunction.messages = messages;
ruleFunction.meta = meta;

export default createPlugin(ruleName, ruleFunction);
