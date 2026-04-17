# run-from-yaml

`run-from-yaml` means the workflow is no longer hardcoded in Python.
Instead, the user defines the research job in a YAML file and the CLI executes it.

## Why this matters

Without `run-from-yaml`:
- every new workflow needs a new hardcoded command like `run-policy-compare`
- reuse is limited
- public users have to edit Python code

With `run-from-yaml`:
- the repo ships one reusable engine
- users create new research workflows by editing YAML only
- the same pipeline can support policy comparisons, paper comparisons, vendor analysis, and curriculum research

## Minimum YAML shape

- `title`
- `sources`
- `report_append`
- `question` (optional)
- `wiki_outputs`
  - `comparison_slug`
  - `comparison_title`
  - `checklist_slug`
  - `checklist_title`
- `entities` (optional)

## Example

See:
- `examples/policy-compare-anthropic-openai-education.yaml`

## Current behavior

The command:
- creates a NotebookLM notebook
- adds sources
- waits for processing
- generates a report and mind map
- asks a synthesis question
- downloads raw artifacts
- writes raw source notes, comparison notes, checklist notes, and optional entity notes
- updates qmd

## Obsidian compatibility

Generated notes use:
- `source_notes` for vault-internal provenance
- `source_urls` for clickable original URLs in Obsidian properties
