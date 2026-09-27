# Web UI tests: smoke, visual baselines, review gallery

Dev-only JS tooling for the web UI (`/ui`, `/kiosk`), implementing the Phase 0
"Minimal JS tooling" and "UI capture baseline" items of
`docs/REMEDIATION_PLAN.md` (§5.3). Nothing here ships in the image.

```bash
npm ci                         # once (Node >= 20)
npx playwright install chromium  # once, for host runs of the smoke tests
```

The Python side (hub + simulator) needs the dev dependencies:
`pip install -r requirements-uc.txt -e ".[dev]"`. The stack finds Python via
`$E2E_PYTHON`, else `.venv` in this checkout or the main checkout, else
`python3`/`python`.

## Commands

| Command | What it does | Where |
| --- | --- | --- |
| `npm run test:e2e` | Smoke tests (`smoke.spec.ts`) | host or container |
| `npm run visual:test` | Compare every catalog entry with the committed baselines | **container only** |
| `npm run visual:update` | Write new/changed baselines (approval step) | **container only** |
| `npm run visual:report` | Open the last Playwright HTML report (baseline / actual / diff) | host |
| `npm run visual:gallery` | Build `ui-gallery/index.html` from the baselines | host or container |
| `node tools/ui/build_gallery.mjs --base origin/main` | Before/after review page against a git ref | host or container |
| `node tools/ui/build_gallery.mjs --viewports kiosk-tab-a11,kiosk-iphone16promax --out <dir>` | Gallery of some viewports only | host or container |
| `npm run lint:js` / `npm run lint:css` | Lint; fail only on violations above the baseline | host |

Extra Playwright arguments go after `--`, e.g.
`npm run visual:test -- --grep "drawer/theme"` or
`npm run visual:update -- --project=kiosk-tab-a11`. Any `--project` argument
replaces the default list of visual projects (the smoke project still runs
first as a dependency; add `--no-deps` to skip it).

## The stack

`playwright.config.ts` starts `support/start-stack.mjs` as its `webServer`:
`tools/dev_stack.py` on fixed ports (hub `18080`, simulator `18443` HTTPS,
`12323` Telnet, `18444` control) with a **fresh temp copy** of
`fixtures/data/` as the hub data dir. Locally an already running stack on
those ports is reused (`reuseExistingServer`), so you can keep
`node tests/e2e/support/start-stack.mjs` running while iterating.

`fixtures/data/` is the seeded hub state, in the managers' on-disk schemas:
profiles (one passcode-protected, passcode `1234`), CEC macros, v2 scenes (one
passcode-protected), built-in + user shortcuts, a dashboard layout with every
card type, device settings (icons, preset names, favourites), UI preferences
and Flic buttons. The simulator starts from `tools/simulator/states/default.json`.

## Visual baselines

- **Catalog** (`visual/catalog.ts`): one named entry per reviewable UI state
  (`<area>/<element>/<state>`). The catalog is the checklist of UI elements: a
  new component or state is not done until it has an entry.
- **Matrix**: Tron Classic x every entry x five viewport projects (Neon,
  Royal, Vaporwave x entries marked `themed` x desktop and both kiosk
  devices; plus one paused frame with the Tron background on, at desktop and
  both kiosk devices). Sizes are in `support/viewports.ts`:

  | Project | Viewport (CSS px) | Scale | Mobile / touch | Device |
  | --- | --- | --- | --- | --- |
  | `desktop` | 1440x900 | 1 | no / no | desktop browser |
  | `tablet` | 1024x768 landscape | 1 | no / yes | iPad class |
  | `phone` | 390x844 portrait | 1 | yes / yes | iPhone 12-15 class |
  | `kiosk-tab-a11` | 1340x800 landscape | 1 | yes / yes | Samsung Galaxy Tab A11 (SM-X133), 8.7", Android Chrome. **PROVISIONAL** |
  | `kiosk-iphone16promax` | 440x956 portrait | 3 | yes / yes | Apple iPhone 16 Pro Max |

  Kiosk devices vary; these two are the owner's test kiosks (owner decision
  2026-09-25). `kiosk-tab-a11` uses the panel resolution at scale 1 because
  the browser's CSS viewport is not confirmed yet: open
  whatismyviewport.com on the device (in the browser mode the kiosk really
  uses), update `support/viewports.ts` and re-baseline with
  `npm run visual:update -- --project=kiosk-tab-a11`. `kiosk-iphone16promax`
  takes its user agent, screen and scale from Playwright's
  "iPhone 16 Pro Max" descriptor but uses the full 440x956 screen as the
  viewport (the descriptor's 440x763 is Safari with its bars showing).
  Every project renders with Chromium; screenshots are taken at CSS scale, so
  each baseline is viewport-sized.
- **Files**: `visual/__snapshots__/<viewport>/[themes/<preset>/]<entry>.png`
  (Git LFS) and `visual/__snapshots__/catalog.json` (entry descriptions and
  notes, read by the gallery).
- **Determinism**: fresh browser context per capture, seeded localStorage,
  frozen `Date`, seeded `Math.random`, transitions/animations/caret disabled,
  Tron background off, pointer parked, simulator reset before every capture,
  hub writes blocked, and the hub's WebSocket `status` broadcasts filtered per
  page (they are sent to every open page and would otherwise re-render pages
  at times set by other tests). The pinned container
  (`mcr.microsoft.com/playwright:v1.63.0-noble`) makes fonts and rendering
  identical locally and in CI; host screenshots will not match.
- **Container**: `tools/ui/run-in-container.mjs` mounts the repo at `/work`,
  keeps its own `node_modules` and a pip/npm/venv cache in named Docker
  volumes (`hdmi-hub-ui-node-modules`, `hdmi-hub-ui-cache`) and runs
  `tools/ui/container-setup.sh` (the same setup the CI `ui` job uses).
  Snapshots, `test-results/` and `playwright-report/` are written inside the
  container and copied back to the repo at the end, because Docker Desktop
  bind mounts on Windows intermittently fail concurrent writes with
  `ENOMEM`. The container is named `hdmi-hub-ui-<pid>-<time>` and is stopped
  if the runner is interrupted.
- **Parallelism**: `E2E_WORKERS` (default 4; the container runner defaults to
  2 because Docker Desktop VMs are often small, and 4 Chromium workers plus
  the stack exhausted a 3 GB VM). The smoke project runs first because it
  changes simulator state (visual projects depend on it; `--no-deps` skips
  it).
- **Removing an entry**: Playwright never deletes obsolete snapshots; delete
  the entry's PNGs by hand (the gallery lists them as entries without
  catalog metadata).

### Approving a visual change

1. `npm run visual:test` fails and lists the changed entries; inspect
   `npm run visual:report`.
2. If intended: `npm run visual:update`, then
   `node tools/ui/build_gallery.mjs --base HEAD` for a before/after page.
3. Commit the baselines on their own: `visual: approve <entries> - <reason>`.
   `CODEOWNERS` makes the project owner the required reviewer.

In CI (`ui` job) a failing comparison uploads `playwright-report` and a
`ui-review` gallery artifact, and a PR comment lists every changed entry.

### Git LFS

Snapshots are LFS objects (`.gitattributes`). Because `core.hooksPath` is
`.githooks`, the standard LFS hooks (`pre-push`, `post-checkout`,
`post-commit`, `post-merge`) are committed there; install git-lfs and run
`git lfs pull` after cloning.

## Lint baselines (existing findings reported, new ones blocking)

`web/` stays unchanged until the UI baseline is signed off, so existing lint
findings are recorded rather than fixed:

- **ESLint** (`eslint.config.js`, flat config, `@eslint/js` recommended,
  browser globals + the app's cross-file globals derived from `web/js`):
  existing findings are in `eslint-suppressions.json` (ESLint bulk
  suppressions). `npm run lint:js` fails only on new violations;
  `npm run lint:js:all` shows everything; after fixing code run
  `npm run lint:js:prune` to shrink the file.
- **Stylelint** (`stylelint.config.js`, `stylelint-config-recommended` +
  `hub/no-raw-colors`, which flags literal colours outside
  `web/css/theme.css`): Stylelint has no suppressions file, so
  `tools/ui/stylelint-baseline.mjs` compares per-file/per-rule counts with
  `tools/ui/stylelint-baseline.json`. `npm run lint:css` prints all findings
  and fails when a count goes up; `npm run lint:css:all` lists them with line
  numbers; `npm run lint:css:baseline` rewrites the baseline after fixes;
  `npm run lint:css:strict` fails on any finding (the end goal).

Both run non-blocking in CI today; make them blocking by removing
`continue-on-error` from the two lint steps of the `ui` job.
