from __future__ import annotations

from typing import Any, Dict, List

ALLOWED_FRAMEWORKS = {"nist_csf", "iso27001", "soc2", "cis_v8"}
ALLOWED_STATUS = {"implemented", "partial", "missing"}


def validate_assessment(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not isinstance(data, dict):
        return ["assessment must be a JSON object"]

    frameworks = data.get("frameworks")
    if frameworks is None:
        errors.append("missing required key: frameworks")
        return errors
    if not isinstance(frameworks, dict):
        errors.append("frameworks must be an object")
        return errors

    for fw, fw_data in frameworks.items():
        if fw not in ALLOWED_FRAMEWORKS:
            errors.append(f"unsupported framework key: {fw}")
            continue
        if not isinstance(fw_data, dict):
            errors.append(f"framework entry for {fw} must be an object")
            continue

        statuses = fw_data.get("statuses", {})
        if not isinstance(statuses, dict):
            errors.append(f"{fw}.statuses must be an object")
            continue

        for control, status in statuses.items():
            if not isinstance(control, str) or not control.strip():
                errors.append(f"{fw}.statuses contains empty/invalid control key")
            if str(status).lower() not in ALLOWED_STATUS:
                errors.append(
                    f"{fw}.statuses[{control}] invalid status '{status}' (allowed: implemented|partial|missing)"
                )

    return errors
