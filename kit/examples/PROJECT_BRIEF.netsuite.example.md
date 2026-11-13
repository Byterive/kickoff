---
title: NetSuite brief example
summary: Filled example PROJECT_BRIEF for a NetSuite sales-order approval customization.
keywords: [example, netsuite, suitescript, brief]
status: draft
updated: 2026-10-17
---

# PROJECT_BRIEF: "SO Approval Automation" (example)

## 1. Goal
Auto-route sales orders over 10,000 to a manager for approval. Done = tested in sandbox, deployment record written.

## 2. Profile
netsuite

## 3. Background and sources
Requirements email thread (docs/requirements/approval-rules.md). Current manual process described in _inbox/process.docx.

## 4. Environment and tools
NetSuite sandbox (account alias SB1; no IDs in files), SuiteScript 2.1, SDF project in src/, VS Code.

## 5. Rules and constraints
Governance: user event must stay under 1,000 usage units. Roles: Sales, Sales Manager.

## 6. Definition of status words
DONE = sandbox test cases logged and passed, permissions verified, rollback plan written.

## 7. Already done / known problems
Saved search "Large Open SOs" exists. Workflow draft exists but does not notify.

## 8. Next steps wanted
1) User event script 2) Email notification 3) Test cases 4) Deployment record.

## 9. Never do
Touch production, edit standard workflows, commit tokens or account IDs, delete custom fields.
