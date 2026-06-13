"""
FlowTriage deterministic analyzer.

Separation of concerns:
  THIS MODULE (deterministic): parse the estate, build the dependency
  graph, detect cycles, scan for literal secrets, flag deprecated
  connectors, polling intervals, error-handling coverage, ownership risks.
  Same input -> same evidence, every run.

  THE AGENT (grounded judgment): takes this evidence plus the raw
  definitions, retrieves the standards from the Foundry IQ knowledge base,
  assigns severities with rubric arithmetic, sequences remediation, and
  routes anything ungroundable to human review.

Usage:
  python src/analyze_estate.py            # prints + writes evidence.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ESTATE_DIR = ROOT / "estate"
EVIDENCE_PATH = ROOT / "evidence.json"

# Internal names of deprecated/retired connectors. The *authority* for
# status, EOL dates, and severity lives in the knowledge base
# (02-connector-deprecation-register.md); this list only enables detection.
DEPRECATED_CONNECTORS = {
    "shared_msnweather",
    "shared_twitter",
    "shared_office365video",
    "shared_googlecalendar",
}

SECRET_HEADER_PATTERN = re.compile(
    r"x-api-key|authorization|ocp-apim-subscription-key|client_secret", re.I
)
SECRET_VALUE_PATTERN = re.compile(r"^(sk_|key_|Bearer\s+\S{12,}|[A-Za-z0-9+/_-]{20,})")

DEPARTED_MARKERS = ("rhys.morgan",)  # demo estate; production would query Entra
POLLING_THRESHOLD_MINUTES = 15
FAILURE_STATUSES = {"Failed", "TimedOut"}


def load_flows() -> list[dict]:
    return [json.loads(f.read_text()) for f in sorted(ESTATE_DIR.glob("flow-*.json"))]


def walk_actions(actions: dict):
    """Yield (name, action) including actions nested in scopes."""
    for name, action in (actions or {}).items():
        yield name, action
        if isinstance(action, dict) and isinstance(action.get("actions"), dict):
            yield from walk_actions(action["actions"])


def build_dependency_graph(flows: list[dict]) -> dict[str, list[str]]:
    graph = {}
    for flow in flows:
        src = flow["name"]
        edges = []
        for _, action in walk_actions(flow["properties"]["definition"].get("actions", {})):
            if action.get("type") == "Workflow":
                target = action.get("inputs", {}).get("host", {}).get("workflowReferenceName")
                if target:
                    edges.append(target)
        graph[src] = edges
    return graph


def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """DFS cycle detection; returns each distinct cycle path once."""
    cycles, seen = [], set()

    def dfs(node, path, on_path):
        for nxt in graph.get(node, []):
            if nxt in on_path:
                cycle = path[path.index(nxt):] + [nxt]
                key = frozenset(cycle)
                if key not in seen:
                    seen.add(key)
                    cycles.append(cycle)
            elif nxt in graph:
                dfs(nxt, path + [nxt], on_path | {nxt})

    for start in graph:
        dfs(start, [start], {start})
    return cycles


def scan_secrets(flow: dict) -> list[dict]:
    hits = []
    for name, action in walk_actions(flow["properties"]["definition"].get("actions", {})):
        if action.get("type") != "Http":
            continue
        headers = action.get("inputs", {}).get("headers", {}) or {}
        for header, value in headers.items():
            if SECRET_HEADER_PATTERN.search(header) and isinstance(value, str) \
                    and SECRET_VALUE_PATTERN.search(value):
                hits.append({"action": name, "header": header,
                             "value_preview": value[:8] + "***REDACTED***"})
    return hits


def analyze() -> dict:
    flows = load_flows()
    graph = build_dependency_graph(flows)

    evidence = {
        "inventory": {
            "flow_count": len(flows),
            "by_state": {},
            "connectors_in_use": sorted({c for f in flows
                                         for c in f["properties"].get("connectionReferences", {})}),
        },
        "dependency_edges": [{"from": s, "to": t} for s, ts in graph.items() for t in ts],
        "cycles": find_cycles(graph),
        "secret_findings": [],
        "deprecated_connector_findings": [],
        "departed_owner_findings": [],
        "aggressive_polling_findings": [],
        "missing_error_handling": [],
        "duplicate_name_suspects": [],
    }

    names_lower = {}
    for flow in flows:
        p = flow["properties"]
        name, display, state = flow["name"], p["displayName"], p.get("state", "Unknown")
        evidence["inventory"]["by_state"][state] = evidence["inventory"]["by_state"].get(state, 0) + 1

        if hits := scan_secrets(flow):
            evidence["secret_findings"].append({"flow": name, "display": display, "hits": hits})

        for conn, meta in p.get("connectionReferences", {}).items():
            if conn in DEPRECATED_CONNECTORS:
                evidence["deprecated_connector_findings"].append(
                    {"flow": name, "display": display, "connector": conn, "state": state})
            owner = (meta or {}).get("connectionOwner", "")
            if any(m in owner for m in DEPARTED_MARKERS):
                evidence["departed_owner_findings"].append(
                    {"flow": name, "connection": conn, "owner": owner, "state": state,
                     "kind": "connection_owner_departed"})

        creator = p.get("creator", {}).get("userPrincipalName", "")
        if any(m in creator for m in DEPARTED_MARKERS):
            evidence["departed_owner_findings"].append(
                {"flow": name, "owner": creator, "state": state, "kind": "flow_owner_departed",
                 "notes": flow.get("_reviewNotes")})

        triggers = p["definition"].get("triggers", {})
        for _, trig in triggers.items():
            rec = trig.get("recurrence", {})
            if rec.get("frequency") == "Minute" and rec.get("interval", 999) < POLLING_THRESHOLD_MINUTES:
                evidence["aggressive_polling_findings"].append(
                    {"flow": name, "display": display, "interval_minutes": rec["interval"]})

        handled = any(
            any(s in FAILURE_STATUSES for deps in (a.get("runAfter") or {}).values() for s in deps)
            for _, a in walk_actions(p["definition"].get("actions", {}))
        )
        if not handled:
            evidence["missing_error_handling"].append({"flow": name, "display": display})

        key = display.lower().replace("copy of ", "").strip()
        names_lower.setdefault(key, []).append(name)

    evidence["duplicate_name_suspects"] = [
        {"base_name": k, "flows": v} for k, v in names_lower.items() if len(v) > 1
    ]

    return evidence


def main() -> None:
    evidence = analyze()
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2))

    inv = evidence["inventory"]
    print(f"Flows: {inv['flow_count']}  states: {inv['by_state']}")
    print(f"Dependency edges: {len(evidence['dependency_edges'])}")
    print(f"CYCLES: {evidence['cycles'] or 'none'}")
    print(f"Secret findings: {[(f['flow'], h['header']) for f in evidence['secret_findings'] for h in f['hits']]}")
    print(f"Deprecated connectors: {[(f['flow'], f['connector']) for f in evidence['deprecated_connector_findings']]}")
    print(f"Departed-owner findings: {[(f['flow'], f['kind']) for f in evidence['departed_owner_findings']]}")
    print(f"Aggressive polling: {[(f['flow'], f['interval_minutes']) for f in evidence['aggressive_polling_findings']]}")
    print(f"Missing error handling: {len(evidence['missing_error_handling'])} flows")
    print(f"Duplicate suspects: {[d['flows'] for d in evidence['duplicate_name_suspects']]}")
    print(f"\nEvidence written to {EVIDENCE_PATH}")


if __name__ == "__main__":
    main()
