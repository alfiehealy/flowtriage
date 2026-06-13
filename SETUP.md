# Setup walkthrough (tenant click-path)

Total time: ~45-60 min first run. Do the smoke test (step 5) before
anything else matters.

## 0. Clearances (before touching the portal)
- [ ] Manager sign-off for using the work Azure subscription (synthetic data only, ~£10-20 spend)
- [ ] Hackathon registration completed
- [ ] Resource group exists: `rg-agentsleague` (you need Contributor)

## 1. Foundry project (10 min)
1. Foundry portal → Create project → into `rg-agentsleague`
2. Region: UK South (fall back to Sweden Central if model quota is tight)
3. Deploy a chat model (latest GPT-4-class deployment available to you;
   name the deployment something neutral like `triage-model`)

## 2. Storage for knowledge docs (5 min)
1. Storage account in the same RG → container `knowledge-docs`
2. Upload ONE file only for now: `knowledge/01-risk-scoring-rubric.md`

## 3. Foundry IQ knowledge base (10 min)
1. In the project: Knowledge → Create knowledge base
2. Add knowledge source → the blob container
3. Wait for indexing to complete (watch the status, don't assume)

## 4. Agent (5 min)
1. Agents → New agent → instructions: paste ALL of `src/system_prompt.md`
2. Attach the knowledge base to the agent
3. Copy the agent ID

## 5. SMOKE TEST — the go/no-go gate
In the agent playground ask: "What severity applies to a hardcoded API
key, and what document says so?" You must get CRITICAL with a rubric
citation. If retrieval fails, fix it NOW (check indexing status, KB
attachment, model deployment) before proceeding. Paste errors to Claude.

## 6. Full knowledge upload (5 min)
Upload the remaining 8 docs to the container → reindex → re-ask the smoke
question plus one deprecation question to confirm multi-doc retrieval.

## 7. Run it
```bash
az login
pip install -r requirements.txt
export PROJECT_ENDPOINT="..."   # project overview page
export AGENT_ID="..."
python src/run_triage.py
python src/eval/run_evals.py
```

## 8. Pre-recording hygiene checklist
- [ ] Clean browser profile for recording (no work bookmarks/avatar)
- [ ] No employer name visible in: portal breadcrumbs, resource names,
      subscription name, email addresses, browser tabs
- [ ] triage-report.md and eval outputs reviewed for anything identifying
