# Flow Ownership and Orphan Policy (GOV-03)

## Policy
Every production flow must have at least two co-owners, one of which
should be a service account for business-critical automations. Connections
must not be solely owned by an individual user account.

## Orphan definition
A flow is ORPHANED when any of: its creator/owner has left the
organisation; it references decommissioned resources (deleted sites,
lists, environments); it is suspended with no owner able to re-enable it.

## Severity guidance
- Orphaned + ENABLED + business-critical: HIGH (single point of failure)
- Orphaned + SUSPENDED: MEDIUM (-10 modifier per rubric: reduced live
  risk, but blocks audits and may hold stale permissions)
- Shared connections owned by a departed user: HIGH — dependent flows
  fail when the account is disabled by leaver process

## Remediation
Reassign ownership to a service account, re-point or retire dead
references, and document the decision in the flow description.
