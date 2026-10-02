"""Policy regression checks; these do not validate production-vLLM compatibility."""
import json
from pathlib import Path
import shutil

import pytest

from labs.check_versions import validate

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repository(tmp_path):
    for relative in (
        "versions/manifest.json", "mini_vllm/__init__.py", "pyproject.toml",
        "maintainers/source-map.json", "phase2/releases/v0.29.0.md",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def edit_manifest(root, change):
    path = root / "versions/manifest.json"
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


def test_repository_versions_agree():
    assert validate(ROOT) == []


def test_package_version_drift_is_rejected(repository):
    path = repository / "pyproject.toml"
    path.write_text(path.read_text().replace('version = "0.1.0"', 'version = "0.2.0"'))
    assert any("version mismatch" in e for e in validate(repository))


def test_floating_upstream_reference_is_rejected(repository):
    edit_manifest(repository, lambda d: d["upstream_baseline"].update(commit="main"))
    assert any("immutable commit" in e for e in validate(repository))


def test_missing_release_note_is_rejected(repository):
    (repository / "phase2/releases/v0.29.0.md").unlink()
    assert any("Missing local file" in e for e in validate(repository))


def test_duplicate_release_is_rejected(repository):
    edit_manifest(repository, lambda d: d["releases"].append(dict(d["releases"][0])))
    assert any("Duplicate release" in e for e in validate(repository))


def test_release_note_must_stay_inside_repository(repository):
    edit_manifest(repository, lambda d: d["releases"][0].update(analysis="../outside.md"))
    assert any("inside the repository" in e for e in validate(repository))


def test_nonbaseline_requires_comparison_commit(repository):
    edit_manifest(repository, lambda d: d["releases"][0].update(status="source-only"))
    assert any("needs comparison base" in e for e in validate(repository))


def test_source_map_drift_is_rejected(repository):
    path = repository / "maintainers/source-map.json"
    data = json.loads(path.read_text())
    data["commit"] = "a" * 40
    path.write_text(json.dumps(data))
    assert any("Source-map commit" in e for e in validate(repository))
