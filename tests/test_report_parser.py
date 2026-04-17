from notebooklm_llm_wiki_flow.report_parser import extract_report_highlights

REPORT = """# Business AI Policy Comparison

## 1. Data Ownership and Model Training
OpenAI does not train on business data by default.
- Customer owns outputs
- Retention control for enterprise

## 2. Minors and Academic Integrity
Anthropic requires human review in high-risk cases.
- Academic dishonesty prohibition
- Student safety guardrails
"""


def test_extract_report_highlights_prioritizes_major_policy_sections():
    highlights = extract_report_highlights(REPORT, max_bullets=5)

    section_titles = [section.title for section in highlights.sections]
    assert "Data Ownership and Model Training" in section_titles
    assert "Minors and Academic Integrity" in section_titles
    assert any("Customer owns outputs" in bullet for bullet in highlights.bullets)
    assert any("Academic dishonesty" in bullet for bullet in highlights.bullets)
