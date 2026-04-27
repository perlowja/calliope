# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import pytest

from calliope.assets import bundle_assets, collect_assets


def _seed_source(root, files):
    for path, content in files.items():
        full = root / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(content)


def test_collect_assets_reads_every_regular_file(tmp_path):
    _seed_source(
        tmp_path,
        {
            "main.css": b"body { color: red; }",
            "js/app.js": b"console.log('hi');",
            "img/logo.svg": b"<svg/>",
        },
    )
    assets = collect_assets(tmp_path)
    by_path = {a.logical_path: a for a in assets}
    assert set(by_path) == {"main.css", "js/app.js", "img/logo.svg"}
    assert by_path["main.css"].content == b"body { color: red; }"


def test_collect_assets_assigns_media_type_when_known(tmp_path):
    _seed_source(tmp_path, {"main.css": b"x"})
    assets = collect_assets(tmp_path)
    assert assets[0].media_type == "text/css"


def test_collect_assets_excludes_listed_paths(tmp_path):
    _seed_source(tmp_path, {"keep.css": b"x", "skip.css": b"y"})
    assets = collect_assets(tmp_path, excludes=["skip.css"])
    paths = {a.logical_path for a in assets}
    assert paths == {"keep.css"}


def test_collect_assets_skips_symlinks(tmp_path):
    src = tmp_path / "src"
    external = tmp_path / "external.css"
    external.write_bytes(b"secret")
    _seed_source(src, {"keep.css": b"body{}"})
    (src / "linked.css").symlink_to(external)

    assets = collect_assets(src)

    assert [asset.logical_path for asset in assets] == ["keep.css"]


def test_collect_assets_returns_empty_for_empty_dir(tmp_path):
    assets = collect_assets(tmp_path)
    assert assets == ()


def test_collect_assets_raises_for_nonexistent_dir(tmp_path):
    missing = tmp_path / "does-not-exist"
    with pytest.raises(FileNotFoundError):
        collect_assets(missing)


def test_bundle_assets_writes_hashed_files_to_output(tmp_path):
    src = tmp_path / "src"
    out = tmp_path / "out"
    _seed_source(src, {"main.css": b"body { color: red; }"})
    manifest = bundle_assets(src, out)
    published = manifest.published("main.css")
    assert published is not None
    assert (out / published).exists()
    assert (out / published).read_bytes() == b"body { color: red; }"


def test_bundle_assets_preserves_subdirectory_layout(tmp_path):
    src = tmp_path / "src"
    out = tmp_path / "out"
    _seed_source(src, {"css/main.css": b"x", "js/app.js": b"y"})
    manifest = bundle_assets(src, out)
    css_published = manifest.published("css/main.css")
    js_published = manifest.published("js/app.js")
    assert css_published.startswith("css/main.")
    assert js_published.startswith("js/app.")
    assert (out / css_published).exists()
    assert (out / js_published).exists()


def test_bundle_assets_creates_missing_output_dir(tmp_path):
    src = tmp_path / "src"
    out = tmp_path / "out" / "nested" / "deep"
    _seed_source(src, {"x.css": b"x"})
    bundle_assets(src, out)
    assert out.is_dir()


def test_bundle_assets_rerun_with_nested_output_dir_is_idempotent(tmp_path):
    src = tmp_path / "src"
    out = src / "dist"
    _seed_source(src, {"main.css": b"body{}", "img/logo.svg": b"<svg/>"})

    first = bundle_assets(src, out)
    second = bundle_assets(src, out)

    assert dict(first.entries) == dict(second.entries)


def test_bundle_assets_rejects_non_path_inputs():
    with pytest.raises(TypeError):
        bundle_assets("/tmp/x", "/tmp/y")  # type: ignore[arg-type]


def test_bundle_assets_hash_changes_for_different_content(tmp_path):
    src1 = tmp_path / "src1"
    src2 = tmp_path / "src2"
    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"
    _seed_source(src1, {"x.css": b"AAA"})
    _seed_source(src2, {"x.css": b"BBB"})
    m1 = bundle_assets(src1, out1)
    m2 = bundle_assets(src2, out2)
    assert m1.published("x.css") != m2.published("x.css")
