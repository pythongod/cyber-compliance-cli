from pathlib import Path

from cyber_compliance_cli.mcp_client import load_assessment, save_assessment, set_control_status


def test_editor_save_cycle_persistence(tmp_path: Path):
    p = tmp_path / "assessment.json"
    assessment = load_assessment(str(p))
    set_control_status(assessment, "nist_csf", "GV.OV-01 Governance strategy defined", "implemented")
    save_assessment(str(p), assessment)

    loaded = load_assessment(str(p))
    assert (
        loaded["frameworks"]["nist_csf"]["statuses"]["GV.OV-01 Governance strategy defined"]
        == "implemented"
    )
