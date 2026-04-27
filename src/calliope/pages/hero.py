# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

"""Hero — the prominent above-the-fold section of a landing page.

Substrate-shaped: the hero has a title, optional subtitle, optional
background image, and optional CTA. Everything above-fold beyond that
(stats, scoreboards, news widgets) belongs in subsequent sections.
"""

from __future__ import annotations

from dataclasses import dataclass

from calliope.pages._validation import (
    validate_class_list,
    validate_css_attribute_value,
    validate_css_declaration_value,
)
from calliope.templates import safe_value


@dataclass(frozen=True)
class Hero:
    title: str
    subtitle: str = ""
    background_image: str | None = None
    background_gradient: str | None = None
    cta_label: str | None = None
    cta_href: str | None = None
    cta_class: str = "hero-cta"

    def __post_init__(self) -> None:
        if self.background_image and self.background_gradient:
            raise ValueError("Hero accepts at most one of background_image, background_gradient")
        validate_css_attribute_value(self.background_image, field_name="background_image")
        validate_css_declaration_value(self.background_gradient, field_name="background_gradient")
        validate_class_list(self.cta_class, field_name="cta_class")


def render_hero(hero: Hero, *, container_class: str = "hero") -> str:
    """Render a `<section class="hero">…</section>` block.

    The block uses the calliope marker convention so pages that include
    a hero can validate the section as a discrete block.
    """
    validate_class_list(container_class, field_name="container_class")
    style_parts: list[str] = []
    if hero.background_image:
        style_parts.append(f"background-image:url('{hero.background_image}');")
    if hero.background_gradient:
        style_parts.append(f"background:{hero.background_gradient};")
    style = f' style="{" ".join(style_parts)}"' if style_parts else ""

    cta_html = ""
    if hero.cta_label and hero.cta_href:
        cta_html = (
            f'\n        <a href="{safe_value(hero.cta_href)}" class="{safe_value(hero.cta_class)}">'
            f"{safe_value(hero.cta_label)}</a>"
        )

    subtitle_html = (
        f'\n        <p class="hero-subtitle">{safe_value(hero.subtitle)}</p>'
        if hero.subtitle
        else ""
    )

    return (
        f"<!-- BLOCK:hero -->\n"
        f'    <section class="{safe_value(container_class)}"{style}>\n'
        f'        <h1 class="hero-title">{safe_value(hero.title)}</h1>'
        f"{subtitle_html}"
        f"{cta_html}\n"
        f"    </section>\n"
        f"<!-- /BLOCK:hero -->"
    )
