# Child Flow Design Guide

## Approved pattern
Parent flows may call child flows (Workflow action type) to a maximum
depth of 2 (parent -> child -> grandchild). Child flows must use the
"Respond to a PowerApp or flow" action to return control.

## Anti-pattern: circular invocation
A cycle (A calls B, B calls C, C calls A - directly or at any depth) causes:
- Infinite trigger loops consuming API request quota
- Run history flooding making diagnosis impossible
- Potential throttling of the entire environment by the platform

Circular invocation at ANY depth is CRITICAL severity (rubric v2.1,
"guaranteed runtime failure" class). Multi-hop cycles (3+ flows) are the
most dangerous because no single flow owner can see the loop.

## Detection guidance
Build a directed graph of Workflow-type actions across the estate
(edge = flow X invokes flow Y via workflowReferenceName). Any cycle in the
graph is a finding. Report the full cycle path.
