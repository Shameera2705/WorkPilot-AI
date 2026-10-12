# WorkPilot AI

**An autonomous enterprise task-execution prototype** demonstrating planning, tool use, persistent audit logs, independent verification, and bounded execution.

## Why this project
WorkPilot triages a sample support-ticket dataset, retrieves relevant internal guidance, creates an action-plan report, and independently verifies whether all urgent ticket IDs appear in the saved deliverable.

## Features
- LLM-driven tool selection through OpenAI-compatible Chat Completions function calling.
- Restricted tool registry: inspect tickets, search local Markdown guidance, write a report, verify a report.
- Fixed output path; the model cannot choose arbitrary filesystem paths.
- SQLite run and tool-event audit log.
- Bounded model turns and tool-call count.
- Independent verifier checks report existence, length, action content, and coverage of all urgent ticket IDs.
- Offline demo mode works without an API key. It is a deterministic demonstration, not an LLM-driven autonomous run.
- Pytest unit tests and a repeatable smoke evaluation.

## Architecture
`User goal -> Agent loop -> LLM tool selection -> Allowlisted tools -> SQLite audit log -> Independent verifier -> Verified result`

The LLM proposes tool calls; Python validates and executes only registered tools. The verifier uses the ticket dataset independently rather than trusting the model's claims.

## Setup (Windows PowerShell)
1. Install Python 3.10+ and Git.
2. Open this folder in VS Code.
3. Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If `py` is not available, try `python` instead.

4. Run the offline demo (no API key required):

```powershell
python main.py --demo
```

5. Run tests and the smoke evaluation:

```powershell
python -m pytest -q
python evaluation.py
```

## Enable the LLM-driven agent
1. Copy `.env.example` to `.env`.
2. Add an API key that has API access and billing/credits enabled.
3. Keep `.env` private; it is ignored by Git.
4. Run:

```powershell
python main.py --task "Triage the support tickets, consult relevant guidance, create a prioritized action plan, save it, and verify all urgent ticket IDs are covered."
```

Set `OPENAI_MODEL` in `.env` to a model available to your API account. API access and ChatGPT subscription access are separate.

## Optional UI
After installing requirements:

```powershell
streamlit run app.py
```

Use **Run offline demo** if no API key is configured. The LLM agent button is enabled only when a key is present.

## Dataset and urgency rule
This project uses fictional sample support tickets. A ticket is urgent if its priority is `critical` or `high`, or it has been open for at least 24 hours. This is a prototype rule for reproducible evaluation, not a universal support policy.

## Evaluation
The smoke evaluation reports dataset size, urgent-ticket count, and independent verification outcome. Run it with `python evaluation.py`. Do not claim measured reliability beyond tests you actually run. Extend this benchmark with more tasks and injected tool failures before making performance claims.

## Limitations and next steps
- The LLM run requires an API key and network access.
- Knowledge-base search is a simple local keyword search, not semantic retrieval.
- The browser automation integration is not yet implemented.
- Checkpointing currently persists run and event history; full mid-run resume is future work.
- Add broader benchmark cases, permission boundaries, prompt-injection tests, and stronger report-quality checks.

## Security
No arbitrary shell execution is exposed to the model. The report path is fixed in code. Do not use real customer data or put secrets in the repository.
