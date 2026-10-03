# Sustainability to Financial Materiality

**Investment research by HHFinAi: company economics, capital allocation and valuation, supported by reproducible calculations.**

Which sustainability issues change cash flow, by how much, and what evidence would change the investment judgment?

## Start with the research

### Heidelberg Materials — what Brevik CCS must earn to matter

**Research assessment: WATCH.** The historical case tests whether an operating carbon-capture project supports incremental value, rather than assuming a group-wide green premium. The central sensitivity gives **€56.08m** of discounted 2026–2030 incremental cash flow; it is not a company forecast or full project NPV. The five-year premium break-even is **€13.08/t cement** under the stated assumptions.

**Status:** retrospective real-issuer research; evidence cutoff **25 February 2026**. This is mitigation/transition economics, not physical adaptation. Material evidence gates and the limits of the cash-flow window remain explicit.

[Read the investment memo](examples/WORKED_EXAMPLE.md) · [Inspect results](examples/heidelberg-brevik/RESULTS.md) · [Run the model](examples/heidelberg-brevik/model.py)

### Microsoft — what must water-resilient AI infrastructure earn?

**Research finding: water savings are not a return calculation.** An explicitly illustrative cooling-design model requires **$3.16m/year** of additional pre-tax operating benefit to break even under its reference assumptions. That is a hurdle to investigate, not a Microsoft forecast or site valuation.

**Status:** real-issuer disclosure context plus an illustrative incremental model, prepared **4 October 2026**. Historical FY2023–FY2025 financial context is kept separate from the 2026 stewardship disclosure. No current share-price recommendation is made.

[Read the research case](examples/microsoft-ai/README.md) · [Sensitivity table](examples/microsoft-ai/RESULTS.md) · [Evidence and source challenges](examples/microsoft-ai/SOURCES.md) · [Evaluation record](examples/microsoft-ai/EVALUATION.md)

## Research contribution and accountability

The work makes counterfactuals, financial transmission, break-even conditions, contrary cases and unresolved evidence visible. Sustainability credentials do not substitute for valuation or underlying economics. Original HHFinAi implementations are distinguished from third-party methodology and issuer disclosures.

The Microsoft release was prepared with AI assistance under Ed's portfolio-development brief. Mathematical checks are executable; independent human validation and workflow research approval are not represented as complete. Each case identifies its own scope. [Portfolio and research standards](https://github.com/HHFinAi/HHFinAi)

## Reproduce the research examples

From the repository root, using Python 3.10 or later:

```bash
python examples/heidelberg-brevik/model.py --check
python examples/microsoft-ai/model.py --check
python examples/microsoft-ai/claim_checks.py
python -m unittest discover -s tests -v
python scripts/check_repository.py
```

The Microsoft metadata exercise is **48 engineered contract checks**, not measured LLM extraction accuracy, investment alpha or productivity improvement. Its [evaluation record](examples/microsoft-ai/EVALUATION.md) separates executed checks from the proposed empirical benchmark.

## Workflow infrastructure

**Engine v0.2.0 · 9 research stages · 3 named routes · Human review · No autonomous trading**

[Workflow](WORKFLOW.md) · [Host instructions](AGENTS.md) · [Prompts and skills](PROMPTS.md) · [Data contract](docs/DATA_CONTRACT.md) · [Evidence and audit](docs/AUDIT.md) · [Validation](docs/VALIDATION.md)

The engine validates and records structured research. A human or separately authorized AI host retrieves evidence and performs substantive analysis; the engine does not fetch documents or run an LLM.

```bash
python -m sf_agent routes
python -m sf_agent demo --out runs/demo-01
python -m sf_agent report --run runs/demo-01
python -m sf_agent export --run runs/demo-01 --out exports/demo-01
python -m sf_agent calc --operation cashflow_bridge --arguments examples/calculation-arguments.json
```

Use a new output directory each time. The demo uses fictional, pre-authored fixtures and does not perform live investment research. [Original synthetic cash-flow example](examples/SYNTHETIC_CASHFLOW_EXAMPLE.md).

For an actual research run, replace every placeholder in `examples/research-request-template.json` and keep confidential material outside the public repository:

```bash
python -m sf_agent init --request your-request.json --out runs/research-01
python -m sf_agent next --run runs/research-01
python -m sf_agent submit --run runs/research-01 --stage mandate --artifact your-artifact.json --revision 0
python -m sf_agent status --run runs/research-01
```

Continue with the current revision. Material evidence gaps require `NEEDS_DATA` or an explicit blocking issue. The [methodology-only source study](examples/reports/source-study-packet.md) remains `NEEDS_DATA`; standalone research examples do not override it. [Synthetic workflow packet](examples/reports/synthetic-packet.md).

## Controls and limitations

Financial and impact materiality are separate. There is no universal ESG premium or automatic score-to-WACC conversion. Scenario arithmetic is not a forecast. Evidence attestations are not independently authenticated, and local audit records are not tamper-proof. [Claim-to-control map](docs/INSTITUTIONAL_QUALITY.md).

There is no embedded AI model, live market feed, scheduler, broker connection, external messaging or automatic voting. Software tests do not establish source truth, commercial viability, investment performance, legal compliance or production security. Third-party methods and sources retain their rights; no endorsement is implied. [Sources](references/SOURCES.md) · [Notices](NOTICE.md) · [FAQ](docs/FAQ.md).

## Existing users and repository maintenance

The workflow core, original cases, source studies and research-approval controls are preserved. The Microsoft case is a supplemental example, not a silent upgrade of the vendored engine. Fetch and pull remote changes before editing an existing clone; preserve `.git` and review local changes.

[GitHub Desktop guide](START_HERE_GITHUB_DESKTOP.md) · [Repository metadata](repository-metadata.json) · [Discoverability](docs/GEO_SEO.md)
