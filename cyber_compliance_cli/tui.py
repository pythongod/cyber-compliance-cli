from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static


class Card(Static):
    def __init__(self, title: str, body: str, classes: str = ""):
        super().__init__(f"[b]{title}[/b]\n{body}", classes=classes)


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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="layout"):
            yield Static("[b cyan]Cyber Security Compliance Dashboard[/b cyan]\n", classes="card")
            with Horizontal():
                yield Card("NIST CSF", "Score: 82\nStatus: Good\nGaps: 6", classes="card ok")
                yield Card("ISO 27001", "Score: 74\nStatus: Improving\nGaps: 11", classes="card warn")
            with Horizontal():
                yield Card("SOC 2", "Score: 68\nStatus: At Risk\nGaps: 14", classes="card warn")
                yield Card("CIS v8", "Score: 59\nStatus: Critical\nGaps: 19", classes="card bad")
            yield Card(
                "Priority Actions",
                "1) Enforce MFA for all privileged users\n"
                "2) Centralize logging + SIEM alert tuning\n"
                "3) Run incident response tabletop this quarter\n"
                "4) Complete asset inventory + ownership mapping",
                classes="card",
            )
        yield Footer()

    def action_refresh(self) -> None:
        self.notify("Dashboard refreshed", timeout=1.5)
