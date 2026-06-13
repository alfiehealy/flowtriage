import json
import os
import sys
from pathlib import Path
 
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
 
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_estate import analyze
 
ROOT = Path(__file__).resolve().parents[1]
ESTATE_DIR = ROOT / "estate"
REPORT_PATH = ROOT / "triage-report.md"
 
AGENT_NAME = os.environ.get("AGENT_NAME", "agl-flowtriage-agent")
 
 
def load_estate_json() -> str:
    flows = [json.loads(f.read_text()) for f in sorted(ESTATE_DIR.glob("flow-*.json"))]
    print(f"[estate] loaded {len(flows)} flow definitions")
    return json.dumps(flows, indent=1)
 
 
def main() -> None:
    endpoint = os.environ.get("PROJECT_ENDPOINT")
    if not endpoint:
        sys.exit("PROJECT_ENDPOINT not set.")
 
    evidence_json = json.dumps(analyze(), indent=1)
    print("[analyzer] deterministic evidence generated")
    estate_json = load_estate_json()
 
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai = project.get_openai_client()
    print(f"[agent] calling {AGENT_NAME!r} via Responses API")
 
    prompt = (
        "Run the full judgment protocol (steps 1-7).\n\n"
        "EVIDENCE (deterministic analyzer output):\n```json\n"
        + evidence_json + "\n```\n\n"
        "RAW FLOW DEFINITIONS (context only):\n```json\n"
        + estate_json + "\n```"
    )
 
    conversation = openai.conversations.create()
    response = openai.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
        input=prompt,
    )
 
    report = response.output_text
    print("\n" + "=" * 72 + "\n" + report + "\n" + "=" * 72)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\n[done] report saved to {REPORT_PATH}")
 
 
if __name__ == "__main__":
    main()
