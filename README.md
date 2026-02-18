# cyber-compliance-cli

A cybersecurity compliance CLI + beautiful terminal dashboard (TUI).

## Features

- Interactive TUI dashboard (Textual)
- Framework scorecards (NIST, ISO 27001, SOC 2, CIS)
- Gap summaries and prioritized actions
- Fast local usage and scripting with CLI commands

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
cybersec dashboard
cybersec score --framework nist_csf --implemented 32 --partial 10 --missing 8
cybersec checklist --framework iso27001
```

## License

MIT
