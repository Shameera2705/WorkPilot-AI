"""Small reproducible evaluation for tool-level success and verification."""
from demo import run_offline_demo
from tools import inspect_tickets, verify_report

def run_evaluation():
    result = run_offline_demo()
    tickets = inspect_tickets()
    verification = verify_report()
    return {
        "evaluation_name": "workpilot_offline_smoke_test",
        "run_status": result.get("status"),
        "tickets_reviewed": tickets["ticket_count"],
        "urgent_ticket_count": tickets["urgent_count"],
        "verification_passed": verification["passed"],
        "checks": verification.get("checks", {}),
    }

if __name__ == "__main__":
    import json
    report = run_evaluation()
    print(json.dumps(report, indent=2))
    if not report["verification_passed"]:
        raise SystemExit(1)
