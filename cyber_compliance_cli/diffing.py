from __future__ import annotations

from typing import Any, Dict, List


def _status_of(assessment: Dict[str, Any], framework: str, control: str) -> str:
    return str(
        assessment.get("frameworks", {})
        .get(framework, {})
        .get("statuses", {})
        .get(control, "missing")
    ).lower()


def compare_assessments(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    frameworks = sorted(set(old.get("frameworks", {}).keys()) | set(new.get("frameworks", {}).keys()))
    improved: List[Dict[str, str]] = []
    regressed: List[Dict[str, str]] = []
    unchanged = 0

    rank = {"missing": 0, "partial": 1, "implemented": 2}

    for fw in frameworks:
        old_controls = set(old.get("frameworks", {}).get(fw, {}).get("statuses", {}).keys())
        new_controls = set(new.get("frameworks", {}).get(fw, {}).get("statuses", {}).keys())
        controls = sorted(old_controls | new_controls)

        for c in controls:
            s_old = _status_of(old, fw, c)
            s_new = _status_of(new, fw, c)
            if rank.get(s_new, -1) > rank.get(s_old, -1):
                improved.append({"framework": fw, "control": c, "from": s_old, "to": s_new})
            elif rank.get(s_new, -1) < rank.get(s_old, -1):
                regressed.append({"framework": fw, "control": c, "from": s_old, "to": s_new})
            else:
                unchanged += 1

    return {
        "frameworks": frameworks,
        "improved": improved,
        "regressed": regressed,
        "unchanged_count": unchanged,
    }
