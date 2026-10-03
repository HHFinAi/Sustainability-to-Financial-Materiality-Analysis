# Evaluation record — scope matters

**Local execution: 4 October 2026.** The new case was executed in the authoring environment using the Python standard library. This record covers the case-specific commands below, not an execution audit of all existing repositories.

| Executed check | Observed result | What it establishes |
|---|---|---|
| `python examples/microsoft-ai/model.py --check` | PASS | The committed result table reproduces from the supplied inputs |
| `python -m unittest discover -s tests -p test_microsoft_ai_case.py -v` | 13 tests passed | Selected arithmetic, unit conversion, validation, tax/timing, break-even and document-regression behavior |
| `python examples/microsoft-ai/claim_checks.py` | 48 designed cases passed | Exact metadata matching against eight supplied reference records |

The metadata exercise contains eight unchanged records and forty deliberately corrupted variants: changed value, unit, period, scope or classification. Six reference records come from historical consolidated financial statements and two are labelled analyst assumptions. The complete per-case result is printed as JSON, making failures inspectable.

**48/48 is not LLM extraction accuracy.** This is a deterministic contract test with deliberately constructed cases. The reference records were selected and inspected with AI assistance, not independently labelled by another reviewer. It cannot prove source truth, textual entailment, exhaustive coverage, unbiased selection or real-world predictive performance. The checker is a supplemental example, not a replacement for the workflow engine's validation.

## Failures this release is designed to expose

A correct amount attached to the wrong year; group capex relabelled AI-only; a million/billion mismatch; analyst assumptions relabelled as reported facts; nonfinite or boolean inputs; capital spending deducted twice; a break-even formula that fails to produce zero NPV; and a memo table that no longer matches its inputs.

## Not measured

No LLM-versus-baseline comparison, independent human accuracy assessment, production latency, cost saving, research-time saving, investment alpha, empirical avoided loss, or regulatory compliance is measured. The project model is intentionally illustrative. Mathematical correctness does not make its assumptions true.

## Next empirical evaluation — protocol, not a result

Use 30–50 newly selected public issuer passages, preserve publication dates, and have a second reviewer label amount, unit, period, entity, scope and claim type without seeing the model's answers. Compare a simple extraction baseline with the structured workflow on the same held-out passages. Record disagreements, abstention, review time and failure cases. Keep this dataset separate from the engineered tests above and publish results only after execution.

[Model](model.py) · [Metadata checker](claim_checks.py) · [Evidence and assumptions](evidence.json) · [Research memo](README.md)
