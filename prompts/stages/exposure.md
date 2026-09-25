# Economic exposure and materiality

## Decision context
Which sustainability issues change revenue, margins, cash flows, credit or valuation, by how much and under which assumptions?

## Assignment
Map each issue to product, geography, asset and value-chain node. Define exposure denominator, time horizon and evidence quality. Identify upside and downside. Preserve human/ecological harm even where financial transmission is unproven.

## Required output sections
- `business_model`: substantive analysis linked to claim IDs.
- `issue_inventory`: substantive analysis linked to claim IDs.
- `time_horizons`: substantive analysis linked to claim IDs.
- `financial_vs_impact_materiality`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use IFRS-S1 with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Scenario arithmetic is not a forecast. Financial materiality and impact materiality are separate; no universal ESG premium or automatic ESG score-to-WACC conversion.
