from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from .tui import CyberComplianceApp

app = typer.Typer(help="Cyber security compliance CLI")
console = Console()

FRAMEWORK_ITEMS = {
    "nist_csf": ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"],
    "iso27001": ["Policies", "Asset Mgmt", "Access Control", "Ops Security", "IR", "BCP"],
    "soc2": ["Security", "Availability", "Confidentiality", "Processing Integrity", "Privacy"],
    "cis_v8": ["Assets", "Software", "Data", "Config", "Accounts", "Logging"],
}


@app.command()
def dashboard() -> None:
    """Launch beautiful TUI dashboard."""
    CyberComplianceApp().run()


@app.command()
def checklist(framework: str = typer.Option(..., help="Framework: nist_csf|iso27001|soc2|cis_v8")) -> None:
    """Print control checklist for a framework."""
    key = framework.lower().strip()
    items = FRAMEWORK_ITEMS.get(key)
    if not items:
        console.print(f"[red]Unsupported framework:[/red] {framework}")
        raise typer.Exit(code=1)

    table = Table(title=f"{key.upper()} Checklist")
    table.add_column("#", justify="right")
    table.add_column("Control Area")
    table.add_column("Status")

    for idx, item in enumerate(items, start=1):
        table.add_row(str(idx), item, "not_started")

    console.print(table)


@app.command()
def score(
    framework: str = typer.Option(..., help="Framework label"),
    implemented: int = typer.Option(0, min=0),
    partial: int = typer.Option(0, min=0),
    missing: int = typer.Option(0, min=0),
) -> None:
    """Calculate and print a weighted risk score."""
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


if __name__ == "__main__":
    app()
