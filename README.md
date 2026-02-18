# cyber-compliance-cli

A cybersecurity compliance CLI + beautiful terminal dashboard (TUI).

## Features

- Interactive TUI dashboard (Textual)
- Framework scorecards (NIST, ISO 27001, SOC 2, CIS)
- Gap summaries and prioritized actions
- Live scoring powered by `cyber-compliance-mcp` logic

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

Run live dashboard:

```bash
cybersec dashboard --assessment-file assessment.json
```

Framework summary:

```bash
cybersec checklist --framework iso27001 --assessment-file assessment.json
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

## License

MIT
