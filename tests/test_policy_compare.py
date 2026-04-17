from notebooklm_llm_wiki_flow.policy_compare import extract_checklist_items, extract_core_policy_table_rows


REPORT = """# Business AI Policy Comparison: Anthropic and OpenAI

## 1. Data Ownership and Model Training

### Core Policies
| Feature | OpenAI (Business/Enterprise/API) | Anthropic (Commercial Services) |
| :--- | :--- | :--- |
| **Input Ownership** | Customer retains all rights. | Customer retains all rights. |
| **Output Ownership** | Customer owns outputs to the extent permitted by law. | Customer owns outputs; Anthropic assigns all right, title, and interest to the customer. |
| **Training on Business Data** | **No by default.** | **No.** |

## 4. Considerations for Education Vertical AI Companies
*   **Student Data Privacy Agreements:** Offer a dedicated student privacy agreement.
*   **Age-Specific Safeguards:** Add minors safety rules.
*   **Mandatory Human-in-the-Loop:** Require review for grading and admissions.
"""

QA = """### Policy Checklist for an Education Vertical AI Company
**1. Data Privacy & Compliance Agreements**
*   [ ] Student Data Privacy Agreement
*   [ ] Zero data retention for sensitive student data

**2. Academic Integrity & Human Oversight**
*   [ ] Ban academic dishonesty
*   [ ] Require human review for grading decisions
"""


def test_extract_core_policy_table_rows_reads_markdown_table():
    rows = extract_core_policy_table_rows(REPORT)

    assert rows[0] == (
        "Input Ownership",
        "Customer retains all rights.",
        "Customer retains all rights.",
    )
    assert rows[2][0] == "Training on Business Data"
    assert "No by default" in rows[2][1]


def test_extract_checklist_items_prefers_checkbox_list_then_falls_back_to_numbered_recommendations():
    qa_items = extract_checklist_items(QA, REPORT)
    report_items = extract_checklist_items("", REPORT)

    assert qa_items[0] == "Student Data Privacy Agreement"
    assert any("human review" in item.lower() for item in qa_items)
    assert all("[" not in item for item in qa_items)
    assert all("**" not in item for item in qa_items)
    assert any("student privacy agreement" in item.lower() for item in report_items)
    assert any("grading and admissions" in item.lower() for item in report_items)
