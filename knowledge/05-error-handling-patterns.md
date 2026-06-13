# Error Handling Patterns for Flows (REL-02)

## Minimum standard
Every flow on a business-critical path must have at least one action with
a `runAfter` condition covering Failed/TimedOut, which notifies an owner
or logs to the incident channel.

## Severity guidance
- Missing failure handling on flows touching payroll, billing, invoicing,
  or customer communications: MEDIUM, +10 modifier per rubric (score ~50-69)
- Missing failure handling on internal convenience flows: LOW

## Approved patterns
1. Try/Catch via scopes: a "Catch" scope with runAfter [Failed, TimedOut]
2. Terminate with status Failed + message after notification
3. Centralised error logger child flow (preferred for estates > 50 flows)
