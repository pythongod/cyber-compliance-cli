from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _label(framework: str) -> str:
    return {
        "nist_csf": "NIST CSF",
        "iso27001": "ISO 27001",
        "soc2": "SOC 2",
        "cis_v8": "CIS v8",
    }.get(framework, framework)


def render_markdown_report(data: Dict[str, Any]) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    frameworks: List[Dict[str, Any]] = data.get("frameworks", [])
    actions: List[str] = data.get("priority_actions", [])

    lines: List[str] = []
    lines.append("# Cyber Compliance Report")
    lines.append("")
    lines.append(f"Generated: {ts}")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    for row in frameworks:
        lines.append(
            f"- **{_label(row.get('framework',''))}**: "
            f"Risk **{str(row.get('risk_level','unknown')).upper()}** "
            f"({row.get('risk_score','?')}%), "
            f"Implemented {row.get('implemented',0)}, "
            f"Partial {row.get('partial',0)}, "
            f"Missing {row.get('missing',0)}"
        )

    lines.append("")
    lines.append("## Priority Actions")
    lines.append("")
    if actions:
        for i, action in enumerate(actions, start=1):
            lines.append(f"{i}. {action}")
    else:
        lines.append("- No prioritized actions generated.")

    lines.append("")
    lines.append("## Framework Details")
    lines.append("")
    for row in frameworks:
        fw = row.get("framework", "")
        lines.append(f"### {_label(fw)}")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        lines.append(f"| Risk score | {row.get('risk_score','?')}% |")
        lines.append(f"| Risk level | {str(row.get('risk_level','unknown')).upper()} |")
        lines.append(f"| Implemented | {row.get('implemented',0)} |")
        lines.append(f"| Partial | {row.get('partial',0)} |")
        lines.append(f"| Missing | {row.get('missing',0)} |")
        lines.append("")

    return "\n".join(lines) + "\n"


def write_markdown_report(path: str | Path, data: Dict[str, Any]) -> Path:
    out = Path(path)
    out.write_text(render_markdown_report(data), encoding="utf-8")
    return out
