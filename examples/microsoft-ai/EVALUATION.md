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

The 4 October model and engineered metadata checks did not measure an LLM-versus-baseline comparison. A separate [8 October issuer claim evaluation](../../evaluation/claim-accuracy/README.md) archives an observed comparison between two fresh assistant sessions with different prompts on 32 new questions from eight primary issuer documents. Read its scored records, source hashes, blind assistant label review and limitations separately; it does not turn 48/48 metadata checks into LLM accuracy.

Independent human accuracy assessment, production latency, cost saving, human research-time saving, investment alpha, empirical avoided loss, and regulatory compliance remain unmeasured. The project model is intentionally illustrative. Mathematical correctness does not make its assumptions true.

## Empirical evaluation protocol and observed execution

The [issuer evaluation](../../evaluation/claim-accuracy/README.md) follows the separation principle with a frozen candidate corpus, a short-prompt assistant baseline, an explicit-scope prompt, archived raw responses and a deterministic scorer. A third fresh assistant labels the candidates without seeing author labels or predictions; this is not independent human adjudication. Eight unresolved fiscal/calendar period-token differences are reported with [both frozen reference scores](../../evaluation/claim-accuracy/REFERENCE_SENSITIVITY.md), rather than a consensus key. It evaluates numeric extraction and entity/unit/period/scope annotation on supplied fragments, not end-to-end retrieval or the workflow engine. Model revision and human review time were unavailable and are not inferred.

For the next stronger evaluation, select new unseen-development documents, use independent human experts, retain natural extraction difficulties and run repeated matched sessions or models. Report label disagreements, abstentions and failure cases before inferring an accuracy or time-saving benefit.

[Model](model.py) · [Metadata checker](claim_checks.py) · [Evidence and assumptions](evidence.json) · [Research memo](README.md)
