# Naming and Hygiene Standard (GOV-01)

## Convention
[Department] - [Process] - [Action], e.g. "Finance - Invoice Approval - Route".
Flows named "Untitled flow", "Copy of ...", "..._FINAL", "..._v2" or
all-lowercase fragments violate the standard.

## Severity guidance
Naming violations alone: LOW. They become MEDIUM only when they obstruct
incident response (e.g. duplicate near-identical flows where the live one
cannot be identified).

## Duplicate detection
Two flows with near-identical action graphs and one named "Copy of ..."
indicates an unmanaged clone. Flag the pair and recommend retiring one.
