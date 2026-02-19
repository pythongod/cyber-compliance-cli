# TODO (Prioritized Next 10)

## P0 — Immediate

1. Add **CSV import/export** for `assessment.json` control statuses.
2. Add **Markdown report export** command (`cybersec report --format md`).
3. Add **PDF export** via Markdown renderer (optional dependency fallback).
4. Improve TUI editor UX: **framework tabs + status color chips + help modal**.

## P1 — Reliability

5. Add tests for **stdio transport path** (mocked MCP server or integration smoke test).
6. Add tests for **editor save cycle** and status persistence.
7. Add command to **validate assessment schema** with useful errors.

## P2 — Product polish

8. Add `cybersec diff` to compare two assessments and show progress.
9. Add `cybersec plan` to generate 30/60/90 remediation plan from current gaps.
10. Package release automation (version bump + changelog + GitHub release notes).
