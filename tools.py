"""Constrained tools available to WorkPilot. No arbitrary shell or code execution."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "knowledge_base"
OUTPUT_DIR = ROOT / "output"
TICKETS_FILE = DATA_DIR / "support_tickets.csv"
REPORT_FILE = OUTPUT_DIR / "support_action_plan.md"

def _read_tickets():
    with TICKETS_FILE.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def inspect_tickets():
    """Read the provided support-ticket dataset and calculate urgency deterministically."""
    rows = _read_tickets()
    result = []
    for row in rows:
        priority = row["priority"].strip().lower()
        hours_open = float(row["hours_open"])
        urgent = priority in {"critical", "high"} or hours_open >= 24
        result.append({
            "ticket_id": row["ticket_id"],
            "customer": row["customer"],
            "priority": row["priority"],
            "hours_open": hours_open,
            "issue": row["issue"],
            "urgent": urgent,
        })
    return {"ticket_count": len(result), "urgent_count": sum(r["urgent"] for r in result),
            "tickets": result}

def search_knowledge_base(query: str):
    """Search local Markdown knowledge-base documents for matching lines."""
    query_terms = [t.lower() for t in re.findall(r"[a-zA-Z0-9_-]+", query) if len(t) > 2]
    matches = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(term in line.lower() for term in query_terms):
                matches.append({"file": path.name, "line": line_no, "text": line.strip()})
    return {"query": query, "matches": matches[:20]}

def write_report(markdown: str):
    """Write a Markdown report to the fixed output location (path cannot be supplied by the model)."""
    if not isinstance(markdown, str) or len(markdown.strip()) < 80:
        raise ValueError("Report must be a non-empty Markdown document of at least 80 characters.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(markdown, encoding="utf-8")
    return {"path": str(REPORT_FILE.relative_to(ROOT)), "characters_written": len(markdown)}

def verify_report():
    """Independently verify report existence, basic quality, and inclusion of every urgent ticket ID."""
    if not REPORT_FILE.exists():
        return {"passed": False, "reason": "Report file does not exist.", "missing_urgent_ids": []}
    report = REPORT_FILE.read_text(encoding="utf-8")
    tickets = inspect_tickets()["tickets"]
    urgent_ids = [r["ticket_id"] for r in tickets if r["urgent"]]
    missing = [ticket_id for ticket_id in urgent_ids if ticket_id not in report]
    checks = {
        "file_exists": True,
        "minimum_length": len(report.strip()) >= 80,
        "urgent_ticket_coverage": len(missing) == 0,
        "contains_recommendations": "recommend" in report.lower() or "action" in report.lower(),
    }
    return {"passed": all(checks.values()), "checks": checks,
            "urgent_ticket_ids": urgent_ids, "missing_urgent_ids": missing,
            "report_characters": len(report)}

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "inspect_tickets",
        "description": "Read the support ticket dataset and identify urgent tickets using the deterministic urgency rule.",
        "parameters": {"type": "object", "properties": {}, "required": []}
    }},
    {"type": "function", "function": {
        "name": "search_knowledge_base",
        "description": "Search internal Markdown policy documents for information relevant to a query.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Keywords or question to search for"}},
                       "required": ["query"]}
    }},
    {"type": "function", "function": {
        "name": "write_report",
        "description": "Write the final Markdown report to the fixed output path. Include every urgent ticket ID and evidence-based actions.",
        "parameters": {"type": "object", "properties": {"markdown": {"type": "string", "description": "Complete Markdown report"}},
                       "required": ["markdown"]}
    }},
    {"type": "function", "function": {
        "name": "verify_report",
        "description": "Independently verify the saved report. Call this after writing the report.",
        "parameters": {"type": "object", "properties": {}, "required": []}
    }},
]

TOOL_FUNCTIONS = {
    "inspect_tickets": lambda args: inspect_tickets(),
    "search_knowledge_base": lambda args: search_knowledge_base(args["query"]),
    "write_report": lambda args: write_report(args["markdown"]),
    "verify_report": lambda args: verify_report(),
}

def execute_tool(name, arguments):
    """Execute only registered tools; invalid names and arguments fail closed."""
    if name not in TOOL_FUNCTIONS:
        raise ValueError(f"Tool is not permitted: {name}")
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a JSON object")
    return TOOL_FUNCTIONS[name](arguments)
