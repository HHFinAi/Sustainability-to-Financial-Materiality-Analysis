# Investment committee and accountable review

## Decision context
Which sustainability issues change revenue, margins, cash flows, credit or valuation, by how much and under which assumptions?

## Assignment
Integrate findings without changing their qualification. Separate facts, inferences, assumptions and calculations; cite evidence IDs and dates. Preserve unknown conclusions. Complete the domain-assessment declarations, register unresolved material issues, and submit for human research review. Do not certify legal compliance or investment performance.

## Required output sections
- `investment_question_and_answer`: substantive analysis linked to claim IDs.
- `financial_vs_sustainability_conclusions`: substantive analysis linked to claim IDs.
- `evidence_and_calculations`: substantive analysis linked to claim IDs.
- `decision_conditions_and_limits`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use the mandate and registered primary evidence with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Scenario arithmetic is not a forecast. Financial materiality and impact materiality are separate; no universal ESG premium or automatic ESG score-to-WACC conversion.

Required typed domain-assessment fields (declarations, not automated truth verification):
```json
{
  "financial_materiality_basis": [
    "cash_flow",
    "credit",
    "both",
    "not_established"
  ],
  "impact_materiality_separate": [
    true
  ],
  "double_counting_review": [
    "reviewed",
    "unresolved"
  ],
  "scenario_not_forecast": [
    true
  ]
}
```
