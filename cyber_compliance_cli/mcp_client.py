from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import anyio

SUPPORTED_FRAMEWORKS = ["nist_csf", "iso27001", "soc2", "cis_v8"]
VALID_STATUSES = {"implemented", "partial", "missing"}


class MCPUnavailableError(RuntimeError):
    pass


def _import_mcp_tools():
    """Import MCP core functions directly (python transport)."""
    try:
        from cyber_compliance_mcp.core import (  # type: ignore
            calculate_risk_score,
            generate_checklist,
            recommend_next_actions,
        )

        return calculate_risk_score, generate_checklist, recommend_next_actions
    except Exception:
        pass

    import sys

    sibling = Path(__file__).resolve().parents[2] / "cyber-compliance-mcp"
    if sibling.exists():
        sys.path.insert(0, str(sibling))
        try:
            from cyber_compliance_mcp.core import (  # type: ignore
                calculate_risk_score,
                generate_checklist,
                recommend_next_actions,
            )

            return calculate_risk_score, generate_checklist, recommend_next_actions
        except Exception as exc:  # pragma: no cover
            raise MCPUnavailableError(f"Could not import MCP tools: {exc}") from exc

    raise MCPUnavailableError(
        "cyber-compliance-mcp is not importable. Install it or keep sibling repo in workspace."
    )


async def _call_tool_stdio(server_command: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call an MCP tool over stdio transport and parse JSON text output."""
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    server = StdioServerParameters(command=server_command, args=[])
    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)

            dumped = result.model_dump()
            if dumped.get("isError"):
                raise MCPUnavailableError(f"MCP tool call failed: {tool_name}")

            content = dumped.get("content", [])
            if not content:
                return {}

            text = content[0].get("text", "{}")
            return json.loads(text)


def _toolset(
    transport: str = "python",
    server_command: str = "cyber-compliance-mcp",
):
    if transport == "python":
        return _import_mcp_tools()

    if transport != "stdio":
        raise MCPUnavailableError(f"Unsupported transport: {transport}")

    def _calculate_risk_score(controls: List[dict]) -> dict:
        return anyio.run(_call_tool_stdio, server_command, "calculate_risk_score", {"controls": controls})

    def _generate_checklist(framework: str, org_type: str = "saas") -> dict:
        return anyio.run(
            _call_tool_stdio,
            server_command,
            "generate_checklist",
            {"framework": framework, "org_type": org_type},
        )

    def _recommend_next_actions(framework: str, gaps: List[str]) -> dict:
        return anyio.run(
            _call_tool_stdio,
            server_command,
            "recommend_next_actions",
            {"framework": framework, "gaps": gaps},
        )

    return _calculate_risk_score, _generate_checklist, _recommend_next_actions


def load_assessment(path: str | Path | None) -> Dict[str, Any]:
    if not path:
        return {"frameworks": {}}

    p = Path(path)
    if not p.exists():
        return {"frameworks": {}}

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return {"frameworks": {}}

    data.setdefault("frameworks", {})
    return data


def save_assessment(path: str | Path, assessment: Dict[str, Any]) -> None:
    p = Path(path)
    p.write_text(json.dumps(assessment, indent=2), encoding="utf-8")


def set_control_status(assessment: Dict[str, Any], framework: str, control: str, status: str) -> None:
    normalized = status.lower().strip()
    if normalized not in VALID_STATUSES:
        normalized = "missing"

    frameworks = assessment.setdefault("frameworks", {})
    fw_data = frameworks.setdefault(framework, {})
    statuses = fw_data.setdefault("statuses", {})
    statuses[control] = normalized


def summarize_framework(
    framework: str,
    assessment: Dict[str, Any],
    org_type: str = "saas",
    transport: str = "python",
    server_command: str = "cyber-compliance-mcp",
) -> Dict[str, Any]:
    calculate_risk_score, generate_checklist, recommend_next_actions = _toolset(transport, server_command)

    checklist_result = generate_checklist(framework=framework, org_type=org_type)
    if checklist_result.get("error"):
        return {
            "framework": framework,
            "error": checklist_result["error"],
            "risk_score": 100.0,
            "risk_level": "critical",
            "missing": 0,
            "partial": 0,
            "implemented": 0,
            "controls_total": 0,
            "controls": [],
        }

    checklist = checklist_result["checklist"]
    framework_assessment = assessment.get("frameworks", {}).get(framework, {})
    status_map = framework_assessment.get("statuses", {})

    controls_for_score: List[Dict[str, str]] = []
    controls_out: List[Dict[str, str]] = []
    missing_gaps: List[str] = []

    for item in checklist:
        control_name = item["control"]
        status = str(status_map.get(control_name, "missing")).lower()
        if status not in VALID_STATUSES:
            status = "missing"

        controls_for_score.append({"control": control_name, "status": status})
        controls_out.append({"control": control_name, "status": status})
        if status == "missing":
            missing_gaps.append(control_name)

    score = calculate_risk_score(controls_for_score)
    recommendations = recommend_next_actions(framework=framework, gaps=missing_gaps[:4])

    return {
        "framework": framework,
        "risk_score": score.get("risk_score", 100.0),
        "risk_level": score.get("risk_level", "critical"),
        "missing": score.get("missing", 0),
        "partial": score.get("partial", 0),
        "implemented": score.get("implemented", 0),
        "controls_total": score.get("controls_total", len(controls_for_score)),
        "actions": recommendations.get("recommended_actions", []),
        "controls": controls_out,
    }


def summarize_all(
    assessment_path: str | None,
    org_type: str = "saas",
    transport: str = "python",
    server_command: str = "cyber-compliance-mcp",
) -> Dict[str, Any]:
    assessment = load_assessment(assessment_path)
    summaries = [
        summarize_framework(
            fw,
            assessment,
            org_type=org_type,
            transport=transport,
            server_command=server_command,
        )
        for fw in SUPPORTED_FRAMEWORKS
    ]

    all_actions: List[str] = []
    for row in summaries:
        all_actions.extend(row.get("actions", []))

    dedup_actions = []
    seen = set()
    for action in all_actions:
        if action not in seen:
            seen.add(action)
            dedup_actions.append(action)

    framework_details = {row["framework"]: row.get("controls", []) for row in summaries}

    return {
        "frameworks": summaries,
        "framework_details": framework_details,
        "priority_actions": dedup_actions[:6],
        "assessment_path": assessment_path,
    }
