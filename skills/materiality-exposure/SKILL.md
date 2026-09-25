---
name: materiality-exposure
description: Economic exposure and materiality for institutional sustainable-finance research; return evidence-linked findings, assumptions, gaps and reviewable outputs.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Economic exposure and materiality

Read `../../AGENTS.md` and `../../prompts/stages/exposure.md` relative to this skill directory. Obtain the current stage packet using the repository CLI. Do not create or claim unavailable source access.

## Task
Map each issue to product, geography, asset and value-chain node. Define exposure denominator, time horizon and evidence quality. Identify upside and downside. Preserve human/ecological harm even where financial transmission is unproven.

## Deliverable
Return the fields in `../../schemas/artifact.schema.json`; use the current run ID and input digest. Required sections: business_model, issue_inventory, time_horizons, financial_vs_impact_materiality. Include source IDs, scope, periods, methods and material gaps. Call only allowlisted calculations with explicit provenance; missing evidence means NEEDS_DATA, not invented values.

## Limit
Scenario arithmetic is not a forecast. Financial materiality and impact materiality are separate; no universal ESG premium or automatic ESG score-to-WACC conversion.
