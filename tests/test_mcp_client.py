from cyber_compliance_cli.mcp_client import summarize_all


def test_summarize_all_has_frameworks():
    out = summarize_all(None)
    assert "frameworks" in out
    assert len(out["frameworks"]) == 4


def test_priority_actions_present():
    out = summarize_all(None)
    assert isinstance(out["priority_actions"], list)
