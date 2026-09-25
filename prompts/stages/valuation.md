# Financial bridge and sensitivity

## Decision context
Which sustainability issues change revenue, margins, cash flows, credit or valuation, by how much and under which assumptions?

## Assignment
Reconcile the unadjusted financial model first. Use explicit annual periods, currency and tax convention. Show terminal-value contribution and distinguish debt repayment capacity from equity residual value. Quantify a bounded sensitivity or return NEEDS_DATA.

## Required output sections
- `baseline_reconciliation`: substantive analysis linked to claim IDs.
- `incremental_cashflows`: substantive analysis linked to claim IDs.
- `equity_credit_bridge`: substantive analysis linked to claim IDs.
- `scenario_sensitivity`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use IFRS-S1 with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Scenario arithmetic is not a forecast. Financial materiality and impact materiality are separate; no universal ESG premium or automatic ESG score-to-WACC conversion.

A domain calculation must pass recomputation. The minimal runnable illustration is `cashflow_bridge`; other needed specialist models must remain explicitly external and independently reviewed.
