# Polling Frequency and Consumption Standard (COST-01)

## Policy
Recurrence triggers more frequent than every 15 minutes require written
justification. Each poll consumes API requests against per-user daily
limits; a 5-minute recurrence is 288 runs/day for one flow.

## Severity guidance
- Recurrence interval < 15 min calling an internal/external API: MEDIUM
- Recurrence interval < 15 min with downstream email/Teams actions
  (notification fatigue + quota): MEDIUM, upper band

## Remediation
Prefer event-based triggers (webhooks, "When an item is created") over
polling. Where polling is unavoidable, batch and debounce.
