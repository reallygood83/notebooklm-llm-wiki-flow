from __future__ import annotations

from typing import Any

from .models import ExtractedTopic


def parse_mindmap_topics(data: dict[str, Any]) -> list[ExtractedTopic]:
    topics: list[ExtractedTopic] = []
    root = data.get("name", "root")

    def walk(node: dict[str, Any], path: list[str]) -> None:
        children = node.get("children") or []
        for child in children:
            next_path = [*path, child["name"]]
            depth = len(next_path) - 1
            importance = "primary" if depth == 1 else "supporting"
            topics.append(ExtractedTopic(path=next_path, depth=depth, importance=importance))
            walk(child, next_path)

    walk(data, [root])
    return topics
