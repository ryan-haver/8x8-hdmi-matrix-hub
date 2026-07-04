"""Batch-replace _LOG.error(f\"...{e}...\") with _LOG.exception(...) in except blocks.

This adds stack traces to error logs without changing control flow.
Operates on all .py files under src/rest_api/.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "src/rest_api")
files = list(ROOT.rglob("*.py"))

# Match _LOG.error(f"...{e}...") at 4+ space indent (inside except blocks).
# The pattern is intentionally specific to except-block log lines:
#   - 4+ spaces of indentation (inside a function / handler)
#   - _LOG.error( with f-string containing {e} or {exc}
PATTERN = re.compile(
    r'^(?P<indent>[ ]{4,})_LOG\.error\(f"(?P<msg>[^"]*\{(?:e|exc)\}[^"]*)"\)',
    re.MULTILINE,
)

total_lines = 0
total_files = 0
for f in files:
    content = f.read_text(encoding="utf-8")
    matches = list(PATTERN.finditer(content))
    if not matches:
        continue
    new_content = PATTERN.sub(
        lambda m: f'{m.group("indent")}_LOG.exception(f"{m.group("msg")}")',
        content,
    )
    f.write_text(new_content, encoding="utf-8")
    print(f"Updated {f}: {len(matches)} sites")
    total_lines += len(matches)
    total_files += 1

print(f"\nTotal: {total_lines} sites updated across {total_files} files")