# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import pytest

from calliope.pages import Hero, render_hero
from calliope.templates import detect_blocks


def test_render_hero_minimal():
    out = render_hero(Hero(title="Welcome"))
    assert "<!-- BLOCK:hero -->" in out
    assert "<!-- /BLOCK:hero -->" in out
    assert ">Welcome<" in out


def test_render_hero_includes_subtitle_when_set():
    out = render_hero(Hero(title="T", subtitle="S"))
    assert ">S<" in out


def test_render_hero_omits_subtitle_when_unset():
    out = render_hero(Hero(title="T"))
    assert "hero-subtitle" not in out


def test_render_hero_with_background_image():
    out = render_hero(Hero(title="T", background_image="/img/bg.jpg"))
    assert "background-image:url('/img/bg.jpg');" in out


def test_render_hero_with_gradient():
    out = render_hero(Hero(title="T", background_gradient="linear-gradient(0deg,#fff,#000)"))
    assert "background:linear-gradient(0deg,#fff,#000);" in out


def test_render_hero_renders_cta_when_both_label_and_href_provided():
    out = render_hero(Hero(title="T", cta_label="Learn more", cta_href="/about.html"))
    assert 'href="/about.html"' in out
    assert ">Learn more<" in out


def test_render_hero_escapes_url_in_attributes():
    out = render_hero(Hero(title="T", cta_label="Learn more", cta_href='/x"><img>'))
    assert 'href="/x&quot;&gt;&lt;img&gt;"' in out
    assert '/x"><img>' not in out
    assert "<img>" not in out


def test_render_hero_omits_cta_if_only_label_set():
    out = render_hero(Hero(title="T", cta_label="Click"))
    assert ">Click<" not in out


def test_render_hero_rejects_unsafe_background_image():
    with pytest.raises(ValueError, match="background_image"):
        Hero(title="T", background_image="x'); color:red; /*")


def test_render_hero_rejects_background_image_with_html_entity_payload():
    with pytest.raises(ValueError, match="background_image"):
        Hero(title="T", background_image="x&#39); color:red;/*")


def test_render_hero_rejects_background_gradient_with_html_entity_payload():
    with pytest.raises(ValueError, match="background_gradient"):
        Hero(title="T", background_gradient="red&#59 color:blue")


def test_render_hero_rejects_unsafe_class():
    with pytest.raises(ValueError, match="cta_class"):
        Hero(title="T", cta_class='hero"bad')


def test_render_hero_rejects_class_with_html_entity_payload():
    with pytest.raises(ValueError, match="cta_class"):
        Hero(title="T", cta_class="hero&amp;bad")


def test_render_hero_rejects_unsafe_container_class():
    with pytest.raises(ValueError, match="container_class"):
        render_hero(Hero(title="T"), container_class='hero"bad')


def test_render_hero_accepts_url_with_query_ampersand():
    # Plain ampersand in a query string (e.g. /img.jpg?x=1&y=2) is NOT an HTML
    # entity reference; the browser does not decode it. The validator must
    # accept these to avoid breaking legitimate URLs.
    out = render_hero(Hero(title="T", background_image="/img/bg.jpg?x=1&y=2"))
    assert "/img/bg.jpg?x=1&y=2" in out


def test_render_hero_rejects_named_entity_with_semicolon():
    with pytest.raises(ValueError, match="background_image"):
        Hero(title="T", background_image="/img/&apos;bg.jpg")


def test_render_hero_rejects_decimal_entity_without_semicolon():
    with pytest.raises(ValueError, match="background_image"):
        Hero(title="T", background_image="x&#39); color:red;/*")


def test_render_hero_rejects_legacy_named_entity_without_semicolon():
    # WHATWG decodes `&quot` (no `;`) to `"` in attribute contexts via the
    # legacy named-entity table. The validator must catch this form too.
    with pytest.raises(ValueError, match="background_image"):
        Hero(title="T", background_image='x&quot onmouseover=alert(1) style="')


def test_render_hero_rejects_hex_entity_in_gradient():
    with pytest.raises(ValueError, match="background_gradient"):
        Hero(title="T", background_gradient="red&#x3B color:blue")


def test_render_hero_rejects_background_image_and_gradient_together():
    with pytest.raises(
        ValueError, match="Hero accepts at most one of background_image, background_gradient"
    ):
        Hero(
            title="T",
            background_image="/img/bg.jpg",
            background_gradient="linear-gradient(0deg,#fff,#000)",
        )


def test_render_hero_escapes_unsafe_text():
    out = render_hero(Hero(title="<script>"))
    assert "<script>" not in out.replace("<script", "")
    assert "&lt;script&gt;" in out


def test_render_hero_emits_valid_block_marker():
    out = render_hero(Hero(title="T"))
    assert detect_blocks(out) == ("hero",)
