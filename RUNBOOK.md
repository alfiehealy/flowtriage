# RUNBOOK - zero to submitted

Follow top to bottom. Tick as you go. Times are realistic, not optimistic.
If anything errors, copy the full error + what step you were on, paste to
Claude, keep moving on a parallel step.

---

## PHASE 0 - Tonight (20 min)

1. [ ] Teams message to Lex:
   "Entering Microsoft's Agents League hackathon this week (ends Sunday).
   Want to use our Azure sub for a small Foundry project - synthetic data
   only, nothing company-related, spend under £20. Doubles as R&D for the
   Flow Intelligence pattern. OK to proceed?"
2. [ ] Register on the Agents League page (Register button). Confirm you
   get participant status.
3. [ ] Azure portal → Resource groups → Create → name: `rg-agentsleague`,
   region UK South. (If you lack permission, ask whoever owns the sub.)
4. [ ] Post the teaser in the Agents League Discord #projects channel:
   "Building FlowTriage for the Reasoning track - an agent that triages
   inherited Power Automate estates with every severity score grounded in
   a Foundry IQ knowledge base. Demo incoming 👀"
5. [ ] Unzip flowtriage.zip somewhere sensible. Open SETUP.md side by side.

## PHASE 1 - Day 1 morning: infrastructure (60-90 min)

6. [ ] ai.azure.com (Foundry portal) → Create project → into
   `rg-agentsleague`, region UK South.
7. [ ] In the project: Models → Deploy → pick the best GPT-4-class chat
   model you have quota for. Deployment name: `triage-model`.
   Test it in the playground with "hello" - confirm tokens flow.
8. [ ] Azure portal → Storage account (same RG, any cheap config) →
   container `knowledge-docs`.
9. [ ] Upload ONE file: `knowledge/01-risk-scoring-rubric.md`.
10. [ ] Foundry portal → Knowledge (Foundry IQ) → Create knowledge base →
    add the blob container as a knowledge source → wait for indexing to
    show COMPLETE. Do not proceed on "in progress".
11. [ ] Agents → New agent:
    - Model: `triage-model`
    - Instructions: paste the ENTIRE contents of `src/system_prompt.md`
    - Knowledge: attach the knowledge base
    - Save. Copy the agent ID somewhere.

## PHASE 2 - THE SMOKE TEST GATE (10 min, do not skip)

12. [ ] In the agent's playground, ask:
    "What severity applies to a hardcoded API key, and which document
    says so?"
    PASS = answer says CRITICAL and cites the Risk Scoring Rubric (and/or
    credential standard), ideally with a visible retrieval annotation.
    FAIL = generic answer, no citation → check: KB indexing complete? KB
    actually attached to THIS agent? Model deployment healthy? Paste the
    behaviour to Claude if stuck >20 min.
13. [ ] **SCREENSHOT the response showing the retrieval annotation.**
    That's PLACEHOLDER_KB_SCREENSHOT for the README. Take it NOW while
    you're here.

## PHASE 3 - Full knowledge + local run (60-90 min)

14. [ ] Upload the remaining 8 knowledge docs to the container → trigger
    reindex → wait for COMPLETE.
15. [ ] Re-test in playground: "Which connectors are retired and what
    happens to flows using them?" Expect Deprecation Register citations.
16. [ ] Local terminal:
    ```
    cd flowtriage
    python -m venv .venv && .venv\Scripts\activate    (or source .venv/bin/activate)
    pip install -r requirements.txt
    az login
    set PROJECT_ENDPOINT=https://<project>.services.ai.azure.com/api/projects/<name>
    set AGENT_ID=<your agent id>
    ```
    (endpoint is on the project Overview page; use `export` on mac/linux)
17. [ ] Sanity: `python src/analyze_estate.py` - should print the cycle
    08→17→23→08, the flow-11 secret, both deprecated connectors, flow-27
    findings. This needs no Azure and proves the repo locally.
18. [ ] `python src/run_triage.py` - full run. Read triage-report.md
    end to end. Check: reasoning trace present, citations present,
    payroll flow scored above "Untitled flow (3)", human-review section
    sane.
    IF THE SDK ERRORS: paste the full traceback to Claude. PLAN B exists
    (Phase 5) - do not burn more than 45 min here.
19. [ ] `python src/eval/run_evals.py` - note the pass count. If a case
    fails on wording (e.g. refusal phrased differently), paste the output
    to Claude for either a prompt tweak or an assertion tweak. Target 8/8,
    accept 7/8 with the failure honestly noted in the README.

## PHASE 4 - Day 1 evening: lock results (30 min)

20. [ ] Fill the README Testing table with real PASS/FAIL results.
21. [ ] Screenshot the triage report findings table → PLACEHOLDER_HERO.
22. [ ] Discord progress reply on your teaser: "Evals just went 8/8 -
    including the 'refuses to fabricate flows' cases ✅" (adjust to truth).

## PHASE 5 - PLAN B (only if the SDK fought you)

The demo does NOT depend on the Python runner. In the agent playground:
paste the contents of evidence.json, then the estate JSON (open
`src/run_triage.py` to see the exact message format), ask it to run the
judgment protocol. Same agent, same KB, same citations - screen-record
that instead. Keep the runner in the repo marked "CLI runner (SDK surface
evolving - playground path verified)". Honest and judges won't blink.

## PHASE 6 - Day 2 morning: repo goes live (60 min)

23. [ ] github.com → New repo → name `flowtriage`, PUBLIC, no template.
24. [ ] In the flowtriage folder:
    ```
    git init
    git add .
    git commit -m "FlowTriage - grounded automation estate triage (Agents League 2026)"
    git branch -M main
    git remote add origin https://github.com/alfiehealy/flowtriage.git
    git push -u origin main
    ```
25. [ ] Open the repo in an incognito window: README renders? Images
    show? No placeholders left except the video link?
26. [ ] Grep yourself: search the repo (GitHub search bar) for your
    employer's name, your work email, "endpoint", "key". Only env-var
    *references* should appear.

## PHASE 7 - Day 2 afternoon: video (90 min, two takes max)

27. [ ] Pre-stage per docs/demo-video-script.md: clean browser profile,
    portal on the KB page, terminal font 16+, report rendered.
28. [ ] Silent dry run once for timings.
29. [ ] Record take 1. Watch it at 2x checking for identifying info in
    EVERY frame. Re-record once max.
30. [ ] Trim, upload to YouTube as Unlisted. Copy link.
31. [ ] Put the link in the README (two places) → commit → push.
32. [ ] Record the 15-sec GIF per docs/gif-storyboard.md → add to README
    hero + Discord.

## PHASE 8 - Submit (30 min, do NOT leave until Saturday night)

33. [ ] Run docs/submission-checklist.md line by line.
34. [ ] Hackathon site → Projects → Submit: track = Reasoning Agents,
    IQ layer = Foundry IQ, repo link, video link. Re-read the disclaimer.
    Click submit.
35. [ ] Confirm the digital badge / confirmation email arrives.
36. [ ] Final Discord post with GIF + repo + video. Then comment
    substantively on 5-10 other projects and vote in the poll.
37. [ ] Close the laptop. Done.

## Budget guardrail
Everything here should cost £5-15 total. If Azure cost alerts fire above
£25, something is looping - check the model deployment metrics.
