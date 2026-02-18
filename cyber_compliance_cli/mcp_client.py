from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

SUPPORTED_FRAMEWORKS = ["nist_csf", "iso27001", "soc2", "cis_v8"]


class MCPUnavailableError(RuntimeError):
    pass


def _import_mcp_tools():
    """Import MCP tool functions from local package or sibling repo checkout."""
    try:
        from cyber_compliance_mcp.core import (  # type: ignore
            calculate_risk_score,
            generate_checklist,
            recommend_next_actions,
        )

        return calculate_risk_score, generate_checklist, recommend_next_actions
    except Exception:
        pass

    # Fallback: sibling repo checkout in OpenClaw workspace
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


def load_assessment(path: str | Path | None) -> Dict[str, Any]:
    """Load assessment JSON.

    Expected structure:
    {
      "frameworks": {
        "nist_csf": {
          "statuses": {
            "GV.OV-01 Governance strategy defined": "implemented",
            "ID.AM-01 Asset inventory maintained": "partial"
          }
        }
      }
    }
    """
    if not path:
        return {}

    p = Path(path)
    if not p.exists():
        return {}

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return {}
    return data


def summarize_framework(framework: str, assessment: Dict[str, Any], org_type: str = "saas") -> Dict[str, Any]:
    calculate_risk_score, generate_checklist, recommend_next_actions = _import_mcp_tools()

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
        }

    checklist = checklist_result["checklist"]

    framework_assessment = (
        assessment.get("frameworks", {}).get(framework, {}) if isinstance(assessment, dict) else {}
    )
    status_map = framework_assessment.get("statuses", {}) if isinstance(framework_assessment, dict) else {}

    controls_for_score: List[Dict[str, str]] = []
    missing_gaps: List[str] = []
    for item in checklist:
        control_name = item["control"]
        status = str(status_map.get(control_name, "missing")).lower()
        if status not in {"implemented", "partial", "missing"}:
            status = "missing"
        controls_for_score.append({"control": control_name, "status": status})
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
    }


def summarize_all(assessment_path: str | None, org_type: str = "saas") -> Dict[str, Any]:
    assessment = load_assessment(assessment_path)
    summaries = [summarize_framework(fw, assessment, org_type=org_type) for fw in SUPPORTED_FRAMEWORKS]

    all_actions: List[str] = []
    for row in summaries:
        all_actions.extend(row.get("actions", []))

    dedup_actions = []
    seen = set()
    for action in all_actions:
        if action not in seen:
            seen.add(action)
            dedup_actions.append(action)

    return {
        "frameworks": summaries,
        "priority_actions": dedup_actions[:6],
        "assessment_path": assessment_path,
    }
