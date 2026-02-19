from __future__ import annotations

from typing import Any, Dict, List

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, Static

from .mcp_client import SUPPORTED_FRAMEWORKS, load_assessment, save_assessment, set_control_status, summarize_all


class AssessmentEditorApp(App):
    CSS = """
    Screen { background: #0b1020; color: #e2e8f0; }
    .panel { border: round #334155; background: #111827; padding: 1 2; margin: 1 2; }
    #filter { margin: 0 2; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("up", "up", "Up"),
        ("down", "down", "Down"),
        ("m", "next_framework", "Next framework"),
        ("h", "help", "Help"),
        ("e", "toggle_modal", "Toggle details"),
        ("1", "set_implemented", "implemented"),
        ("2", "set_partial", "partial"),
        ("3", "set_missing", "missing"),
        ("s", "save", "Save"),
    ]

    def __init__(
        self,
        assessment_file: str,
        org_type: str = "saas",
        transport: str = "python",
        server_command: str = "cyber-compliance-mcp",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.assessment_file = assessment_file
        self.org_type = org_type
        self.transport = transport
        self.server_command = server_command
        self.framework_idx = 0
        self.control_idx = 0
        self.show_help = False
        self.show_modal = False
        self.filter_text = ""

        self.data = summarize_all(
            self.assessment_file,
            org_type=self.org_type,
            transport=self.transport,
            server_command=self.server_command,
        )
        self.assessment = load_assessment(self.assessment_file)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Static("", id="header", classes="panel")
            yield Input(placeholder="Filter controls (type to search)...", id="filter")
            yield Static("", id="controls", classes="panel")
            yield Static("", id="modal", classes="panel")
            yield Static("", id="help", classes="panel")
        yield Footer()

    def on_mount(self) -> None:
        self._render_all()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "filter":
            self.filter_text = event.value.strip().lower()
            self.control_idx = 0
            self._render_all()

    def _current_framework(self) -> str:
        return SUPPORTED_FRAMEWORKS[self.framework_idx % len(SUPPORTED_FRAMEWORKS)]

    def _controls(self) -> List[Dict[str, str]]:
        controls: List[Dict[str, str]] = self.data.get("framework_details", {}).get(self._current_framework(), [])
        if not self.filter_text:
            return controls
        return [c for c in controls if self.filter_text in c["control"].lower() or self.filter_text in c["status"].lower()]

    def _status_chip(self, status: str) -> str:
        return {"implemented": "🟢", "partial": "🟡", "missing": "🔴"}.get(status, "⚪")

    def _framework_tabs(self) -> str:
        curr = self._current_framework()
        tabs = [f"[{f}]" if f == curr else f for f in SUPPORTED_FRAMEWORKS]
        return " | ".join(tabs)

    def _render_all(self) -> None:
        fw = self._current_framework()
        summary = next((x for x in self.data.get("frameworks", []) if x.get("framework") == fw), {})
        self.query_one("#header", Static).update(
            f"[b]Tabs:[/b] {self._framework_tabs()}\n"
            f"[b]Framework:[/b] {fw}    [b]Risk:[/b] {summary.get('risk_level', 'unknown').upper()} ({summary.get('risk_score', '?')}%)    [b]File:[/b] {self.assessment_file}"
        )

        rows: List[str] = []
        controls = self._controls()
        if not controls:
            rows.append("No controls match current filter.")
            self.control_idx = 0
        else:
            self.control_idx = max(0, min(self.control_idx, len(controls) - 1))
            for idx, item in enumerate(controls):
                mark = ">" if idx == self.control_idx else " "
                chip = self._status_chip(item["status"])
                rows.append(f"{mark} {chip} {item['status']:<11}  {item['control']}")
        self.query_one("#controls", Static).update("\n".join(rows))

        modal = self.query_one("#modal", Static)
        if self.show_modal and controls:
            curr = controls[self.control_idx]
            modal.update(
                "[b]Control Detail[/b]\n"
                f"Control: {curr['control']}\n"
                f"Status: {curr['status']}\n"
                "Quick set: [1]=implemented [2]=partial [3]=missing"
            )
        else:
            modal.update("Press [e] to toggle control detail modal")

        help_text = (
            "Keys: ↑/↓ move • m switch framework • type in filter box • e detail modal • 1/2/3 set status • s save • h toggle help • q quit\n"
            "Legend: 🟢 implemented  🟡 partial  🔴 missing"
            if self.show_help
            else "Press [h] for help"
        )
        self.query_one("#help", Static).update(help_text)

    def _set_status(self, status: str) -> None:
        controls = self._controls()
        if not controls:
            return
        item = controls[self.control_idx]
        item["status"] = status
        set_control_status(self.assessment, self._current_framework(), item["control"], status)
        self._render_all()

    def action_up(self) -> None:
        self.control_idx = max(0, self.control_idx - 1)
        self._render_all()

    def action_down(self) -> None:
        controls = self._controls()
        if controls:
            self.control_idx = min(len(controls) - 1, self.control_idx + 1)
        self._render_all()

    def action_next_framework(self) -> None:
        self.framework_idx = (self.framework_idx + 1) % len(SUPPORTED_FRAMEWORKS)
        self.control_idx = 0
        self._render_all()

    def action_help(self) -> None:
        self.show_help = not self.show_help
        self._render_all()

    def action_toggle_modal(self) -> None:
        self.show_modal = not self.show_modal
        self._render_all()

    def action_set_implemented(self) -> None:
        self._set_status("implemented")

    def action_set_partial(self) -> None:
        self._set_status("partial")

    def action_set_missing(self) -> None:
        self._set_status("missing")

    def action_save(self) -> None:
        save_assessment(self.assessment_file, self.assessment)
        self.data = summarize_all(
            self.assessment_file,
            org_type=self.org_type,
            transport=self.transport,
            server_command=self.server_command,
        )
        self.notify("Saved assessment.json", timeout=1.5)
        self._render_all()
