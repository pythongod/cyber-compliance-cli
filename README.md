# cyber-compliance-cli

A cybersecurity compliance CLI + beautiful terminal dashboard (TUI).

## Features

- Interactive TUI dashboard (Textual)
- Interactive TUI control status editor
- Framework scorecards (NIST, ISO 27001, SOC 2, CIS)
- Gap summaries and prioritized actions
- Live scoring powered by `cyber-compliance-mcp` logic
- Transport modes: `python` (direct import) and `stdio` (true MCP client/server)

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Also install MCP package (or keep sibling repo checkout):

```bash
cd ../cyber-compliance-mcp
pip install -e .
```

## Usage

Create starter assessment file:

```bash
cybersec init-assessment
```

Run live dashboard (python transport):

```bash
cybersec dashboard --assessment-file assessment.json --transport python
```

Run live dashboard (true MCP stdio transport):

```bash
cybersec dashboard --assessment-file assessment.json --transport stdio --server-command cyber-compliance-mcp
```

Open interactive status editor:

```bash
cybersec edit --assessment-file assessment.json --transport stdio
```

Framework summary:

```bash
cybersec checklist --framework iso27001 --assessment-file assessment.json --transport stdio
```

Manual weighted score:

```bash
cybersec score --framework nist_csf --implemented 32 --partial 10 --missing 8
```

## assessment.json format

```json
{
  "frameworks": {
    "nist_csf": {
      "statuses": {
        "GV.OV-01 Governance strategy defined": "implemented",
        "ID.AM-01 Asset inventory maintained": "partial"
      }
    }
  }
}
```

Status values: `implemented`, `partial`, `missing`.

## Quick dev

```bash
cp assessment.sample.json assessment.json
make setup
make test
```

## License

MIT


CSV import/export:

```bash
cybersec export-csv --assessment-file assessment.json --output-csv assessment.csv
cybersec import-csv --input-csv assessment.csv --assessment-file assessment.json
```

Markdown report:

```bash
cybersec report --assessment-file assessment.json --output compliance-report.md --transport stdio
```


## Error handling behavior

CLI now enforces MCP unified envelopes when available:
- success: `{"ok": true, ...}`
- failure: `{"ok": false, "error": {"code", "message"}}`

On failure, CLI exits with a clear mapped error message.


### Friendly error hints

CLI maps common MCP error codes to actionable hints, for example:
- `INVALID_FRAMEWORK` → suggests valid framework keys
- `ASSESSMENT_NOT_FOUND` → suggests creating/fixing id
- `INVALID_STATUS` → suggests valid status values


PDF report (optional `reportlab`):

```bash
cybersec report --assessment-file assessment.json --format pdf --output compliance-report.pdf
```


Validation + diff:

```bash
cybersec validate-assessment --assessment-file assessment.json
cybersec diff --old-file baseline.json --new-file assessment.json
```
