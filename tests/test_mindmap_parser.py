from notebooklm_llm_wiki_flow.mindmap_parser import parse_mindmap_topics


def test_parse_mindmap_topics_extracts_paths_and_importance():
    data = {
        "name": "Policy",
        "children": [
            {
                "name": "Data Ownership",
                "children": [
                    {"name": "No training by default"},
                    {"name": "Customer owns outputs"},
                ],
            }
        ],
    }

    topics = parse_mindmap_topics(data)

    assert topics[0].path == ["Policy", "Data Ownership"]
    assert topics[0].importance == "primary"
    assert topics[1].path == ["Policy", "Data Ownership", "No training by default"]
    assert topics[1].importance == "supporting"
