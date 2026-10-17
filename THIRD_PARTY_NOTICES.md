# Third-Party Notices and License Audit

This document records the third-party software, bundled assets, fonts, and icons included in or used by the OREI BK-808 HDMI Matrix integration repository, along with their provenance, copyright, and licensing status.

---

## 1. Primary Project License

The OREI BK-808 HDMI Matrix Hub is licensed under the **Mozilla Public License Version 2.0 (MPL-2.0)**.
See the full license text in [LICENSE](LICENSE).

---

## 2. Bundled Asset Audit (Icons, Brand Assets, Fonts)

A complete audit of all graphical and font assets in this repository was conducted for release gate compliance (**UI-22**, `docs/REMEDIATION_PLAN.md` §4.3 & §6).

### 2.1 Bundled Device Icons (`web/assets/icons/svg/`) — ✅ Resolved via In-House Replacement (UI-22)

- **Location:** `web/assets/icons/svg/*.svg` (57 SVG files) and `web/assets/icons/svg/_icon-paths.json`.
- **Full Provenance Record:** Documented in [web/assets/icons/PROVENANCE.md](web/assets/icons/PROVENANCE.md).
- **Historical Background & Provenance Risk (UI-22):**
  - The repository's original icon set was auto-traced from external PNG sprite sheets (`device_icons_set.png`, `*_icon*.png`) using `scripts/convert-icons-to-svg.js` (Jimp) and `potrace` (`optTolerance 0.4`, `optCurve true`).
  - Those source PNGs were located outside this repository (`C:\Users\ryanh\.gemini\antigravity\brain\...`) and **were never part of this repository**.
  - Because no license, author, or copyright information could be established for the original sprites, the traced vectors had an **unresolved** license status, creating the provenance risk tracked under **UI-22**.
- **Remediation Executed (WP-G1):**
  - On 2026-10-17, under WP-G1, all 57 external SVG icons were **completely replaced** with original, in-house code-authored vector line geometry (`tools/generate_clean_device_icons.py`) authored under the project's **Mozilla Public License Version 2.0 (MPL-2.0)**.
  - The old unlicensed potrace sprite traces were permanently discarded.
  - Geometry is authored directly in code with clean line art primitives on a `viewBox="0 0 1024 1024"` grid with `fill="currentColor"`.
  - Footprint across all 57 SVG files dropped from 3.1 MB to **44 KB (98.6% reduction)**.
  - `web/assets/icons/svg/_icon-paths.json` was regenerated from the new in-house vector paths, shrinking from 2.9 MB to **39 KB (98.7% reduction)**.
  - **Size Budget Enforcement:** Every SVG icon is constrained to **< 5,120 bytes** (< 5 KB), enforced by `tests/test_ui_pwa_icons_shortcuts.py` and `tests/test_license_and_protocol_docs.py`. Actual sizes range from 458 bytes (`monitor.svg`) to 1,478 bytes (`nintendo_switch.svg`).
- **License Status: RESOLVED (In-House MPL-2.0)**
  - All 57 device icons and `_icon-paths.json` are now 100% original works created in this repository under **MPL-2.0**.
  - The UI-22 distribution gate is fully resolved.
- **Runtime Usage:**
  - `IconLibrary.getIconHtml()` in `web/js/utils/icon-library.js`—the primary icon renderer called by the UI (`icon-picker.js`, preset/profile editors)—renders inline 24×24 SVG paths directly from JavaScript code (*"External SVGs are disabled due to quality issues"*). Core UI inline icon rendering remains visually unchanged.
  - `device_icons_set.png.svg` has been replaced with a clean 8×8 matrix cross-point switch grid symbol (eliminating the previous full-canvas solid black block trace artifact).

### 2.2 Project Favicon and Home Assistant Brand Icons — In-House (MPL-2.0)

- **Files:**
  - `web/assets/favicon.svg` (908 bytes)
  - `custom_components/hdmi_matrix/brand/icon.png` (256×256 px)
  - `custom_components/hdmi_matrix/brand/icon@2x.png` (512×512 px)
- **Provenance:** Hand-drawn in this repository by Ryan Haver. Consists of geometric rounded rectangles depicting an 8×8 matrix switch panel with `#3b82f6` and `#2563eb` linear gradients. The Home Assistant brand icons were rendered directly from `web/assets/favicon.svg` to satisfy HACS brand validation.
- **License:** Mozilla Public License Version 2.0 (MPL-2.0), matching the repository.

### 2.3 Inline Vector Device Icons — In-House (MPL-2.0)

- **File:** `web/js/utils/icon-library.js`
- **Provenance:** Hand-crafted 24×24 vector primitives (`<rect>`, `<circle>`, `<path>`) authored directly in JavaScript for wireframe, detailed, and glyph variants across 16 device categories.
- **License:** Mozilla Public License Version 2.0 (MPL-2.0), matching the repository.

### 2.4 Typography and Web Font Audit — Zero Font Binaries

- **Bundled Font Files:** **None.** No font files (`.woff`, `.woff2`, `.ttf`, `.otf`, `.eot`) are stored or distributed in this repository.
- **External Web Fonts:** **None.** No external font stylesheets (e.g., Google Fonts, Adobe Fonts, Typekit) are referenced in HTML or CSS.
- **Font Stacks:** Web styling (`web/css/style.css`, `web/css/tokens.css`, `web/css/components.css`) relies exclusively on standard client operating system font stacks:
  - System UI font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", Arial, sans-serif`
  - Monospace font stack: `ui-monospace, "SF Mono", "Menlo", "Monaco", "Consolas", "Liberation Mono", "Courier New", monospace`
- **Licensing Impact:** No third-party font licensing obligations apply to this repository.

---

## 3. Third-Party Runtime Python Dependencies

The following third-party Python packages are required by the runtime (`requirements.txt`, `requirements-uc.txt`, `pyproject.toml`):

### 3.1 ucapi

- **Package:** `ucapi` (Version 0.7.0)
- **Project URL:** <https://github.com/unfoldedcircle/core-api-python> / <https://www.unfoldedcircle.com/>
- **Copyright:** Copyright (c) Unfolded Circle ApS
- **License:** Mozilla Public License Version 2.0 (MPL-2.0)
- **Notice:** This component is licensed under the Mozilla Public License 2.0. You may obtain a copy of the License at <https://www.mozilla.org/MPL/2.0/>.

### 3.2 pyee

- **Package:** `pyee` (Version 14.0.0 / >=11.0.0)
- **Project URL:** <https://github.com/jfhbrook/pyee>
- **Copyright:** Copyright (c) 2014-2024 Josh Holbrook
- **License:** MIT License

```text
MIT License

Copyright (c) 2014-2024 Josh Holbrook

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 3.3 aiohttp

- **Package:** `aiohttp` (Version 3.13.3 / >=3.9.0)
- **Project URL:** <https://github.com/aio-libs/aiohttp>
- **Copyright:** Copyright (c) 2013-2024 aiohttp contributors
- **License:** Apache License, Version 2.0 AND MIT License
- **Notice:** Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

### 3.4 psutil

- **Package:** `psutil` (Version 7.2.1 / >=5.9.0)
- **Project URL:** <https://github.com/giampaolo/psutil>
- **Copyright:** Copyright (c) 2009, Jay Loden, Dave Daeschler, Giampaolo Rodola
- **License:** BSD 3-Clause License

```text
Copyright (c) 2009, Jay Loden, Dave Daeschler, Giampaolo Rodola
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 * Neither the name of the psutil authors nor the names of its contributors
   may be used to endorse or promote products derived from this software without
   specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

---

## 4. Development and Test-Only Dependencies (Not Shipped)

The following packages are installed only for local linting, testing, and continuous integration. They are not bundled into production Docker containers or distributed with runtime wheels:

### 4.1 Python Development Tools

- `pytest` (MIT License)
- `pytest-asyncio` (Apache-2.0 License)
- `pytest-aiohttp` (Apache-2.0 License)
- `black` (MIT License)
- `ruff` (MIT / Apache-2.0 License)
- `mypy` (MIT License)
- `cryptography` (Apache-2.0 / BSD-3-Clause)
- `pyyaml` (MIT License)
- `jsonschema` (MIT License)

### 4.2 Node.js Development Tools (`package.json`)

- `@playwright/test`, `@axe-core/playwright` (Apache-2.0 / MPL-2.0)
- `eslint`, `@eslint/js`, `globals` (MIT License)
- `stylelint`, `stylelint-config-recommended` (MIT License)
- `pixelmatch`, `pngjs`, `sharp` (ISC / MIT / Apache-2.0)

---

## 5. Vendor Proprietary Assets & Binary Hygiene (SEC-14)

In accordance with security and repository hygiene requirements (**SEC-14**, `docs/REMEDIATION_PLAN.md` §4.1):

1. **No Vendor Firmware or Binaries:** All proprietary vendor firmware images, Windows flashing utilities (`XP3.exe`), and Control4/RTI binary driver packages (`.c4z`) were purged from the git history and repository.
2. **No Vendor Copyrighted Manuals:** Proprietary vendor PDF manuals were removed; all command specifications and protocol behaviors documented in this repository have been independently reverse-engineered and verified against physical hardware captures.
3. **No Unredacted Device Captures:** All network traces and fixture captures in `tests/fixtures/device/` have MAC addresses, hostnames, and passwords redacted.
