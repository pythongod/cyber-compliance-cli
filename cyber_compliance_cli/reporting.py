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

    lines: List[str] = ["# Cyber Compliance Report", "", f"Generated: {ts}", "", "## Executive Summary", ""]

    for row in frameworks:
        lines.append(
            f"- **{_label(row.get('framework',''))}**: "
            f"Risk **{str(row.get('risk_level','unknown')).upper()}** "
            f"({row.get('risk_score','?')}%), "
            f"Implemented {row.get('implemented',0)}, "
            f"Partial {row.get('partial',0)}, "
            f"Missing {row.get('missing',0)}"
        )

    lines.extend(["", "## Priority Actions", ""])
    if actions:
        for i, action in enumerate(actions, start=1):
            lines.append(f"{i}. {action}")
    else:
        lines.append("- No prioritized actions generated.")

    lines.extend(["", "## Framework Details", ""])
    for row in frameworks:
        fw = row.get("framework", "")
        lines.extend(
            [
                f"### {_label(fw)}",
                "",
                "| Metric | Value |",
                "|---|---|",
                f"| Risk score | {row.get('risk_score','?')}% |",
                f"| Risk level | {str(row.get('risk_level','unknown')).upper()} |",
                f"| Implemented | {row.get('implemented',0)} |",
                f"| Partial | {row.get('partial',0)} |",
                f"| Missing | {row.get('missing',0)} |",
                "",
            ]
        )

    return "\n".join(lines) + "\n"


def write_markdown_report(path: str | Path, data: Dict[str, Any]) -> Path:
    out = Path(path)
    out.write_text(render_markdown_report(data), encoding="utf-8")
    return out


def write_pdf_report(path: str | Path, data: Dict[str, Any]) -> Path:
    """Write simple PDF report. Requires reportlab; otherwise raises RuntimeError."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PDF export requires optional dependency: reportlab") from exc

    out = Path(path)
    md = render_markdown_report(data)
    c = canvas.Canvas(str(out), pagesize=A4)
    width, height = A4
    y = height - 40
    for raw in md.splitlines():
        line = raw[:120]
        c.drawString(40, y, line)
        y -= 14
        if y < 40:
            c.showPage()
            y = height - 40
    c.save()
    return out
