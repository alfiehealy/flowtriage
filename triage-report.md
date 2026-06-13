### Estate summary
- Inputs present: deterministic EVIDENCE + raw flow definitions (30 flows).
- Inventory: 30 flows total; **29 Started**, **1 Suspended**.
- Connectors in use (8): approvals, Dataverse, Excel, MSN Weather, Office 365, SharePoint, Teams, Twitter.
- Deterministic findings counts:
  - Cycles: **1** (3-flow loop)
  - Secrets: **1** (hardcoded API key)
  - Deprecated connectors: **2**
  - Departed owner: **3** evidence items (1 flow-owner, 2 connection-owner) affecting **flow-27**
  - Aggressive polling: **1**
  - Missing error handling: **23 flows**
  - Duplicate-name suspects: **1 pair**

### Reasoning trace
(Per finding: evidence → standard → judgment + score arithmetic)

1) **Circular child-flow invocation (cycle)**
- Evidence: cycle path `flow-08 → flow-17 → flow-23 → flow-08` (dependency_edges and cycles).
- Standard: Child Flow Design Guide (anti-pattern: circular invocation is **CRITICAL**).【9:3†source】  
  Rubric: CRITICAL = 90–100; +10 modifier if touches billing/customer-facing comms.【6:0†source】
- Context from raw defs: `flow-23` is **Billing Setup Handler**; `flow-08` is **Customer Onboarding - Master** and sends onboarding email.
- Judgment: **CRITICAL**. Score = base 90 + 10 (billing/customer-facing path) = **100** (cap at rubric max).【6:0†source】【9:3†source】

2) **Hardcoded API key in flow definition**
- Evidence: `flow-11` “Sync Pricing To Legacy CRM” has HTTP header `x-api-key` with `sk_live_***`.
- Standard: Credential Handling Standard (SEC-04): hardcoded secrets in headers/definition are **CRITICAL**; remediation steps prescribed (rotate, Key Vault, secret env var/custom connector).【6:1†source】  
  Rubric: hardcoded credentials are CRITICAL (90–100).【6:0†source】
- Judgment: **CRITICAL**. Score = **95** (within CRITICAL band).【6:0†source】【6:1†source】

3) **Deprecated/retired connector: Twitter (legacy)**
- Evidence: `flow-19` uses `shared_twitter`, state Started.
- Standard: Deprecation Register: `shared_twitter` is **RETIRED** (API access revoked 2023) and will fail; enabled flow = **HIGH**.【6:3†source】  
  Rubric: HIGH = 70–89 (“will fail/unsupportable on known date” class).【6:0†source】
- Judgment: **HIGH**. Score = **85** (already effectively nonfunctional on trigger).【6:0†source】【6:3†source】

4) **Deprecated connector: MSN Weather (EOL date)**
- Evidence: `flow-05` uses `shared_msnweather`, state Started.
- Standard: Deprecation Register: `shared_msnweather` DEPRECATED, **EOL 2026-10-01**; enabled recurrence/event flows using deprecated connectors = **HIGH**.【6:3†source】  
  Rubric: HIGH = 70–89.【6:0†source】
- Judgment: **HIGH**. Score = **75** (time-bound retirement risk).【6:0†source】【6:3†source】

5) **Aggressive polling (5-minute recurrence calling API + email)**
- Evidence: `flow-14` interval_minutes = 5.
- Standard: Polling Frequency & Consumption Standard: recurrence <15 min calling API is **MEDIUM**; with downstream email/Teams is MEDIUM upper band.【9:2†source】  
  Rubric: MEDIUM = 40–69.【6:0†source】
- Judgment: **MEDIUM**. Score = **65**.【6:0†source】【9:2†source】

6) **Departed owner / orphaned flow (Suspended)**
- Evidence: `flow-27` suspended; flow owner departed + connection owners departed (SharePoint + Office365); notes include decommissioned HR-Archive site.
- Standard: Ownership & Orphan Policy: orphaned + SUSPENDED = **MEDIUM** (reduced live risk but liability); departed connection owners are a failure risk when enabled, but suspension reduces live impact.【6:4†source】  
  Rubric modifiers: +10 if connection owner left; -10 if Suspended/Stopped.【6:0†source】
- Judgment: **MEDIUM** (because flow is Suspended). Score = base 50 +10 (departed owner risk present) -10 (Suspended) = **50**.【6:0†source】【6:4†source】

7) **Missing error handling (business-critical subset)**
- Evidence: missing_error_handling includes `flow-08` (Customer Onboarding - Master) and `flow-23` (Billing Setup Handler), among others.
- Standard: Error Handling Patterns: missing failure handling on flows touching billing/customer communications = **MEDIUM** +10 modifier per rubric.【6:2†source】  
  Rubric: +10 modifier for payroll/billing/customer-facing comms.【6:0†source】
- Judgment:
  - `flow-23` (Billing): **MEDIUM**. Score = 50 +10 = **60**.【6:0†source】【6:2†source】
  - `flow-08` (Customer onboarding notifications): **MEDIUM**. Score = 50 +10 = **60**.【6:0†source】【6:2†source】

8) **Missing error handling (remaining 21 flows)**
- Evidence: the rest of the missing_error_handling list (e.g., flow-04, 05, 06, 07, 09–15, 17–22, 25, 27, 28, 30).
- Standard: Error Handling Patterns: internal convenience flows missing failure handling are **LOW**.【6:2†source】  
  Rubric: LOW = 1–39.【6:0†source】
- Judgment: **LOW** as a batched hygiene item pending confirmation of customer-facing scope. Score = **30**.【6:0†source】【6:2†source】

9) **Duplicate-name suspects (unmanaged clone risk)**
- Evidence: duplicate_name_suspects base_name “invoice approval routing” for `flow-01` and `flow-24`.
- Standard: Naming & Hygiene Standard: naming/duplicate clones are **LOW** unless obstructing incident response; “Copy of …” indicates unmanaged clone; flag pair and recommend retiring one.【9:1†source】  
  Rubric: LOW = 1–39.【6:0†source】
- Judgment: **LOW**. Score = **25**.【6:0†source】【9:1†source】

### Prioritised findings
| Rank | Flow(s) | Finding | Severity + score | Citation | Effort |
|---:|---|---|---|---|---|
| 1 | flow-08, flow-17, flow-23 | Circular invocation cycle `08→17→23→08` (guaranteed loop/throttle risk) | **CRITICAL 100** (90 +10 billing/customer path) |【6:0†source】【9:3†source】 | L |
| 2 | flow-11 | Hardcoded secret (`x-api-key`) in HTTP action | **CRITICAL 95** |【6:0†source】【6:1†source】 | M |
| 3 | flow-19 | Uses retired `shared_twitter` connector (will fail) | **HIGH 85** |【6:0†source】【6:3†source】 | L |
| 4 | flow-05 | Uses deprecated `shared_msnweather` (EOL **2026-10-01**) | **HIGH 75** |【6:0†source】【6:3†source】 | M |
| 5 | flow-14 | 5-minute polling + API + email (cost/quota + fatigue) | **MEDIUM 65** |【6:0†source】【9:2†source】 | S |
| 6 | flow-23, flow-08 | Missing failure handling on billing/onboarding path | **MEDIUM 60** |【6:0†source】【6:2†source】 | M |
| 7 | flow-27 | Orphaned (departed owner) + decommissioned site refs; flow is Suspended | **MEDIUM 50** (50 +10 -10) |【6:0†source】【6:4†source】 | S–M |
| 8 | 21 flows (see evidence list excluding flow-08, flow-23) | Missing failure handling (batch hygiene item) | **LOW 30** |【6:0†source】【6:2†source】 | M |
| 9 | flow-01, flow-24 | Duplicate/clone “Invoice Approval Routing” vs “Copy of …” | **LOW 25** |【6:0†source】【9:1†source】 | S |

### Remediation plan
(Sequenced per playbook ordering rules.)【6:5†source】

1) **Break the cycle (flow-08/17/23)**
- Remove `flow-23 → flow-08` “re-trigger master” call, or replace with a non-invoking status update mechanism (e.g., write status to Dataverse/SharePoint that `flow-08` reads), ensuring call depth ≤2 and no cycles.【9:3†source】
- Add explicit “respond” semantics for child flows where applicable so parent control returns cleanly.【9:3†source】

2) **Contain the credential exposure (flow-11)**
- Rotate the exposed key at the source system immediately.
- Store the replacement in Azure Key Vault and reference via a **Secret** environment variable (or move to a connector/OAuth pattern).【6:1†source】
- Re-run access review to determine who had co-owner/export access during exposure window (human step; see “Requires human review”).

3) **Connector lifecycle migrations (batch by connector)**
- `shared_twitter` (flow-19): decide **retire vs rebuild** against X API v2 (paid tier) or alternative social listening source; remove dead trigger if retiring.【6:3†source】
- `shared_msnweather` (flow-05): migrate to the prescribed replacement (Azure Maps Weather via HTTP + managed identity) before **2026-10-01**.【6:3†source】

4) **Stabilize reliability/cost**
- flow-14: move from 5-minute recurrence to event-based trigger if available; otherwise increase interval ≥15 min and debounce notifications.【9:2†source】
- Add standard try/catch scopes (or a consistent failure notification action with `runAfter: [Failed, TimedOut]`) to prioritized flows first (flow-23, flow-08), then batch the remaining set.【6:2†source】

5) **Governance cleanup**
- flow-27 (Suspended): reassign ownership to a service account or formally delete after confirming it is obsolete (HR-Archive decommissioned). Document the decision in description/change record.【6:4†source】
- flow-01 vs flow-24: confirm which is authoritative and retire/disable the clone; rename to match the naming convention.【9:1†source】

### Requires human review
- **Customer-facing impact confirmation for missing error handling:** Several flows have display names suggesting external/customer comms (e.g., “CSAT Survey Dispatcher”, “Quote Follow-up Nudger”, “DocGen - Sales Proposals”, “Customer Churn Alerter”), but the provided definitions don’t show explicit recipients/content. Confirm whether they send customer communications; if yes, re-score/apply the rubric +10 modifier and prioritize accordingly.【6:0†source】【6:2†source】
- **Security incident handling for the exposed API key (flow-11):** confirm key scope, rotation completion timestamp, and whether any anomalous use occurred during the exposure window (needs SOC/app-owner input).【6:1†source】
- **Disposition decision for Twitter flow (flow-19):** business owner decision required (retire vs fund rebuild on paid X API tier).【6:3†source】