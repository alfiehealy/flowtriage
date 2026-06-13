"""
Synthetic Power Automate estate generator for FlowTriage.
Produces 30 flow definition exports (simplified Logic Apps schema) with
4 deliberately planted landmines plus realistic background mess.

Landmines:
  LM1  Circular child-flow dependency spanning THREE flows (08 -> 17 -> 23 -> 08)
  LM2  Hardcoded API key in an HTTP action header (flow 11)
  LM3  Deprecated connector usage (flow 05, 'shared_msnweather'; flow 19, legacy 'shared_twitter')
  LM4  Orphaned flow: disabled, owner left, references a deleted SharePoint list (flow 27)

Background mess (realistic, lower severity):
  - Inconsistent naming conventions
  - Missing error handling (no runAfter failure branches) on most flows
  - A flow with a 5-minute polling trigger hammering an API
  - Shared connection references owned by a single user account
"""
import json, os, random

random.seed(42)
OUT = os.path.join(os.path.dirname(__file__), "estate")
os.makedirs(OUT, exist_ok=True)

OWNERS = ["megan.price@contoso.com", "dylan.hughes@contoso.com", "sioned.evans@contoso.com",
          "tom.bradshaw@contoso.com", "SVC-automation@contoso.com"]
DEPARTED_OWNER = "rhys.morgan@contoso.com"  # left the business; owns the orphan + shared connections

CONNECTORS = {
    "sharepoint": "shared_sharepointonline",
    "outlook": "shared_office365",
    "teams": "shared_teams",
    "dataverse": "shared_commondataserviceforapps",
    "http": "http",
    "approvals": "shared_approvals",
    "excel": "shared_excelonlinebusiness",
    "weather_deprecated": "shared_msnweather",
    "twitter_legacy": "shared_twitter",
}

def base_flow(idx, name, owner, trigger, actions, state="Started", created="2023", connections=None, notes=None):
    return {
        "name": f"flow-{idx:02d}",
        "id": f"/providers/Microsoft.Flow/flows/{idx:02d}a{random.randint(10000,99999)}",
        "properties": {
            "displayName": name,
            "state": state,
            "createdTime": f"{created}-{random.randint(1,12):02d}-{random.randint(1,28):02d}T09:00:00Z",
            "lastModifiedTime": f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}T14:30:00Z",
            "creator": {"userPrincipalName": owner},
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "triggers": trigger,
                "actions": actions,
            },
            "connectionReferences": connections or {},
        },
        **({"_reviewNotes": notes} if notes else {}),
    }

def sp_trigger(list_name, site="https://contoso.sharepoint.com/sites/Operations"):
    return {"When_an_item_is_created": {"type": "ApiConnection",
            "inputs": {"host": {"connectionName": CONNECTORS["sharepoint"]},
                       "parameters": {"dataset": site, "table": list_name}}}}

def recurrence(minutes):
    return {"Recurrence": {"type": "Recurrence", "recurrence": {"frequency": "Minute", "interval": minutes}}}

def manual():
    return {"manual": {"type": "Request", "kind": "Button"}}

def child_flow_call(target_flow_id, action_name="Run_child_flow"):
    return {action_name: {"type": "Workflow",
            "inputs": {"host": {"workflowReferenceName": target_flow_id}},
            "runAfter": {}}}

def email_action(to, subject):
    return {"Send_an_email_V2": {"type": "ApiConnection",
            "inputs": {"host": {"connectionName": CONNECTORS["outlook"]},
                       "parameters": {"emailMessage/To": to, "emailMessage/Subject": subject}},
            "runAfter": {}}}

def conn(*keys, owner=None):
    out = {}
    for k in keys:
        out[CONNECTORS[k]] = {"connectionName": CONNECTORS[k],
                              "source": "Embedded",
                              "connectionOwner": owner or random.choice(OWNERS)}
    return out

flows = []

# ---- LM1: three-hop circular dependency: 08 -> 17 -> 23 -> 08 ----
flows.append((8, base_flow(8, "Customer Onboarding - Master", "megan.price@contoso.com",
    sp_trigger("New Customers"),
    {**child_flow_call("flow-17", "Trigger_provisioning_subflow"),
     **email_action("onboarding@contoso.com", "New customer onboarding started")},
    connections=conn("sharepoint", "outlook"))))

flows.append((17, base_flow(17, "Provisioning Subflow", "dylan.hughes@contoso.com",
    manual(),
    {**child_flow_call("flow-23", "Run_billing_setup"),
     "Create_Dataverse_record": {"type": "ApiConnection",
        "inputs": {"host": {"connectionName": CONNECTORS["dataverse"]},
                   "parameters": {"entityName": "accounts"}}, "runAfter": {}}},
    connections=conn("dataverse"))))

flows.append((23, base_flow(23, "Billing Setup Handler", "sioned.evans@contoso.com",
    manual(),
    {"Notify_master_flow": {"type": "Workflow",
        "inputs": {"host": {"workflowReferenceName": "flow-08"},
                   "comment": "Re-trigger master to refresh status"},
        "runAfter": {}}},
    connections=conn("dataverse", "outlook"))))

# ---- LM2: hardcoded API key ----
flows.append((11, base_flow(11, "Sync Pricing To Legacy CRM", "tom.bradshaw@contoso.com",
    recurrence(60),
    {"Call_legacy_pricing_API": {"type": "Http",
        "inputs": {"method": "POST",
                   "uri": "https://legacy-crm.contoso-internal.net/api/pricing/sync",
                   "headers": {"x-api-key": "sk_live_9f3Kd82mZpQw7Lr4Tn6VbXc1",
                                "Content-Type": "application/json"},
                   "body": {"source": "powerautomate"}},
        "runAfter": {}}},
    connections={})))

# ---- LM3: deprecated connectors ----
flows.append((5, base_flow(5, "Daily Site Weather Email", "megan.price@contoso.com",
    recurrence(1440),
    {"Get_forecast": {"type": "ApiConnection",
        "inputs": {"host": {"connectionName": CONNECTORS["weather_deprecated"]},
                   "parameters": {"units": "Metric", "location": "Cardiff"}}, "runAfter": {}},
     **email_action("fieldops@contoso.com", "Today's site weather")},
    connections=conn("weather_deprecated", "outlook"))))

flows.append((19, base_flow(19, "Social Mentions Tracker", "dylan.hughes@contoso.com",
    {"When_a_new_tweet_appears": {"type": "ApiConnection",
        "inputs": {"host": {"connectionName": CONNECTORS["twitter_legacy"]},
                   "parameters": {"searchQuery": "@contoso"}}},
    },
    {"Append_to_Excel": {"type": "ApiConnection",
        "inputs": {"host": {"connectionName": CONNECTORS["excel"]},
                   "parameters": {"file": "/Shared/SocialMentions.xlsx"}}, "runAfter": {}}},
    connections=conn("twitter_legacy", "excel"))))

# ---- LM4: orphaned flow ----
flows.append((27, base_flow(27, "old_leaver_process_v2_FINAL", DEPARTED_OWNER,
    sp_trigger("Leavers 2022", site="https://contoso.sharepoint.com/sites/HR-Archive"),
    {**email_action("itservicedesk@contoso.com", "Leaver detected - deprovision"),
     "Update_deleted_list": {"type": "ApiConnection",
        "inputs": {"host": {"connectionName": CONNECTORS["sharepoint"]},
                   "parameters": {"dataset": "https://contoso.sharepoint.com/sites/HR-Archive",
                                  "table": "Leavers 2022"}}, "runAfter": {}}},
    state="Suspended", created="2022",
    connections=conn("sharepoint", "outlook", owner=DEPARTED_OWNER),
    notes="Site 'HR-Archive' decommissioned Q3 2024. Owner left the business Jan 2025.")))

# ---- background mess: aggressive polling ----
flows.append((14, base_flow(14, "check stock levels", "tom.bradshaw@contoso.com",
    recurrence(5),
    {"Query_stock_API": {"type": "Http",
        "inputs": {"method": "GET", "uri": "https://erp.contoso-internal.net/api/stock/all"},
        "runAfter": {}},
     **email_action("warehouse@contoso.com", "Stock alert")},
    connections=conn("outlook"))))

# ---- filler flows: plausible, mixed quality ----
FILLER = [
    ("Invoice Approval Routing", "approvals", "sharepoint"),
    ("New Starter IT Checklist", "sharepoint", "teams"),
    ("Weekly KPI Digest", "dataverse", "outlook"),
    ("Expense Receipt Capture", "sharepoint", "approvals"),
    ("Contract Renewal Reminders", "dataverse", "outlook"),
    ("teams_channel_archiver", "teams", "sharepoint"),
    ("Fleet MOT Reminder", "excel", "outlook"),
    ("Holiday Request Sync", "sharepoint", "dataverse"),
    ("CSAT Survey Dispatcher", "dataverse", "outlook"),
    ("supplier-onboarding-NEW", "sharepoint", "approvals"),
    ("Asset Register Updater", "excel", "dataverse"),
    ("Incident P1 Escalation", "teams", "outlook"),
    ("Quote Follow-up Nudger", "dataverse", "outlook"),
    ("DocGen - Sales Proposals", "sharepoint", "outlook"),
    ("Meeting Room No-Show Release", "outlook", "teams"),
    ("Engineer Job Sheet Sync", "sharepoint", "dataverse"),
    ("Copy of Invoice Approval Routing", "approvals", "sharepoint"),
    ("Untitled flow (3)", "sharepoint", "outlook"),
    ("payroll_export_DO_NOT_EDIT", "excel", "outlook"),
    ("Customer Churn Alerter", "dataverse", "teams"),
    ("Site Survey Photo Filer", "sharepoint", "teams"),
    ("Renewals Pipeline Refresher", "dataverse", "excel"),
    ("Webinar Registration Handler", "sharepoint", "outlook"),
]

used = {f[0] for f in flows}
idx_pool = [i for i in range(1, 31) if i not in used]
for (name, c1, c2), idx in zip(FILLER, idx_pool):
    trig = random.choice([sp_trigger(name.split()[0] + " List"), recurrence(random.choice([60, 240, 1440])), manual()])
    actions = {
        f"Step_1_{c1}": {"type": "ApiConnection",
            "inputs": {"host": {"connectionName": CONNECTORS[c1]}, "parameters": {}}, "runAfter": {}},
        f"Step_2_{c2}": {"type": "ApiConnection",
            "inputs": {"host": {"connectionName": CONNECTORS[c2]}, "parameters": {}},
            "runAfter": {f"Step_1_{c1}": ["Succeeded"]}},
    }
    # ~25% of filler flows get proper error handling; the rest don't (realistic)
    if random.random() < 0.25:
        actions["Notify_on_failure"] = {"type": "ApiConnection",
            "inputs": {"host": {"connectionName": CONNECTORS["teams"]},
                       "parameters": {"message": "Flow failed"}},
            "runAfter": {f"Step_2_{c2}": ["Failed", "TimedOut"]}}
    flows.append((idx, base_flow(idx, name, random.choice(OWNERS), trig, actions,
                                 connections=conn(c1, c2))))

flows.sort(key=lambda x: x[0])
for idx, f in flows:
    with open(os.path.join(OUT, f"flow-{idx:02d}.json"), "w") as fh:
        json.dump(f, fh, indent=2)

print(f"Wrote {len(flows)} flows to {OUT}")
print("Landmines: LM1 circular 08->17->23->08 | LM2 hardcoded key flow-11 | "
      "LM3 deprecated connectors flow-05, flow-19 | LM4 orphan flow-27")
