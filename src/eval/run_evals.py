"""
FlowTriage eval harness - runs the 8 reliability cases in eval_cases.json
against the live agent and reports pass/fail per assertion.

Usage:
  PROJECT_ENDPOINT=... AGENT_ID=... python src/eval/run_evals.py

Cases E1-E4 prove grounded multi-step reasoning (detection + citation +
arithmetic). Cases E5-E8 prove safe failure: refusal over fabrication.
Paste the summary table into the README's Testing section.
"""
import json
import os
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze_estate import analyze

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((Path(__file__).parent / "eval_cases.json").read_text())["cases"]
EVIDENCE_JSON = json.dumps(analyze(), indent=1)


def load_estate_json() -> str:
    flows = [json.loads(f.read_text()) for f in sorted((ROOT / "estate").glob("flow-*.json"))]
    return json.dumps(flows, indent=1)


def ask(client, agent, estate_json: str, prompt: str) -> str:
    thread = client.agents.threads.create()
    content = prompt
    # Most cases need the estate as context; E7 supplies its own.
    if "this estate:" not in prompt:
        content = (prompt
                   + "\n\nEVIDENCE:\n```json\n" + EVIDENCE_JSON + "\n```"
                   + "\n\nEstate:\n```json\n" + estate_json + "\n```")
    client.agents.messages.create(thread_id=thread.id, role="user", content=content)
    run = client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    if str(run.status).lower() != "completed":
        return f"<RUN FAILED: {getattr(run, 'last_error', run.status)}>"
    for msg in client.agents.messages.list(thread_id=thread.id):
        if msg.role == "assistant":
            return "\n".join(b.text.value for b in msg.content if getattr(b, "text", None))
    return "<NO RESPONSE>"


def check(case: dict, response: str) -> list[tuple[str, bool]]:
    results, low = [], response.lower()
    for needle in case.get("must_contain", []):
        results.append((f"contains '{needle}'", needle.lower() in low))
    for needle in case.get("must_not_contain", []):
        results.append((f"absent   '{needle}'", needle.lower() not in low))
    if cite := case.get("must_cite"):
        results.append((f"cites    '{cite}'", cite.lower() in low))
    return results


def main() -> None:
    endpoint, agent_id = os.environ.get("PROJECT_ENDPOINT"), os.environ.get("AGENT_ID")
    if not endpoint or not agent_id:
        sys.exit("Set PROJECT_ENDPOINT and AGENT_ID (evals require the grounded portal agent).")

    client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    agent = client.agents.get_agent(agent_id)
    estate_json = load_estate_json()

    print(f"Running {len(CASES)} eval cases against agent '{agent.name}'\n")
    passed_cases = 0
    for case in CASES:
        response = ask(client, agent, estate_json, case["prompt"])
        results = check(case, response)
        ok = all(r for _, r in results)
        passed_cases += ok
        print(f"{'PASS' if ok else 'FAIL'}  {case['id']}  - {case['tests']}")
        for label, r in results:
            print(f"        {'✓' if r else '✗'} {label}")
        (ROOT / "src" / "eval" / f"output_{case['id']}.md").write_text(response)

    print(f"\n{passed_cases}/{len(CASES)} cases passed. "
          "Per-case outputs saved alongside this script for the README.")


if __name__ == "__main__":
    main()
