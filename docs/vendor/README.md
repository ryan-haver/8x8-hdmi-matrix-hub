# Vendor Reference Material (not redistributed)

Earlier versions of this repository included vendor files for the OREI BK-808: firmware images, the user manual, and the Control4 and RTI drivers. They were removed from the repository and its entire git history on 2026-09-24 because this project has no right to redistribute them.

This project does not need any of these files to build or run. They were only used as reference while reverse-engineering the matrix's HTTP and Telnet control protocol, which is documented in our own words in [OREI_API_COMMANDS.md](../OREI_API_COMMANDS.md).

## Where to get them

- **User manual, firmware updates:** the [OREI BK-808 product page](https://orei.com/products/8k-8x8-hdmi-matrix-switcher-4k-120hz-hdcp-2-3-hdr-edid-dolby-vision-atmos-downscaling-bk-808) or OREI support.
- **Control4 / RTI drivers:** request them from OREI support (they are provided for integrators).

Only install firmware obtained directly from the vendor.

## Files formerly in this repository

Use the SHA-256 checksums to confirm you have the same file versions this project was developed against.

| Former path | SHA-256 |
| --- | --- |
| `docs/BK-808 Firmware/MCU_MAIN_BK-808_V1.10.02_202510161359.bin` | `ce1b631c2b8e9783c2afd681c36c147dd18ab11b3534d4b0dae2a99a859c1be0` |
| `docs/BK-808 Firmware/IP_MODULE_RS02_firmware_BK-808_10.01.17_2.00.03_20250630.bin` | `70bf0ef5196e43728bb690938cfa5364cd7d2b87f150b15e99a073ee6e535fc9` |
| `docs/BK-808_User_Manual.pdf` | `2ff120aa9604e9f3946ae41834afcd536f0eda100c40be00061bd5cf65877d99` |
| `docs/BK-808 Control4 Driver.c4z` | `75040dfa6c6f1d41bd0dc0df721a0db0c44c6b8f561c9d101a3d2e91073b663f` |
| `docs/BK-808 Control4 Driver/driver.lua` | `9300ded2e092d3d9e42d1109df8bcc8eb000b556b2394b39ef2e06a51bd519d4` |
| `docs/BK-808 Control4 Driver/driver.xml` | `4f58a23182e992e127c3191927b1f77c8236818b83c9dd75e0a8b7f03a0a1a0d` |
| `docs/BK-808 Control4 Driver/documentation.rtf` | `049e1731d2778e3bd9174c32c6160e0bbef0c73ca55516cec7e2315be3c0d825` |
| `docs/BK-808 RTI Driver/Driver/BK-808_CN_AV.rtidriver` | `d3068059960420eda2caf70a5f0ed6bd48c430ff2a4b7bf03f094c1402318462` |
| `docs/BK-808 RTI Driver/TestProject/Matrix Switch.rti` | `3480a2563efe955064008e08e6ee14fc4ec1f967f45899c629a45ef5ed71b60c` |
| `docs/BK-808 RTI Driver/TestProject/XP3.exe` (RTI Integration Designer) | `8234aed9cd49b967edd375e2acdda3a53c8e503ad25e9dafdf5d9d930007e7fd` |

## Firmware versions this project was developed against

| Component | Version | Build date |
| --- | --- | --- |
| Main MCU | V1.10.02 | 2025-10-16 |
| IP module (RS02) | 10.01.17 / 2.00.03 | 2025-06-30 |

Hardware validation reports in `docs/validation/` record the firmware versions of the device under test.

## Contributor rules

- Do not commit vendor firmware, executables, drivers, manuals, or packet/HAR captures. CI rejects `*.bin`, `*.exe`, `*.c4z`, `*.har`, and large binaries.
- HAR captures of the matrix web UI contain LAN addresses and login payloads; keep them local (they are git-ignored).
- When documenting protocol behaviour learned from vendor material, describe it in your own words and verify it against real hardware.
