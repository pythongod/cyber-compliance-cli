from pathlib import Path

from cyber_compliance_cli.io_csv import export_assessment_csv, import_assessment_csv
from cyber_compliance_cli.mcp_client import load_assessment
from cyber_compliance_cli.reporting import render_markdown_report


def test_csv_roundtrip(tmp_path: Path):
    assessment = tmp_path / "assessment.json"
    assessment.write_text('{"frameworks":{"nist_csf":{"statuses":{"A":"implemented"}}}}', encoding="utf-8")

    csv_out = tmp_path / "assessment.csv"
    export_assessment_csv(str(assessment), str(csv_out))
    assert csv_out.exists()

    assessment2 = tmp_path / "assessment2.json"
    import_assessment_csv(str(csv_out), str(assessment2))
    data = load_assessment(str(assessment2))
    assert data["frameworks"]["nist_csf"]["statuses"]["A"] == "implemented"


def test_markdown_report_render():
    md = render_markdown_report({
        "frameworks": [{"framework": "nist_csf", "risk_level": "high", "risk_score": 70, "implemented": 1, "partial": 2, "missing": 3}],
        "priority_actions": ["Do X"],
    })
    assert "# Cyber Compliance Report" in md
    assert "NIST CSF" in md
