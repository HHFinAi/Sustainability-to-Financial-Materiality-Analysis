---
name: materiality-transmission
description: Causal financial transmission for institutional sustainable-finance research; return evidence-linked findings, assumptions, gaps and reviewable outputs.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Causal financial transmission

Read `../../AGENTS.md` and `../../prompts/stages/transmission.md` relative to this skill directory. Obtain the current stage packet using the repository CLI. Do not create or claim unavailable source access.

## Task
For each issue connect trigger -> operational exposure -> volume/price/cost/capex/working capital -> cash flow. State adaptation, pass-through, contractual protection and timing. Separate fact, causal inference and scenario assumption. Do not count the same shock in cash flow and an unexplained discount-rate overlay.

## Deliverable
Return the fields in `../../schemas/artifact.schema.json`; use the current run ID and input digest. Required sections: causal_chain, revenue_margin_capex, credit_channels, double_counting_register. Include source IDs, scope, periods, methods and material gaps. Call only allowlisted calculations with explicit provenance; missing evidence means NEEDS_DATA, not invented values.

## Limit
Scenario arithmetic is not a forecast. Financial materiality and impact materiality are separate; no universal ESG premium or automatic ESG score-to-WACC conversion.
