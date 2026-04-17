from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

_TEMPLATE_ENV = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parents[2] / "templates"),
    autoescape=False,
    keep_trailing_newline=True,
    lstrip_blocks=False,
    trim_blocks=False,
    undefined=StrictUndefined,
)


def render_entity_template(*, title: str, created: str, updated: str, source_notes: list[str], source_urls: list[str], overview: str, policy_posture: list[str], related_links: list[str]) -> str:
    template = _TEMPLATE_ENV.get_template("entity.md.j2")
    return template.render(
        title=title,
        created=created,
        updated=updated,
        source_notes=source_notes,
        source_urls=source_urls,
        overview=overview,
        policy_posture=policy_posture,
        related_links=related_links,
    )
