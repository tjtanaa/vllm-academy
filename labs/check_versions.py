"""Validate local version/source relationships; does not verify upstream behavior."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"[0-9a-f]{40}")
VERSION = re.compile(r"\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?")
STATUSES = {"source-baseline", "pending", "source-only", "proposed", "implemented",
            "no-teaching-relevant-change"}


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads((root / "versions/manifest.json").read_text())
        if not isinstance(data, dict):
            return ["Version manifest must be an object"]
        if data.get("schema_version") != 1:
            errors.append("Unsupported manifest schema_version")
        for field in ("academy_version", "mini_engine_version"):
            if not VERSION.fullmatch(str(data.get(field, ""))):
                errors.append(f"Invalid {field}")

        def local_file(value: object) -> Path | None:
            if not isinstance(value, str) or not value:
                errors.append("Missing local document path")
                return None
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"Path must stay inside the repository: {value}")
                return None
            target = root / path
            if not target.is_file():
                errors.append(f"Missing local file: {value}")
                return None
            return target

        mini = data.get("mini_engine_version")
        for path, pattern in (
            ("mini_vllm/__init__.py", r'^__version__\s*=\s*"([^"]+)"'),
            ("pyproject.toml", r'^version\s*=\s*"([^"]+)"'),
        ):
            match = re.search(pattern, (root / path).read_text(), re.M)
            if not match or match.group(1) != mini:
                errors.append(f"Teaching version mismatch: {path}")
        baseline = data.get("upstream_baseline")
        if not isinstance(baseline, dict):
            return errors + ["Missing upstream baseline"]
        if not SHA.fullmatch(str(baseline.get("commit", ""))):
            errors.append("Baseline needs a full immutable commit SHA")
        source_path = local_file(data.get("source_map"))
        if source_path is not None:
            source = json.loads(source_path.read_text())
            for key in ("tag", "commit"):
                if source.get(key) != baseline.get(key):
                    errors.append(f"Source-map {key} differs from baseline")
        releases = data.get("releases")
        if not isinstance(releases, list) or not releases:
            return errors + ["Release index must be a nonempty list"]
        seen: set[str] = set()
        for row in releases:
            if not isinstance(row, dict):
                errors.append("Release row must be an object")
                continue
            tag = row.get("upstream_tag")
            if not isinstance(tag, str) or not tag.startswith("v"):
                errors.append("Release row needs an explicit upstream tag")
                continue
            if tag in seen:
                errors.append(f"Duplicate release: {tag}")
            seen.add(tag)
            if row.get("status") not in STATUSES:
                errors.append(f"Invalid release status: {tag}")
            for key in ("upstream_commit", "comparison_base_commit"):
                value = row.get(key)
                if key == "comparison_base_commit" and value is None:
                    if row.get("status") != "source-baseline":
                        errors.append(f"Non-baseline release needs comparison base: {tag}")
                elif not SHA.fullmatch(str(value)):
                    errors.append(f"Invalid immutable {key}: {tag}")
            local_file(row.get("analysis"))
            if not VERSION.fullmatch(str(row.get("mini_engine_version", ""))):
                errors.append(f"Invalid mapped teaching version: {tag}")
        matching = [row for row in releases if isinstance(row, dict)
                    and row.get("upstream_tag") == baseline.get("tag")
                    and row.get("upstream_commit") == baseline.get("commit")]
        if not matching:
            errors.append("Baseline is not represented in the release index")
    except (OSError, ValueError, AttributeError, TypeError) as exc:
        errors.append(f"Cannot validate repository metadata: {exc}")
    return errors


def main() -> None:
    errors = validate()
    print(json.dumps({"check": "local version/source relationships", "errors": errors}, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
