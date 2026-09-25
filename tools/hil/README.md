# Hardware-in-the-loop scripts

Scripts in this folder talk to a **real OREI BK-808 matrix**. They are not
pytest tests. They used to live in `tests/` as `test_*.py`, where pytest
collected them and they failed with fixture errors whenever `MATRIX_HOST` was
set (TST-05). pytest only collects `tests/`, so nothing here runs in CI.

Most of these scripts are interactive. They ask for input with `input()`, and
some of them change the live routing or power state. Run them only while you
are watching the matrix.

| Script | What it does | Usage |
| --- | --- | --- |
| `connection.py` | Connects, recalls presets 1-3, prints the status. `-i` starts an interactive preset/status loop. | `python tools/hil/connection.py <ip> [port]` or `MATRIX_HOST=<ip> python tools/hil/connection.py` |
| `all_features.py` | Power off/on (asks you first), switches input 2 and then input 5 to output 1, recalls presets 1-2, prints the status. | `python tools/hil/all_features.py <ip> [port]` |
| `input_names.py` | Prints the input names the matrix reports. Read-only. | `python tools/hil/input_names.py <ip> [port]` |
| `manual.py` | Sends `preset set` over HTTP(S) one preset at a time and asks whether the routing changed. | `python tools/hil/manual.py <ip> [port]` |
| `http_vs_https.py` | Sends the same preset command over HTTP (80) and HTTPS (443) so you can compare the responses. | `python tools/hil/http_vs_https.py <ip> [preset]` |
| `all_formats.py` | Telnet (port 23) probe that tries many preset command spellings and line terminators. It was used to reverse-engineer the protocol. | `python tools/hil/all_formats.py <ip>` |

None of the scripts has a default IP address. The target must always be given
explicitly.

## Future

These are stopgaps. They will be replaced by the scripted hardware-in-the-loop
suite described in `docs/REMEDIATION_PLAN.md` §5.2 (HIL-A…E): for example,
`tools/hil/capture.py` will record golden device responses for the simulator,
and session results will be recorded under `docs/validation/`. When a scripted
HIL check covers what one of these scripts does, delete that script.

pytest tests that really need hardware should use the `hardware` marker
(`@pytest.mark.hardware`). They are deselected by default and run with
`pytest -m hardware`.
