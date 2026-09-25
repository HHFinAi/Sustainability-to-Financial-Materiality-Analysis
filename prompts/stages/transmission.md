# Causal financial transmission

## Decision context
Which sustainability issues change revenue, margins, cash flows, credit or valuation, by how much and under which assumptions?

## Assignment
For each issue connect trigger -> operational exposure -> volume/price/cost/capex/working capital -> cash flow. State adaptation, pass-through, contractual protection and timing. Separate fact, causal inference and scenario assumption. Do not count the same shock in cash flow and an unexplained discount-rate overlay.

## Required output sections
- `causal_chain`: substantive analysis linked to claim IDs.
- `revenue_margin_capex`: substantive analysis linked to claim IDs.
- `credit_channels`: substantive analysis linked to claim IDs.
- `double_counting_register`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use IFRS-S1 with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Scenario arithmetic is not a forecast. Financial materiality and impact materiality are separate; no universal ESG premium or automatic ESG score-to-WACC conversion.
