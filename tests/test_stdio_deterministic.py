from cyber_compliance_cli import mcp_client


def test_stdio_transport_deterministic(monkeypatch):
    def fake_call(server_command, tool_name, arguments):
        if tool_name == "generate_checklist":
            return {
                "framework": arguments["framework"],
                "org_type": arguments["org_type"],
                "checklist": [
                    {"control": "PR.AA-01 Identity and access managed", "status": "not_started"},
                    {"control": "DE.CM-01 Continuous monitoring enabled", "status": "not_started"},
                ],
            }
        if tool_name == "calculate_risk_score":
            return {
                "risk_score": 50.0,
                "risk_level": "high",
                "controls_total": 2,
                "missing": 1,
                "partial": 1,
                "implemented": 0,
            }
        if tool_name == "recommend_next_actions":
            return {
                "recommended_actions": ["Enable SSO + MFA everywhere and review privileged access"]
            }
        raise AssertionError(f"Unexpected tool: {tool_name}")

    monkeypatch.setattr(mcp_client.anyio, "run", lambda fn, *a, **k: fake_call(*a))

    out = mcp_client.summarize_all(None, transport="stdio", server_command="cyber-compliance-mcp")
    assert len(out["frameworks"]) == 4
    first = out["frameworks"][0]
    assert first["controls_total"] == 2
    assert first["risk_level"] == "high"
