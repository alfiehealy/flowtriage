# Connector Deprecation Register (updated 2026-05)

Connectors listed here are deprecated or retired. Flows using them must be
migrated per the timelines below.

| Connector | Internal name | Status | Action required |
|---|---|---|---|
| MSN Weather | shared_msnweather | DEPRECATED - retirement announced, EOL 2026-10-01 | Migrate to Azure Maps Weather via HTTP with managed identity |
| Twitter (legacy) | shared_twitter | RETIRED - API access revoked 2023 | Flow will fail on next trigger poll. Remove or rebuild against X API v2 with paid tier |
| Office 365 Video | shared_office365video | RETIRED | Migrate to Stream on SharePoint |
| Google Calendar (v1) | shared_googlecalendar | DEPRECATED EOL 2026-08 | Migrate to Graph-based calendar actions |

## Detection guidance
Check `connectionReferences` in the flow definition for the internal names
above. A deprecated connector in an ENABLED flow with a recurrence or
event trigger is HIGH severity (will fail on/after EOL). In a SUSPENDED
flow it is MEDIUM.
