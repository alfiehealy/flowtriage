# Automation Risk Scoring Rubric (v2.1)

Standard severity model for triaging Power Automate flows. All triage
recommendations MUST reference this rubric when assigning a severity.

## Severity levels

| Severity | Score | Definition | Response time |
|---|---|---|---|
| CRITICAL | 90-100 | Active security exposure or guaranteed runtime failure (hardcoded credentials, circular execution, data loss path) | Remediate within 48 hours |
| HIGH | 70-89 | Will fail or become unsupportable on a known date (deprecated connector with announced retirement, single point of failure on a departed owner) | Remediate within 2 weeks |
| MEDIUM | 40-69 | Degraded reliability or cost (missing error handling on business-critical path, aggressive polling, orphaned but disabled flows) | Plan into next sprint |
| LOW | 1-39 | Hygiene issues (naming conventions, duplicate flows, missing descriptions) | Backlog |

## Scoring modifiers
- +10 if the flow touches payroll, billing, or customer-facing communications
- +10 if the connection owner has left the organisation
- -10 if the flow is in a Suspended/Stopped state (reduced live risk, still a liability)

## Mandatory rule
A finding without a rubric citation is invalid. If a risk type is not
covered by this rubric or the other standards documents, escalate to a
human reviewer rather than assigning an unsupported severity.
