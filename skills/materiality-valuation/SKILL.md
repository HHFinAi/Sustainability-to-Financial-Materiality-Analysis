---
name: materiality-valuation
description: Financial bridge and sensitivity for institutional sustainable-finance research; return evidence-linked findings, assumptions, gaps and reviewable outputs.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Financial bridge and sensitivity

Read `../../AGENTS.md` and `../../prompts/stages/valuation.md` relative to this skill directory. Obtain the current stage packet using the repository CLI. Do not create or claim unavailable source access.

## Task
Reconcile the unadjusted financial model first. Use explicit annual periods, currency and tax convention. Show terminal-value contribution and distinguish debt repayment capacity from equity residual value. Quantify a bounded sensitivity or return NEEDS_DATA.

## Deliverable
Return the fields in `../../schemas/artifact.schema.json`; use the current run ID and input digest. Required sections: baseline_reconciliation, incremental_cashflows, equity_credit_bridge, scenario_sensitivity. Include source IDs, scope, periods, methods and material gaps. Call only allowlisted calculations with explicit provenance; missing evidence means NEEDS_DATA, not invented values.

## Limit
Scenario arithmetic is not a forecast. Financial materiality and impact materiality are separate; no universal ESG premium or automatic ESG score-to-WACC conversion.
