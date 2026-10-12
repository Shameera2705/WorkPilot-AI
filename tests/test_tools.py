from tools import inspect_tickets, search_knowledge_base, write_report, verify_report

def test_ticket_inspection_has_urgent_tickets():
    result = inspect_tickets()
    assert result["ticket_count"] >= 1
    assert result["urgent_count"] >= 1
    assert all("urgent" in ticket for ticket in result["tickets"])

def test_knowledge_base_search_returns_shape():
    result = search_knowledge_base("SLA escalation")
    assert "matches" in result
    assert isinstance(result["matches"], list)

def test_verifier_fails_before_report_exists(tmp_path, monkeypatch):
    import tools
    monkeypatch.setattr(tools, "REPORT_FILE", tmp_path / "missing.md")
    result = tools.verify_report()
    assert result["passed"] is False
    assert result["reason"] == "Report file does not exist."

def test_verifier_detects_missing_urgent_ticket(tmp_path, monkeypatch):
    import tools
    monkeypatch.setattr(tools, "REPORT_FILE", tmp_path / "report.md")
    monkeypatch.setattr(tools, "inspect_tickets", lambda: {"tickets": [{"ticket_id": "T-URGENT-999", "urgent": True}]})
    tools.REPORT_FILE.write_text("# Action plan\n\nA sufficiently long report with action recommendations but no ticket id.", encoding="utf-8")
    result = tools.verify_report()
    assert result["passed"] is False
    assert result["missing_urgent_ids"] == ["T-URGENT-999"]
