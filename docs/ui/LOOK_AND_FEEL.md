# Look & Feel Specification

> **Status:** APPROVED 2026-09-25. The project owner signed it off after walking through the Phase 0 UI baseline gallery (170 catalog entries, 763 snapshots, `tests/e2e/visual/`). The baseline screenshots are the visual reference for every section below. From now on, changes to this document go through the same review as a visual baseline change (see `docs/REMEDIATION_PLAN.md` §5.3).
>
> **Purpose:** define what "correct" looks like, so every UI change can be checked against something written down rather than against memory.

---

## 1. Character

- **Dark, layered, and glowing.** Near-black blue backgrounds, translucent "glass" surfaces on top, and a single saturated accent that glows on active and hover states.
- **Tron-inspired.** The default pairing is cyan (primary) and orange (secondary), with a faint grid behind the content and an optional animated light-cycle background.
- **Calm by default, bright when active.** Idle elements are muted. The accent colour and glow mark what is live: the current route, the connected state, and the focused control.
- **Touch-first.** The same UI runs on a desktop, a tablet, a phone, and a wall-mounted kiosk.

## 2. Colour system

### 2.1 Accent model (HSL)

All accent colours derive from two hues, so a theme preset changes only hue values, never individual colours.

| Token | Definition | Role |
| --- | --- | --- |
| `--accent-h` / `--accent-s` / `--accent-l` | default `187 / 92% / 50%` | Primary hue (Tron cyan) |
| `--accent` | `hsl(h, s, l)` | Active state, primary buttons, focus, links on hover |
| `--accent-hover` / `--accent-active` | lightness +8% / −5% | Pointer states |
| `--accent-dim` | accent at 15% alpha | Active backgrounds, selected pills |
| `--accent-glow` | accent at 40% alpha | Glow shadows |
| `--accent-gradient` | 135° from accent to hue+15 | Primary buttons |
| `--secondary-h` | default `25` (orange) | Secondary hue: standby state, warnings, second light cycle |

**Derived status colours** (never hard-code these):

| Token | Derived from | Meaning |
| --- | --- | --- |
| `--status-active` | accent | Connected / routed / signal present |
| `--status-standby` | secondary | Standby / idle / warning |
| `--status-disconnected` | `--text-muted` at 50% opacity | Offline / no signal |
| `--status-error` | accent hue + 120° | Errors |

### 2.2 Theme presets

| Preset | Primary hue | Secondary hue |
| --- | --- | --- |
| Tron Classic (default) | 187 (cyan) | 25 (orange) |
| Neon | 350 (crimson) | 80 (lime) |
| Royal | 240 (indigo) | 45 (gold) |
| Vaporwave | 170 (teal) | 330 (pink) |

The swatch picker offers eight hues (Cyan 187, Orange 25, Crimson 350, Lime 80, Indigo 240, Gold 45, Teal 170, Pink 330). Users can customise the four presets. **Rule:** every coloured element must follow the active preset. Nothing may stay cyan or orange when the preset changes (see §9, observed issues).

### 2.3 Neutral palette

| Token | Value | Use |
| --- | --- | --- |
| `--bg-base` | `#0a0e14` | Page background |
| `--bg-elevated` | `#111720` | Cards, modals |
| `--bg-surface` | `#1a2130` | Interactive surfaces |
| `--bg-hover` / `--bg-active` | `#242e40` / `#2d3a50` | Pointer states |
| `--text-primary` | `#f0f4f8` | Body text, titles |
| `--text-secondary` | `#a0aec0` | Labels, secondary info |
| `--text-muted` | `#5a6a7a` | Hints, disabled-adjacent |
| `--text-disabled` | `#3a4454` | Disabled |
| `--border-subtle` / `--border-default` / `--border-strong` | white at 6% / 10% / 15% | Dividers, outlines |

## 3. Surfaces: glass, cards, modals

| Element | Background | Border | Radius | Shadow / glow |
| --- | --- | --- | --- | --- |
| Glass panel | `--glass-bg` (`rgba(17,23,32,.75)`), `backdrop-filter: blur(16px)` (heavy: 24px) | `1px` white at 8% | — | `--glass-shadow` `0 8px 32px rgba(0,0,0,.4)` |
| Card | `rgba(17,23,32, var(--card-opacity))` | white at `8% × opacity`; hover: accent 30%; active: accent 60% | `--card-radius` 12px | hover `0 8px 25px rgba(0,0,0,.4)`; selected: accent glow |
| Modal / drawer | `--modal-bg` (opacity-aware) | accent at 25% (strong: 40%) | `--modal-radius` 16px | accent glow `0 0 40px` at 15% |

- **Card opacity** (`--card-opacity`, default 0.8) is user-adjustable. Surfaces must stay legible from about 0.4 to 1.0.
- Glass blur is capped at 16–24px. Lighter overlays use 4–10px.

## 4. Typography

- **Family:** system UI stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif`). No web fonts.
- **Monospace** (API snippets, debug panel): intended as `--font-mono`, which is currently undefined (see §9).
- **Scale:** 12 / 14 / 16 / 18 / 20 / 24px (`--font-size-xs` … `--font-size-2xl`); base 16px, line-height 1.5.
- **Weights:** 400 body, 500 labels, 600 titles and buttons, 700 emphasis.

## 5. Spacing, radii, elevation

- **Spacing scale (4px base):** 4, 8, 12, 16, 20, 24, 32, 40, 48 (`--space-1` … `--space-12`). Components use only these values.
- **Radii:** 4 (small chips), 8, 12 (cards), 10 (buttons, inputs), 16 (modals, drawers), full (pills, toggles).
- **Shadows:** `--shadow-sm/md/lg/xl`, plus accent glows (`--glow-cyan-sm` 8px, `--glow-cyan` 16px, `--glow-cyan-lg` 24+48px). Glow means "active or focused". Don't use it for decoration.
- **Z-index layers:** base 0 · dropdown 100 · sticky 200 · fixed 300 · modal backdrop 400 · modal 500 · toast 600 · tooltip 700.

## 6. Motion

- **Easing:** `--ease-out-expo` `cubic-bezier(0.16, 1, 0.3, 1)` for almost everything.
- **Durations:** fast 150ms (hover, press), normal 250ms (drawers, toggles), slow 400ms (large panels).
- **Tron background:** opt-in (off by default), animated light cycles in the primary and secondary hues.
- **Reduced motion:** with `prefers-reduced-motion: reduce`, transitions become instant and the Tron background stays off.

## 7. Controls

| Control | Resting | Hover / focus | Active / on |
| --- | --- | --- | --- |
| Primary button | accent gradient, dark text `#0d0d1a`, radius 10, accent glow shadow | stronger glow | pressed: `--accent-active` |
| Secondary button | transparent, white 20% border | accent 50% border | — |
| Danger button | red gradient `#ef4444 → #dc2626` | — | — |
| Input | white 5% fill, white 10% border, radius 10 | accent 5% fill, accent 50% border, 3px accent focus ring | — |
| Toggle | white 10% track | — | accent track + 10px accent glow |
| Pill / chip | white 5% fill, white 10% border | — | accent-dim fill |

**Focus:** every interactive element shows a visible accent focus ring. **Touch targets:** minimum 44×44px (Phase 5 target; some controls are currently 22px, see §9).

## 8. Component anatomy

The visual reference for each component is its entries in the UI state catalog (`tests/e2e/visual/catalog.ts`) and their approved baselines (browse them with `npm run visual:gallery`).

- **Header:** app title (matrix model name) with the connection status shown as a coloured border line around the title (active / standby / disconnected colours); desktop tabs centred.
- **Tabs:** Matrix · Dashboard · Inputs · Outputs · Profiles. Users can pin and reorder them. Mobile uses a bottom tab bar.
- **Control Deck (side nav):** tab list plus a grid of utility buttons (Route All, Presets, Theme, Refresh, General, Hardware, Interface, Shortcuts, Integrations). Coexists with one right-side drawer.
- **Right-side drawers:** glass surface with modal border, radius 16, header with title and close button. Only one is open at a time.
- **Matrix grid:** inputs × outputs cells. The routed cell uses accent fill and glow; output cards use a 2×4 layout.
- **Output tile → CEC remote:** tapping an output tile opens a bottom-drawer remote (D-pad or trackpad, playback, volume, power).
- **Dashboard cards:** profile, scene, preset, macro, and shortcut cards; card surface and hover rules from §3.
- **Toasts:** top layer (z 600), status-coloured accent edge.
- **Kiosk:** header ("Select Input", edit button, status, link to the full UI), swipeable tabs (Routing · Presets · Shortcuts · Profiles), tile grids, an "Output Status" footer, and the bottom-drawer CEC remote.

## 9. Observed inconsistencies (for review, not yet fixed)

These are recorded as found in the current UI, and the approved baseline captures them as they are. They stay open until Phase 5, where each fix is made as a deliberate, reviewed visual change.

1. **Hard-coded Tron colours.** The body background grid (`style.css`) and about 30 other places use literal cyan/orange values (`rgba(0,200,200,…)`, `rgba(255,140,0,…)`, `#00e5cc`, …) instead of accent tokens, so they don't follow the Neon, Royal, or Vaporwave presets.
2. **Undefined monospace token.** `--font-mono` / `--font-family-mono` are used but never defined, so code text renders in the sans-serif body font.
3. **Duplicate background token.** `--bg-primary` is defined in `style.css` (`#0d0d1a`), overridden in `theme.css` (`var(--bg-base)` = `#0a0e14`), and set to `#000` in a third rule. Two near-identical page backgrounds exist.
4. **Raw colours.** There are about 130 raw hex colours outside `theme.css`, mainly in `components.css`, `style.css`, `cec-tray.css`, and `responsive.css`.
5. **Small, hover-only actions.** Preset action buttons are 22px and appear only on hover, so touch users can't see them.
6. **Minimal reduced-motion support.** Only one `prefers-reduced-motion` rule exists.
7. **Ad-hoc durations.** Most transitions use literal `0.2s` / `0.15s` / `0.3s` instead of the motion tokens.

## 10. Review checklist (for every UI change)

- [ ] Colours come only from tokens and follow all four presets.
- [ ] Spacing, radii, and durations come from the scales above.
- [ ] Glow is used only for active or focused states.
- [ ] Legible at card opacity 0.4 and 1.0.
- [ ] Works at desktop, tablet, phone, and kiosk sizes; touch targets ≥ 44px.
- [ ] Visible focus ring; reduced-motion respected.
- [ ] Before/after captures reviewed and approved (§5.3).
