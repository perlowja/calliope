# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import pytest

from calliope.pages import (
    Scoreboard,
    ScoreboardRow,
    make_scoreboard,
    render_scoreboard,
)
from calliope.templates import detect_blocks


def test_scoreboard_total_sums_row_counts():
    sb = Scoreboard(
        title="By City",
        rows=(
            ScoreboardRow(label="A", count=3),
            ScoreboardRow(label="B", count=5),
        ),
    )
    assert sb.total == 8


def test_scoreboard_rejects_non_tuple_rows():
    with pytest.raises(TypeError):
        Scoreboard(title="x", rows=[ScoreboardRow(label="A")])  # type: ignore[arg-type]


def test_scoreboard_rejects_non_row_entry():
    with pytest.raises(TypeError):
        Scoreboard(title="x", rows=(("wrong",),))  # type: ignore[arg-type]


def test_scoreboard_rejects_negative_count():
    with pytest.raises(ValueError):
        Scoreboard(title="x", rows=(ScoreboardRow(label="A", count=-1),))


def test_make_scoreboard_accepts_iterable():
    sb = make_scoreboard(
        "By City",
        iter([ScoreboardRow(label="A", count=3), ScoreboardRow(label="B", count=5)]),
    )
    assert sb.total == 8


def test_render_scoreboard_emits_block_marker():
    sb = Scoreboard(title="By City", rows=(ScoreboardRow(label="A", count=3),))
    out = render_scoreboard(sb)
    assert detect_blocks(out) == ("scoreboard",)


def test_render_scoreboard_renders_rows_as_links_when_href_set():
    sb = Scoreboard(
        title="By City",
        rows=(ScoreboardRow(label="A", count=3, href="/a.html"),),
    )
    out = render_scoreboard(sb)
    assert '<a href="/a.html"' in out


def test_render_scoreboard_escapes_row_href_in_attributes():
    sb = Scoreboard(
        title="By City",
        rows=(ScoreboardRow(label="A", count=3, href='/x"><img>'),),
    )
    out = render_scoreboard(sb)
    assert 'href="/x&quot;&gt;&lt;img&gt;"' in out
    assert '/x"><img>' not in out
    assert "<img>" not in out


def test_render_scoreboard_renders_rows_as_divs_when_no_href():
    sb = Scoreboard(title="x", rows=(ScoreboardRow(label="A", count=3),))
    out = render_scoreboard(sb)
    assert "<a href=" not in out


def test_render_scoreboard_includes_total_by_default():
    sb = Scoreboard(title="x", rows=(ScoreboardRow(label="A", count=3),))
    out = render_scoreboard(sb)
    assert "scoreboard-total" in out
    assert ">TOTAL<" in out
    assert ">3<" in out


def test_render_scoreboard_omits_total_when_disabled():
    sb = Scoreboard(title="x", rows=(ScoreboardRow(label="A", count=3),), show_total=False)
    out = render_scoreboard(sb)
    assert "scoreboard-total" not in out


def test_render_scoreboard_escapes_label():
    sb = Scoreboard(title="x", rows=(ScoreboardRow(label="<b>", count=0),))
    out = render_scoreboard(sb)
    assert "<b>" not in out.replace("<b>0</b>", "").replace("<b ", "")
    assert "&lt;b&gt;" in out


def test_scoreboard_row_rejects_unsafe_color():
    with pytest.raises(ValueError, match="color"):
        ScoreboardRow(label="A", color="red; display:none")


def test_scoreboard_row_rejects_color_with_html_entity_payload():
    with pytest.raises(ValueError, match="color"):
        ScoreboardRow(label="A", color="red&#59 color:blue")


def test_scoreboard_row_rejects_unsafe_class():
    with pytest.raises(ValueError, match="css_class"):
        ScoreboardRow(label="A", css_class='row"bad')


def test_scoreboard_row_rejects_class_with_html_entity_payload():
    with pytest.raises(ValueError, match="css_class"):
        ScoreboardRow(label="A", css_class="row&amp;bad")


def test_scoreboard_rejects_unsafe_container_class():
    with pytest.raises(ValueError, match="container_class"):
        Scoreboard(title="x", rows=(), container_class='scoreboard"bad')


def test_scoreboard_rejects_container_class_with_html_entity_payload():
    with pytest.raises(ValueError, match="container_class"):
        Scoreboard(title="x", rows=(), container_class="scoreboard&amp;bad")


def test_render_scoreboard_empty_rows_still_renders_total_zero():
    sb = Scoreboard(title="x", rows=())
    out = render_scoreboard(sb)
    assert ">0<" in out
