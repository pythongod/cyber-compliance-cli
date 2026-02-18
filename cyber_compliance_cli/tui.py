from __future__ import annotations

from typing import Any, Dict, List

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static


class Card(Static):
    def __init__(self, title: str, body: str, classes: str = ""):
        super().__init__(f"[b]{title}[/b]\n{body}", classes=classes)


def _badge(risk_level: str) -> str:
    level = (risk_level or "").lower()
    if level == "low":
        return "ok"
    if level in {"medium", "high"}:
        return "warn"
    return "bad"


def _framework_label(framework_key: str) -> str:
    labels = {
        "nist_csf": "NIST CSF",
        "iso27001": "ISO 27001",
        "soc2": "SOC 2",
        "cis_v8": "CIS v8",
    }
    return labels.get(framework_key, framework_key)


class CyberComplianceApp(App):
    CSS = """
    Screen {
        background: #0b1020;
        color: #e2e8f0;
    }

    Header {
        background: #1d4ed8;
        color: white;
    }

    Footer {
        background: #111827;
        color: #93c5fd;
    }

    #layout {
        height: 1fr;
        padding: 1 2;
    }

    .card {
        border: round #334155;
        background: #111827;
        padding: 1 2;
        margin: 1 1;
        width: 1fr;
        height: auto;
    }

    .ok { border: round #22c55e; }
    .warn { border: round #eab308; }
    .bad { border: round #ef4444; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, data: Dict[str, Any], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.data = data

    def compose(self) -> ComposeResult:
        frameworks: List[Dict[str, Any]] = self.data.get("frameworks", [])
        actions: List[str] = self.data.get("priority_actions", [])
        source = self.data.get("assessment_path") or "(default: missing controls unless in assessment file)"

        yield Header(show_clock=True)
        with Vertical(id="layout"):
            yield Static(
                "[b cyan]Cyber Security Compliance Dashboard[/b cyan]\n"
                f"Data source: {source}",
                classes="card",
            )

            # Render cards in rows of 2
            for i in range(0, len(frameworks), 2):
                pair = frameworks[i : i + 2]
                with Horizontal():
                    for item in pair:
                        label = _framework_label(item.get("framework", ""))
                        risk = item.get("risk_score", "?")
                        level = str(item.get("risk_level", "unknown")).upper()
                        body = (
                            f"Score: {risk}%\n"
                            f"Risk: {level}\n"
                            f"Implemented: {item.get('implemented', 0)}\n"
                            f"Partial: {item.get('partial', 0)}\n"
                            f"Missing: {item.get('missing', 0)}"
                        )
                        yield Card(label, body, classes=f"card {_badge(item.get('risk_level', ''))}")

            if actions:
                action_lines = "\n".join(f"{idx+1}) {action}" for idx, action in enumerate(actions[:6]))
            else:
                action_lines = "No prioritized actions generated."

            yield Card("Priority Actions", action_lines, classes="card")

        yield Footer()

    def action_refresh(self) -> None:
        self.notify("Dashboard refreshed", timeout=1.5)
