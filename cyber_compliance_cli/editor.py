from __future__ import annotations

from typing import Any, Dict, List

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static

from .mcp_client import (
    SUPPORTED_FRAMEWORKS,
    load_assessment,
    save_assessment,
    set_control_status,
    summarize_all,
)


class AssessmentEditorApp(App):
    CSS = """
    Screen {
        background: #0b1020;
        color: #e2e8f0;
    }

    .panel {
        border: round #334155;
        background: #111827;
        padding: 1 2;
        margin: 1 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("up", "up", "Up"),
        ("down", "down", "Down"),
        ("m", "next_framework", "Next framework"),
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
            yield Static("", id="controls", classes="panel")
            yield Static(
                "Keys: ↑/↓ move • m switch framework • 1/2/3 set status • s save • q quit",
                classes="panel",
            )
        yield Footer()

    def on_mount(self) -> None:
        self._render_all()

    def _current_framework(self) -> str:
        return SUPPORTED_FRAMEWORKS[self.framework_idx % len(SUPPORTED_FRAMEWORKS)]

    def _controls(self) -> List[Dict[str, str]]:
        fw = self._current_framework()
        return self.data.get("framework_details", {}).get(fw, [])

    def _render_all(self) -> None:
        fw = self._current_framework()
        summary = next((x for x in self.data.get("frameworks", []) if x.get("framework") == fw), {})
        self.query_one("#header", Static).update(
            f"[b]Framework:[/b] {fw}    "
            f"[b]Risk:[/b] {summary.get('risk_level', 'unknown').upper()} ({summary.get('risk_score', '?')}%)    "
            f"[b]File:[/b] {self.assessment_file}"
        )

        rows = []
        controls = self._controls()
        if not controls:
            rows.append("No controls loaded.")
        else:
            self.control_idx = max(0, min(self.control_idx, len(controls) - 1))
            for idx, item in enumerate(controls):
                mark = ">" if idx == self.control_idx else " "
                rows.append(f"{mark} {item['status']:<11}  {item['control']}")

        self.query_one("#controls", Static).update("\n".join(rows))

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
