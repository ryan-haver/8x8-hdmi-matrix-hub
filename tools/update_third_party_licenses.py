"""Copy runtime distribution license notices from a verified locked environment.

Install requirements.txt with --require-hashes first, then run this script.
It preserves the license/NOTICE files supplied by those installed wheels;
metadata declarations are recorded rather than interpreted as legal advice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def collect(requirements: Path, output: Path) -> list[dict]:
    packages = re.findall(
        r"^([A-Za-z0-9_.-]+)==([^\s\\]+)", requirements.read_text(encoding="utf-8"), re.MULTILINE
    )
    if not packages:
        raise ValueError("Expected a pinned runtime lock")
    prepared: dict[Path, bytes] = {}
    rows = []
    for name, version in packages:
        dist = metadata.distribution(name)
        if dist.version != version:
            raise ValueError(f"Install the lock first: {name} is {dist.version}, expected {version}")
        info = dist.metadata
        declared = info.get("License-Expression") or info.get("License")
        if not declared:
            raise ValueError(f"No declared license metadata for {name}")
        canonical = re.sub(r"[-_.]+", "-", name).lower()
        files = []
        for item in dist.files or []:
            path = str(item).replace("\\", "/")
            if ".dist-info/" not in path or not any(
                term in item.name.lower() for term in ("license", "licence", "copying", "notice")
            ):
                continue
            relative = path.split("/licenses/", 1)[-1] if "/licenses/" in path else item.name
            destination = output / canonical / relative
            if not destination.resolve().is_relative_to(output.resolve()):
                raise ValueError(f"Invalid license path for {name}")
            data = Path(dist.locate_file(item)).read_bytes()
            prepared[destination] = data
            files.append({
                "path": destination.relative_to(output).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
        if not files:
            raise ValueError(f"No license files supplied by the {name} distribution")
        urls = [value.partition(", ") for value in info.get_all("Project-URL", [])]
        source = next(
            (url for title, _, url in urls if title.lower() in {"repository", "source", "source code", "github: repo"}),
            info.get("Home-page") or next((url for _, _, url in urls), ""),
        )
        rows.append({
            "name": info["Name"], "version": version, "declared_license": declared,
            "source": source, "files": sorted(files, key=lambda entry: entry["path"]),
        })
    # Validate all distributions before replacing any generated files.
    for path, data in prepared.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    rows.sort(key=lambda row: row["name"].lower())
    output.mkdir(parents=True, exist_ok=True)
    (output / "manifest.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", type=Path, default=ROOT / "requirements.txt")
    parser.add_argument("--out", type=Path, default=ROOT / "LICENSES" / "python")
    args = parser.parse_args()
    rows = collect(args.requirements, args.out)
    print(f"Recorded {len(rows)} locked runtime distributions in {args.out}")


if __name__ == "__main__":
    main()
