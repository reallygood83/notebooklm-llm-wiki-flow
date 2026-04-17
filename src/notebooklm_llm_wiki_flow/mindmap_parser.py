from __future__ import annotations

from .models import ExtractedTopic


def parse_mindmap_topics(data: dict) -> list[ExtractedTopic]:
    topics: list[ExtractedTopic] = []
    root = data.get("name", "root")

    def walk(node: dict, path: list[str]) -> None:
        children = node.get("children") or []
        for child in children:
            next_path = [*path, child["name"]]
            depth = len(next_path) - 1
            importance = "primary" if depth == 1 else "supporting"
            topics.append(ExtractedTopic(path=next_path, depth=depth, importance=importance))
            walk(child, next_path)

    walk(data, [root])
    return topics
