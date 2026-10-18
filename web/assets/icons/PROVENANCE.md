# Device icon provenance and size budget

Provenance record for the SVG icons in `web/assets/icons/svg/` and
`web/assets/favicon.svg`. Written for **UI-22** in
`docs/REMEDIATION_PLAN.md`: *"Device icon set is a bitmap trace of a PNG sprite
of unknown origin/licence; `_icon-paths.json` is 2.9 MB and single icons reach
376 KB ... establish provenance of the current set; if the licence can't be
confirmed, replace it with a permissively licensed set or redraw in-house as
clean vector paths ... Target < 5 KB per icon."*

Enforced by `tests/test_ui_pwa_icons_shortcuts.py`.

## Where the icons come from

The set was **not** drawn in-house. It was auto-traced from PNG sprites:

| Step | Tool |
| --- | --- |
| Source artwork | PNG sprites named `*_icon*.png`, including `device_icons_set.png` |
| Pre-processing | `scripts/convert-icons-to-svg.js` (Jimp; keeps pixels near the UI teal `#00E5CC`, everything else white) |
| Vectorisation | `potrace` (`optTolerance 0.4`, `optCurve true`) + SVGO |
| Output | one `<path fill="#00e5cc">` per icon on a `viewBox="0 0 1024 1024"` grid |

`scripts/convert-icons-to-svg.js` reads its sources from
`C:\Users\ryanh\.gemini\antigravity\brain\03e28c61-...` - a path outside this
repository. **Those PNGs are not in the repository**, so the sprite artwork
cannot be re-derived from a clean checkout, and no licence, author or
attribution for it could be established. The tracer also recorded only what the
pixel grid resolved to, which is why the outlines carried thousands of
sub-pixel steps and single icons reached **376 KB** (`htpc.svg` before this
change).

## What changed on 2026-10-17 (WP-E2, UI-22)

`scripts/optimize_device_icons.py` re-traced every icon at the resolution the UI
actually draws it at (192 px grid), re-fitted the contours as clean Catmull-Rom
cubics on integer coordinates, dropped tracing speckle, and rewrote each file as
a single compact path:

* **57 files, 3,105,918 -> 128,398 bytes (95.9% smaller).**
* **Largest file: 5,000 bytes** (`xbox_controller.svg`), budget 5,120 bytes.
* `_icon-paths.json` regenerated from the new paths: **2,908,419 -> 123,718 bytes**.
* Fill is now `currentColor`, so the files inherit the surrounding text colour
  when they are inlined; `viewBox` is unchanged.

The pipeline is lossy by design (it drops the tracing hairline work that no
22-48 px display can resolve), so it refuses to re-trace a file it already
wrote unless `--force` is passed; re-running is a no-op.

### Licence status: still open

This change makes the assets *maintainable*, not *licence-clean*. The new
geometry is a derivative of the same unlicensed PNG sprites, so the provenance
risk recorded in UI-22 is unchanged:

* the sprite artwork is **not** redistributable until its licence is confirmed,
  and
* the release gate *"Licence audit of every bundled asset ... release blocked
  until UI-22 is resolved"* in `docs/REMEDIATION_PLAN.md` §4.3 stays **open**.

The clean fix is still the one the plan asks for: replace this set with
permissively licensed line icons (MIT/ISC) or redraw in-house, matching the
inline icons in `web/js/utils/icon-library.js`. Nothing in the running UI blocks
that change - see below.

## Findings worth keeping

* **The UI does not load these files.** `IconLibrary.getIconHtml()` -
   the only icon renderer the UI calls (`icon-picker.js`, profile/preset
   editors) - always returns the inline 24x24 icons and its own comment says
   *"External SVGs are disabled due to quality issues"*. The only consumer of
   these files, `IconLibrary.getIconElement()`, has no callers. The directory
   is therefore dead weight today, which is why replacing it is low risk.
* **Seven files are sprite sheets, not single devices**: `apple_tv`,
  `bluray_player`, `cable_box`, `fire_tv`, `mac_mini`, `roku_stick` and
  `xbox_series_x` rasterise to a grid of 15-22 device glyphs, because the
  converter traced the whole sheet into each file.
* **`device_icons_set.png.svg` has no icon in it.** It contains a loop covering
   the full `0 0 1024 1024` canvas, so with the non-zero fill rule it renders as
   a solid block; the 389 glyph loops inside it are absorbed. It is kept only as
   the record of the sprite trace.
* Fine interior detail is lost by the budget pass (mean silhouette overlap with
   the pre-2026-10-17 drawings is 0.89; the sprite sheets and
   `atari_2600.svg`, which are mostly hairline work, are the outliers). For a
   22-48 px icon that detail was sub-pixel anyway.

## Size budget

Budget: **< 5,120 bytes per SVG** (`docs/REMEDIATION_PLAN.md` target is 5 KB).

| File | Bytes | KiB |
| --- | ---: | ---: |
| `apple_tv.svg` | 3,450 | 3.4 |
| `atari_2600.svg` | 765 | 0.7 |
| `av_receiver.svg` | 702 | 0.7 |
| `bedroom.svg` | 3,667 | 3.6 |
| `bluray_player.svg` | 3,579 | 3.5 |
| `cable_box.svg` | 3,369 | 3.3 |
| `chromecast.svg` | 422 | 0.4 |
| `curved_tv.svg` | 732 | 0.7 |
| `device_icons_set.png.svg` | 139 | 0.1 |
| `dreamcast.svg` | 2,085 | 2.0 |
| `fire_tv.svg` | 3,088 | 3.0 |
| `game_room.svg` | 3,760 | 3.7 |
| `gamecube.svg` | 1,524 | 1.5 |
| `gaming_pc.svg` | 4,565 | 4.5 |
| `gaming_scene.svg` | 1,729 | 1.7 |
| `generic_device.svg` | 687 | 0.7 |
| `generic_input.svg` | 1,491 | 1.5 |
| `generic_output.svg` | 969 | 0.9 |
| `hdmi_switch.svg` | 2,510 | 2.5 |
| `headphones.svg` | 3,940 | 3.8 |
| `htpc.svg` | 4,701 | 4.6 |
| `laptop.svg` | 1,073 | 1.0 |
| `living_room.svg` | 2,280 | 2.2 |
| `mac_mini.svg` | 2,497 | 2.4 |
| `monitor.svg` | 3,469 | 3.4 |
| `movie_scene.svg` | 2,212 | 2.2 |
| `music_scene.svg` | 2,749 | 2.7 |
| `n64.svg` | 1,049 | 1.0 |
| `nes_console.svg` | 1,460 | 1.4 |
| `nintendo_switch.svg` | 1,453 | 1.4 |
| `nvidia_shield.svg` | 949 | 0.9 |
| `office_room.svg` | 3,300 | 3.2 |
| `playstation_5.svg` | 980 | 1.0 |
| `projector.svg` | 1,507 | 1.5 |
| `ps2.svg` | 3,582 | 3.5 |
| `ps3.svg` | 1,438 | 1.4 |
| `ps4.svg` | 2,614 | 2.6 |
| `ps_controller.svg` | 2,967 | 2.9 |
| `roku_stick.svg` | 3,122 | 3.0 |
| `security_camera.svg` | 1,942 | 1.9 |
| `sega_genesis.svg` | 1,283 | 1.3 |
| `server_rack.svg` | 2,485 | 2.4 |
| `settings_gear.svg` | 1,764 | 1.7 |
| `snes_console.svg` | 1,327 | 1.3 |
| `soundbar.svg` | 2,832 | 2.8 |
| `speaker.svg` | 3,236 | 3.2 |
| `sports_scene.svg` | 3,730 | 3.6 |
| `steam_deck.svg` | 2,199 | 2.1 |
| `subwoofer.svg` | 3,601 | 3.5 |
| `tablet.svg` | 269 | 0.3 |
| `television.svg` | 1,346 | 1.3 |
| `turntable.svg` | 960 | 0.9 |
| `wii.svg` | 3,049 | 3.0 |
| `xbox_360.svg` | 1,050 | 1.0 |
| `xbox_controller.svg` | 5,000 | 4.9 |
| `xbox_one.svg` | 2,323 | 2.3 |
| `xbox_series_x.svg` | 3,484 | 3.4 |

`web/assets/favicon.svg` (908 bytes, referenced by `web/manifest.json` and the
`<link rel="icon">` in `index.html`) is hand-drawn in this repository: flat
rounded rectangles for the matrix panel and its inputs, `#3b82f6`/`#2563eb`
gradient, no external source.

## Rebuilding

```bash
python scripts/optimize_device_icons.py           # rewrite any traced icon
python scripts/optimize_device_icons.py --check   # report only, write nothing
python scripts/optimize_device_icons.py --render out.png television
```

Standard library only (Pillow is used solely by `--render`).
`tests/test_ui_pwa_icons_shortcuts.py` fails if any SVG goes back over the
budget, loses its `viewBox` or stops using `currentColor`.