# Device icon provenance and size budget

Provenance record for the SVG icons in `web/assets/icons/svg/` and
`web/assets/favicon.svg`. Written for **UI-22** in
`docs/REMEDIATION_PLAN.md`: *"Device icon set is a bitmap trace of a PNG sprite
of unknown origin/licence; `_icon-paths.json` is 2.9 MB and single icons reach
376 KB ... establish provenance of the current set; if the licence can't be
confirmed, replace it with a permissively licensed set or redraw in-house as
clean vector paths ... Target < 5 KB per icon."*

Enforced by `tests/test_ui_pwa_icons_shortcuts.py` and `tests/test_license_and_protocol_docs.py`.

## Where the icons came from (Historical Background)

The original icon set was auto-traced from external PNG sprites:

| Step | Tool |
| --- | --- |
| Source artwork | PNG sprites named `*_icon*.png`, including `device_icons_set.png` |
| Pre-processing | `scripts/convert-icons-to-svg.js` (Jimp; keeps pixels near the UI teal `#00E5CC`, everything else white) |
| Vectorisation | `potrace` (`optTolerance 0.4`, `optCurve true`) + SVGO |
| Output | one `<path fill="#00e5cc">` per icon on a `viewBox="0 0 1024 1024"` grid |

`scripts/convert-icons-to-svg.js` read its sources from
`C:\Users\ryanh\.gemini\antigravity\brain\03e28c61-...` - a path outside this
repository. **Those PNGs were not in the repository**, so the sprite artwork
could not be re-derived from a clean checkout, and no licence, author or
attribution for it could be established. That left the licence status
**unresolved** and created the provenance risk tracked in **UI-22**.
The auto-traced files also suffered from extreme size inflation: `_icon-paths.json`
reached **2.9 MB** and individual files reached **376 KB** (`htpc.svg`).

## Complete In-House Line Vector Replacement (WP-G1, UI-22 Resolution)

On 2026-10-17, under **WP-G1**, all 57 external SVG icons in `web/assets/icons/svg/`
were completely replaced with original in-house code-authored vector line geometry
(`tools/generate_clean_device_icons.py`) under the project's **Mozilla Public License Version 2.0 (MPL-2.0)**:

* **100% In-House Code-Authored:** Designed directly in code with clean geometric line primitives (`viewBox="0 0 1024 1024"`, `fill="currentColor"` with the even-odd fill rule).
* **Zero Tracing:** The old unlicensed potrace sprite traces were completely discarded.
* **Massive Footprint Reduction:**
  - 57 files: **3,105,918 -> 44,908 bytes (98.6% reduction)** across the entire set.
  - Largest file: **1,498 bytes** (`nintendo_switch.svg`), well below the **5,120 bytes (5 KB)** budget.
  - Smallest file: **478 bytes** (`monitor.svg`).
  - `_icon-paths.json` regenerated: **2,908,419 -> 39,031 bytes (98.7% reduction)**.
* **Licence Status: RESOLVED (In-House MPL-2.0)**
  - All 57 device icons are now original works created within this repository under **MPL-2.0**.
  - The UI-22 distribution blocker and provenance risk are fully resolved.

## Runtime Usage Notes

* **Core UI Inline Icons Unaffected:**
  `IconLibrary.getIconHtml()` in `web/js/utils/icon-library.js`—the primary renderer called by the UI (`icon-picker.js`, profile/preset editors)—continues to render the 24×24 inline SVG paths authored in JavaScript. Its comment notes: *"External SVGs are disabled due to quality issues"*.
* `device_icons_set.png.svg` has been redrawn as a clean 8×8 matrix cross-point switch grid symbol on the 1024×1024 canvas (replacing the previous full-canvas solid black block trace).

## Size budget

Budget: **< 5,120 bytes per SVG** (`docs/REMEDIATION_PLAN.md` target is 5 KB).

| File | Bytes | KiB |
| --- | ---: | ---: |
| `apple_tv.svg` | 629 | 0.6 |
| `atari_2600.svg` | 810 | 0.8 |
| `av_receiver.svg` | 881 | 0.9 |
| `bedroom.svg` | 928 | 0.9 |
| `bluray_player.svg` | 655 | 0.6 |
| `cable_box.svg` | 665 | 0.6 |
| `chromecast.svg` | 619 | 0.6 |
| `curved_tv.svg` | 689 | 0.7 |
| `device_icons_set.png.svg` | 991 | 1.0 |
| `dreamcast.svg` | 842 | 0.8 |
| `fire_tv.svg` | 797 | 0.8 |
| `game_room.svg` | 945 | 0.9 |
| `gamecube.svg` | 838 | 0.8 |
| `gaming_pc.svg` | 672 | 0.7 |
| `gaming_scene.svg` | 937 | 0.9 |
| `generic_device.svg` | 548 | 0.5 |
| `generic_input.svg` | 724 | 0.7 |
| `generic_output.svg` | 578 | 0.6 |
| `hdmi_switch.svg` | 973 | 1.0 |
| `headphones.svg` | 870 | 0.8 |
| `htpc.svg` | 671 | 0.7 |
| `laptop.svg` | 612 | 0.6 |
| `living_room.svg` | 1,135 | 1.1 |
| `mac_mini.svg` | 541 | 0.5 |
| `monitor.svg` | 478 | 0.5 |
| `movie_scene.svg` | 1,010 | 1.0 |
| `music_scene.svg` | 519 | 0.5 |
| `n64.svg` | 825 | 0.8 |
| `nes_console.svg` | 818 | 0.8 |
| `nintendo_switch.svg` | 1,498 | 1.5 |
| `nvidia_shield.svg` | 549 | 0.5 |
| `office_room.svg` | 664 | 0.6 |
| `playstation_5.svg` | 870 | 0.8 |
| `projector.svg` | 1,132 | 1.1 |
| `ps2.svg` | 736 | 0.7 |
| `ps3.svg` | 656 | 0.6 |
| `ps4.svg` | 602 | 0.6 |
| `ps_controller.svg` | 1,191 | 1.2 |
| `roku_stick.svg` | 691 | 0.7 |
| `security_camera.svg` | 826 | 0.8 |
| `sega_genesis.svg` | 826 | 0.8 |
| `server_rack.svg` | 1,204 | 1.2 |
| `settings_gear.svg` | 1,472 | 1.4 |
| `snes_console.svg` | 787 | 0.8 |
| `soundbar.svg` | 650 | 0.6 |
| `speaker.svg` | 688 | 0.7 |
| `sports_scene.svg` | 571 | 0.6 |
| `steam_deck.svg` | 1,038 | 1.0 |
| `subwoofer.svg` | 623 | 0.6 |
| `tablet.svg` | 702 | 0.7 |
| `television.svg` | 535 | 0.5 |
| `turntable.svg` | 774 | 0.8 |
| `wii.svg` | 602 | 0.6 |
| `xbox_360.svg` | 678 | 0.7 |
| `xbox_controller.svg` | 1,004 | 1.0 |
| `xbox_one.svg` | 541 | 0.5 |
| `xbox_series_x.svg` | 598 | 0.6 |

`web/assets/favicon.svg` (908 bytes, referenced by `web/manifest.json` and the
`<link rel="icon">` in `index.html`) is hand-drawn in this repository: flat
rounded rectangles for the matrix panel and its inputs, `#3b82f6`/`#2563eb`
gradient, no external source.

## Rebuilding Clean Icons

```bash
python tools/generate_clean_device_icons.py
```

Generates all 57 SVG files and `_icon-paths.json` from original vector primitives.
`tests/test_ui_pwa_icons_shortcuts.py` fails if any SVG goes over the budget, loses its `viewBox` or stops using `currentColor`.