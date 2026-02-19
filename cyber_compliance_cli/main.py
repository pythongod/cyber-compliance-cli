from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .editor import AssessmentEditorApp
from .mcp_client import MCPUnavailableError, load_assessment, summarize_all, summarize_framework
from .tui import CyberComplianceApp

app = typer.Typer(help="Cyber security compliance CLI")
console = Console()


@app.command()
def dashboard(
    assessment_file: str = typer.Option("assessment.json", help="Path to assessment JSON."),
    org_type: str = typer.Option("saas", help="Organization type for checklist generation."),
    transport: str = typer.Option("python", help="Transport: python|stdio"),
    server_command: str = typer.Option("cyber-compliance-mcp", help="MCP server command for stdio mode."),
) -> None:
    """Launch beautiful TUI dashboard using live data from MCP logic."""
    try:
        data = summarize_all(
            assessment_file,
            org_type=org_type,
            transport=transport,
            server_command=server_command,
        )
    except MCPUnavailableError as exc:
        console.print(f"[red]MCP unavailable:[/red] {exc}")
        raise typer.Exit(code=2)

    CyberComplianceApp(data).run()


@app.command()
def edit(
    assessment_file: str = typer.Option("assessment.json", help="Path to assessment JSON."),
    org_type: str = typer.Option("saas", help="Organization type for checklist generation."),
    transport: str = typer.Option("python", help="Transport: python|stdio"),
    server_command: str = typer.Option("cyber-compliance-mcp", help="MCP server command for stdio mode."),
) -> None:
    """Interactive TUI editor to update control statuses."""
    try:
        AssessmentEditorApp(
            assessment_file=assessment_file,
            org_type=org_type,
            transport=transport,
            server_command=server_command,
        ).run()
    except MCPUnavailableError as exc:
        console.print(f"[red]MCP unavailable:[/red] {exc}")
        raise typer.Exit(code=2)


@app.command()
def checklist(
    framework: str = typer.Option(..., help="Framework: nist_csf|iso27001|soc2|cis_v8"),
    assessment_file: str = typer.Option("assessment.json", help="Path to assessment JSON."),
    org_type: str = typer.Option("saas", help="Organization type."),
    transport: str = typer.Option("python", help="Transport: python|stdio"),
    server_command: str = typer.Option("cyber-compliance-mcp", help="MCP server command for stdio mode."),
) -> None:
    """Print control checklist summary via MCP logic."""
    try:
        assessment = load_assessment(assessment_file)
        summary = summarize_framework(
            framework.lower().strip(),
            assessment,
            org_type,
            transport=transport,
            server_command=server_command,
        )
    except MCPUnavailableError as exc:
        console.print(f"[red]MCP unavailable:[/red] {exc}")
        raise typer.Exit(code=2)

    if summary.get("error"):
        console.print(f"[red]{summary['error']}[/red]")
        raise typer.Exit(code=1)

    table = Table(title=f"{framework.upper()} Compliance Summary")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Risk score", f"{summary.get('risk_score')}%")
    table.add_row("Risk level", str(summary.get("risk_level", "")).upper())
    table.add_row("Implemented", str(summary.get("implemented", 0)))
    table.add_row("Partial", str(summary.get("partial", 0)))
    table.add_row("Missing", str(summary.get("missing", 0)))
    table.add_row("Controls total", str(summary.get("controls_total", 0)))

    console.print(table)


@app.command()
def score(
    framework: str = typer.Option(..., help="Framework label"),
    implemented: int = typer.Option(0, min=0),
    partial: int = typer.Option(0, min=0),
    missing: int = typer.Option(0, min=0),
) -> None:
    """Calculate and print a weighted risk score (manual mode)."""
    total = implemented + partial + missing
    if total == 0:
        console.print("[yellow]No controls provided.[/yellow]")
        raise typer.Exit()

    weighted_risk = ((partial * 5) + (missing * 10)) / (total * 10) * 100
    if weighted_risk < 25:
        level = "low"
        color = "green"
    elif weighted_risk < 50:
        level = "medium"
        color = "yellow"
    elif weighted_risk < 75:
        level = "high"
        color = "orange3"
    else:
        level = "critical"
        color = "red"

    console.print(f"Framework: [bold]{framework}[/bold]")
    console.print(f"Risk Score: [bold {color}]{weighted_risk:.2f}%[/bold {color}]")
    console.print(f"Risk Level: [bold {color}]{level.upper()}[/bold {color}]")


@app.command("init-assessment")
def init_assessment(
    output: str = typer.Option("assessment.json", help="Where to write starter assessment file."),
) -> None:
    """Create starter assessment.json for live dashboard data."""
    template = {
        "frameworks": {
            "nist_csf": {"statuses": {}},
            "iso27001": {"statuses": {}},
            "soc2": {"statuses": {}},
            "cis_v8": {"statuses": {}},
        }
    }

    path = Path(output)
    path.write_text(json.dumps(template, indent=2), encoding="utf-8")
    console.print(f"[green]Created[/green] {path}")
    console.print("Fill statuses with implemented|partial|missing and rerun dashboard.")


if __name__ == "__main__":
    app()
