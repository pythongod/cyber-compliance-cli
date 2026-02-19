from cyber_compliance_cli.mcp_client import set_control_status, summarize_all


def test_summarize_all_has_frameworks():
    out = summarize_all(None)
    assert "frameworks" in out
    assert len(out["frameworks"]) == 4


def test_priority_actions_present():
    out = summarize_all(None)
    assert isinstance(out["priority_actions"], list)


def test_set_control_status_updates_assessment():
    assessment = {"frameworks": {}}
    set_control_status(assessment, "nist_csf", "GV.OV-01 Governance strategy defined", "implemented")
    assert (
        assessment["frameworks"]["nist_csf"]["statuses"]["GV.OV-01 Governance strategy defined"]
        == "implemented"
    )


import pytest
from cyber_compliance_cli.mcp_client import _unwrap_result, MCPUnavailableError


def test_unwrap_result_ok_payload():
    out = _unwrap_result({"ok": True, "a": 1}, "ctx")
    assert out["a"] == 1
    assert "ok" not in out


def test_unwrap_result_error_raises():
    with pytest.raises(MCPUnavailableError):
        _unwrap_result({"ok": False, "error": {"code": "X", "message": "bad"}}, "ctx")
