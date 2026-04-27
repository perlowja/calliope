# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from calliope.cards import Pill, TaxonomyEntry, render_pill, render_pills


def test_render_pill_minimal():
    out = render_pill(Pill(label="Restaurant"))
    assert out == '<span class="pill">Restaurant</span>'


def test_render_pill_with_class_and_color():
    out = render_pill(Pill(label="Routine", css_class="pill-rest", color="#dc2626"))
    assert 'class="pill pill-rest"' in out
    assert 'style="background:#dc2626;"' in out
    assert ">Routine<" in out


def test_render_pill_with_title():
    out = render_pill(Pill(label="HP", title="High priority"))
    assert 'title="High priority"' in out


def test_render_pill_escapes_label():
    out = render_pill(Pill(label="<script>"))
    assert "<script>" not in out.replace("<script", "")
    assert "&lt;script&gt;" in out


def test_render_pills_empty_returns_empty_string():
    assert render_pills([]) == ""


def test_render_pills_wraps_with_container_class():
    out = render_pills([Pill(label="A"), Pill(label="B")], container_class="pills")
    assert out.startswith('<div class="pills">')
    assert "<span" in out


def test_render_pills_custom_base_class():
    out = render_pills([Pill(label="A")], base_class="badge")
    assert 'class="badge"' in out
    assert 'class="pill"' not in out


def test_pill_from_taxonomy_entry():
    entry = TaxonomyEntry(label="LLC", css_class="entity-llc", color="#3b82f6")
    pill = Pill.from_taxonomy(entry, title="Limited Liability Co.")
    assert pill.label == "LLC"
    assert pill.css_class == "entity-llc"
    assert pill.color == "#3b82f6"
    assert pill.title == "Limited Liability Co."
