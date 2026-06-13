# Demo video script — target 2:45, hard cap 3:00

Record at 1080p, screen + voiceover. Two takes max. Energy up, pace brisk.
Pre-stage every window before recording (portal on KB page, terminal ready,
triage-report.md rendered in a markdown preview).

---

**[0:00-0:20 — HOOK. Face or title card + estate folder on screen]**

"Every company running Power Automate has hundreds of flows nobody fully
understands. I know — I maintain four hundred and seventy-seven of them in
production. Auditing one flow takes half an hour. Auditing the whole estate
never happens. So I built an agent that does it in minutes. This is
FlowTriage."

**[0:20-0:50 — WHAT & HOW. Architecture diagram, then Foundry portal]**

"FlowTriage is a reasoning agent built on Microsoft Foundry, in the
Reasoning Agents track. The clever bit is the grounding: its entire
judgment model — the risk rubric, the security standards, the deprecation
register — lives in a *Foundry IQ knowledge base*." [show KB in portal]
"So every severity score it produces is a citation to a standard, not an
opinion. Swap the knowledge base for your company's standards, and it
triages by your rules."

**[0:50-2:00 — THE RUN. Terminal: python src/run_triage.py]**

"I'm pointing it at a thirty-flow estate with some landmines buried in it."
[run starts; while it processes, scroll two flow JSONs]
"These are raw flow exports — triggers, actions, connections. No
documentation."
[report appears; scroll to reasoning trace]
"Two-stage architecture: a deterministic analyzer builds the dependency
graph, scans for secrets, checks every connector — same evidence every
run, no LLM guesswork. Then the agent does what LLMs are actually good
at: judgment. And look what the graph turned up — a circular dependency
spanning THREE flows. Zero-eight calls seventeen, seventeen calls
twenty-three, twenty-three calls zero-eight again. Each hop looks fine on
its own; no single flow owner could ever see this loop. The agent
retrieves the child-flow standard from Foundry IQ and judges it CRITICAL,
explaining the blast radius."
[scroll to findings table]
"And here's the judgment the code can't do. The analyzer found
twenty-three flows missing error handling — the agent read the raw
definitions and triaged them: the payroll export gets the plus-ten
business-impact modifier; 'Untitled flow three' stays LOW. The hardcoded
API key? It noticed the flow runs hourly and is enabled, so the exposure
repeats twenty-four times a day — rotate the key BEFORE touching the
flow. The rubric doing all this maths is itself a document retrieved from
Foundry IQ — watch the citations."

**[2:00-2:25 — THE REFUSAL MOMENT. Playground or second terminal]**

"Now the part I care most about — what it does when it *shouldn't* answer."
[ask: "What's the risk severity of flow-99, the payroll reconciliation flow?"]
"Flow ninety-nine doesn't exist. It says so. No fabricated finding, no
guessed severity. There's an eight-case eval suite in the repo proving this
behaviour — refusals, empty estates, prompt injection. Reliability isn't a
claim here, it's a test result."

**[2:25-2:45 — CLOSE. README on screen]**

"Small agent, deep reasoning, zero hallucination — and a pattern already
proven nightly against four hundred and seventy-seven production flows.
Repo's public, evals included, README has the one-command quick start.
FlowTriage. Thanks for watching."

---

## Recording checklist
- [ ] Clean browser profile, no identifying tabs/avatars/tenant names
- [ ] Terminal font size 16+, dark theme, window pre-sized
- [ ] Do a silent dry-run of the triage BEFORE recording so timings are known
- [ ] If the live run is slow, cut the wait — jump-cut to the report
- [ ] Say "Microsoft Foundry", "Foundry IQ", and "Reasoning Agents track"
      out loud (judges checklist-listen for these)
