"""WorkPilot AI command-line entry point."""
import argparse
import json
import os
from dotenv import load_dotenv
from demo import run_offline_demo

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="WorkPilot AI autonomous task agent")
    parser.add_argument("--task", help="Goal for the agent")
    parser.add_argument("--demo", action="store_true", help="Run the deterministic offline demo (no API required)")
    parser.add_argument("--max-steps", type=int, default=10, help="Maximum model/tool turns")
    args = parser.parse_args()

    if args.demo:
        result = run_offline_demo()
        print(json.dumps(result, indent=2))
        return

    if not (os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")):
        raise SystemExit(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add a key, "
            "or run the offline demo with: python main.py --demo"
        )

    task = args.task or input("What should WorkPilot do? ").strip()
    if not task:
        raise SystemExit("Please provide a task.")
    from agent import WorkPilotAgent
    agent = WorkPilotAgent(max_steps=args.max_steps)
    result = agent.run(task)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
