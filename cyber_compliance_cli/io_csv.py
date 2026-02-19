from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict

from .mcp_client import SUPPORTED_FRAMEWORKS, load_assessment, save_assessment


def export_assessment_csv(assessment_file: str, output_csv: str) -> Path:
    assessment = load_assessment(assessment_file)
    rows = []
    for framework in SUPPORTED_FRAMEWORKS:
        statuses = assessment.get("frameworks", {}).get(framework, {}).get("statuses", {})
        for control, status in statuses.items():
            rows.append({"framework": framework, "control": control, "status": status})

    out = Path(output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["framework", "control", "status"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return out


def import_assessment_csv(input_csv: str, assessment_file: str) -> Dict[str, Any]:
    assessment = load_assessment(assessment_file)
    frameworks = assessment.setdefault("frameworks", {})

    with Path(input_csv).open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            framework = str(row.get("framework", "")).strip()
            control = str(row.get("control", "")).strip()
            status = str(row.get("status", "missing")).strip().lower()
            if not framework or not control:
                continue
            if status not in {"implemented", "partial", "missing"}:
                status = "missing"

            fw = frameworks.setdefault(framework, {})
            statuses = fw.setdefault("statuses", {})
            statuses[control] = status

    save_assessment(assessment_file, assessment)
    return assessment
