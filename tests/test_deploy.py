# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from pathlib import Path

import pytest

from calliope.deploy import (
    DeployResult,
    DeployTarget,
    DryRunDeployTarget,
    LocalDeployTarget,
)

# --- DeployResult ---


def test_deploy_result_rejects_negative_duration():
    with pytest.raises(ValueError):
        DeployResult(target_name="local", success=True, duration_ms=-1.0)


def test_deploy_result_rejects_success_with_error():
    with pytest.raises(ValueError):
        DeployResult(target_name="local", success=True, duration_ms=1.0, error="boom")


def test_deploy_result_rejects_empty_target_name():
    with pytest.raises(ValueError):
        DeployResult(target_name="", success=True, duration_ms=1.0)


def test_deploy_result_rejects_negative_files_uploaded():
    with pytest.raises(ValueError):
        DeployResult(target_name="x", success=True, duration_ms=1.0, files_uploaded=-1)


# --- DeployTarget Protocol ---


def test_local_target_satisfies_protocol(tmp_path):
    assert isinstance(LocalDeployTarget(tmp_path / "dest"), DeployTarget)


def test_dryrun_target_satisfies_protocol():
    assert isinstance(DryRunDeployTarget(), DeployTarget)


def test_object_without_deploy_does_not_satisfy_protocol():
    class Stub:
        @property
        def name(self) -> str:
            return "stub"

    assert not isinstance(Stub(), DeployTarget)


# --- LocalDeployTarget ---


def _seed_site(root: Path, files: dict[str, bytes]) -> None:
    for path, content in files.items():
        full = root / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(content)


def test_local_deploy_copies_files(tmp_path):
    src = tmp_path / "site"
    dest = tmp_path / "dest"
    _seed_site(src, {"index.html": b"<html/>", "css/main.css": b"body{}"})
    target = LocalDeployTarget(dest)
    result = target.deploy(src)
    assert result.success
    assert result.files_uploaded == 2
    assert result.bytes_uploaded == len(b"<html/>") + len(b"body{}")
    assert (dest / "index.html").read_bytes() == b"<html/>"
    assert (dest / "css/main.css").read_bytes() == b"body{}"


def test_local_deploy_creates_destination_if_missing(tmp_path):
    src = tmp_path / "site"
    dest = tmp_path / "deeply" / "nested" / "dest"
    _seed_site(src, {"a.html": b"a"})
    LocalDeployTarget(dest).deploy(src)
    assert dest.is_dir()


def test_local_deploy_clear_existing_replaces_destination(tmp_path):
    src = tmp_path / "site"
    dest = tmp_path / "dest"
    _seed_site(src, {"a.html": b"new"})
    dest.mkdir()
    (dest / "stale.html").write_bytes(b"stale")
    LocalDeployTarget(dest, clear_existing=True).deploy(src)
    assert (dest / "a.html").read_bytes() == b"new"
    assert not (dest / "stale.html").exists()


def test_local_deploy_default_does_not_clear_destination(tmp_path):
    src = tmp_path / "site"
    dest = tmp_path / "dest"
    _seed_site(src, {"a.html": b"new"})
    dest.mkdir()
    (dest / "stale.html").write_bytes(b"stale")
    LocalDeployTarget(dest).deploy(src)
    assert (dest / "stale.html").exists()


def test_local_deploy_skips_symlinks(tmp_path):
    src = tmp_path / "site"
    dest = tmp_path / "dest"
    external = tmp_path / "secret.txt"
    external.write_bytes(b"secret")
    _seed_site(src, {"index.html": b"<html/>"})
    (src / "linked.txt").symlink_to(external)

    result = LocalDeployTarget(dest).deploy(src)

    assert result.success
    assert result.files_uploaded == 1
    assert (dest / "index.html").exists()
    assert not (dest / "linked.txt").exists()


def test_local_deploy_rejects_destination_under_source(tmp_path):
    src = tmp_path / "site"
    dest = src / "deploy"
    _seed_site(src, {"index.html": b"<html/>"})

    result = LocalDeployTarget(dest).deploy(src)

    assert not result.success
    assert result.error_type == "ValueError"
    assert not dest.exists()


def test_local_deploy_reports_failure_for_missing_source(tmp_path):
    target = LocalDeployTarget(tmp_path / "dest")
    result = target.deploy(tmp_path / "nope")
    assert not result.success
    assert result.error_type == "FileNotFoundError"


def test_local_deploy_rejects_non_path_local_dir(tmp_path):
    target = LocalDeployTarget(tmp_path / "dest")
    result = target.deploy("/tmp/nope")  # type: ignore[arg-type]
    assert not result.success
    assert result.error_type == "TypeError"


def test_local_deploy_rejects_non_path_destination():
    with pytest.raises(TypeError):
        LocalDeployTarget("/tmp/x")  # type: ignore[arg-type]


def test_local_deploy_target_name():
    target = LocalDeployTarget(Path("/tmp/x"))
    assert target.name == "local:/tmp/x"


def test_local_deploy_target_url_is_destination_path(tmp_path):
    src = tmp_path / "site"
    dest = tmp_path / "dest"
    _seed_site(src, {"a.html": b"a"})
    result = LocalDeployTarget(dest).deploy(src)
    assert result.target_url == str(dest)


# --- DryRunDeployTarget ---


def test_dryrun_counts_files_and_bytes(tmp_path):
    src = tmp_path / "site"
    _seed_site(src, {"a.html": b"x" * 5, "b.html": b"y" * 7, "c.html": b"z" * 2})
    result = DryRunDeployTarget().deploy(src)
    assert result.success
    assert result.files_uploaded == 3
    assert result.bytes_uploaded == 14


def test_dryrun_skips_symlinks(tmp_path):
    src = tmp_path / "site"
    external = tmp_path / "secret.txt"
    external.write_bytes(b"secret")
    _seed_site(src, {"index.html": b"abc"})
    (src / "linked.txt").symlink_to(external)

    result = DryRunDeployTarget().deploy(src)

    assert result.success
    assert result.files_uploaded == 1
    assert result.bytes_uploaded == 3


def test_dryrun_does_not_write_anything(tmp_path):
    src = tmp_path / "site"
    _seed_site(src, {"a.html": b"x"})
    DryRunDeployTarget().deploy(src)
    # No new directories created in tmp_path beyond the site itself.
    assert {p.name for p in tmp_path.iterdir()} == {"site"}


def test_dryrun_target_url_is_none(tmp_path):
    src = tmp_path / "site"
    _seed_site(src, {"a.html": b"x"})
    result = DryRunDeployTarget().deploy(src)
    assert result.target_url is None


def test_dryrun_reports_failure_for_missing_source(tmp_path):
    result = DryRunDeployTarget().deploy(tmp_path / "nope")
    assert not result.success
    assert result.error_type == "FileNotFoundError"


def test_dryrun_target_name():
    assert DryRunDeployTarget().name == "dryrun"
