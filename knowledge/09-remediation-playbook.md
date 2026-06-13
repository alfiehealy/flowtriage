# Remediation Playbook

Standard remediation sequencing for estate triage output.

## Ordering rules
1. CRITICAL findings first, ordered by score descending.
2. Security findings (credentials) before stability findings (cycles)
   when scores tie — exposure compounds over time.
3. Batch HIGH deprecated-connector migrations by connector, not by flow
   (one migration pattern, applied N times).
4. MEDIUM/LOW items enter the backlog with the rubric score recorded so
   prioritisation survives personnel changes.

## Required output per finding
- Flow name(s) and ID(s)
- Severity + score + rubric citation
- Evidence (the specific definition fragment that triggered the finding)
- Remediation steps referencing the relevant standard document
- Effort estimate: S (<2h), M (<1 day), L (>1 day)

## Escalation rule
Findings that cannot be grounded in the standards library are NOT to be
scored. Output them under "Requires human review" with a plain-language
description of the concern.
