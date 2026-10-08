# Executed validation — 0.2.0

Date: **25 September 2026**. Environment: Python **3.13.5**, **Linux**.

**Historical validation record:** the results and omissions below describe that build. This source repository is now public. Check [GitHub Actions](https://github.com/HHFinAi/Sustainability-to-Financial-Materiality-Analysis/actions) for subsequent runs; publication alone does not establish that CI passed or that research is complete.

**120 local unit-test executions passed**, including **13 domain-specific tests**. Shared controls are intentionally rerun in every independently packaged repository; repeated controls do not represent independent financial-model validations. See [complete test log](TEST_LOG.txt) and [machine-readable record](validation.json).

**3 named routes** ran through their complete synthetic workflow, with status `SYNTHETIC_COMPLETE_NOT_APPROVED`. **36 request/artifact schema validations** passed. The bounded official-methodology study stopped at **NEEDS_DATA**. No synthetic or source-study packet was approved as investment research.

Tests cover selected arithmetic, finite numbers, evidence scopes/units/periods, calculation provenance/recomputation, required fields, domain declarations, stale revisions, dependency gating, material issues, review invalidation, local integrity checks, quote/contract gates and no execution authority. Domain test names and fixtures are inspectable in the `tests` folder.

## What was not established by that build
No live issuer, portfolio or market diligence; no model-host integration test; no independent audit or penetration test; no exhaustive legal, PCAF, ICMA, IFRS, SBTi or other standards certification; no scientific or causal-impact validation; no alpha or tradability proof; no actual GitHub remote CI run. Local schema checks used the installed `jsonschema` library; runtime and unit tests need no third-party packages. Future dates/framework updates require revalidation.

The repository check validates local package structure, JSON, local Markdown links, source metadata, route definitions and shared runtime digests. It does not fetch remote URLs or authenticate external sources.

## 2026-10-03 case-study and publication update

Validated locally on Python 3.12.14 (Linux):

- `python -m unittest discover -s tests -v`: **129 tests passed**, including publication metadata and the new case's arithmetic/reproducibility checks.
- `python scripts/check_repository.py`: **PASS**, including shared runtime integrity and local Markdown links.
- `python examples/heidelberg-brevik/model.py --check`: **PASS**; committed model outputs reproduce.
- Original source-study packet and research approval controls are preserved.

This validates software behavior and the stated arithmetic. It does not validate unobserved commercial inputs, legal terms, market quotes, impact attribution or human approval. GitHub Actions results are reported separately for each published commit.

## 2026-10-08 filesystem-host integration

The [host integration record](../examples/host-integration/README.md) archives a session AI’s bounded source review, authored artifacts and actual research-mode CLI run in a fresh local checkout. Current packet identifiers were submitted, a stale revision was rejected, upstream revision invalidated and archived downstream artifacts, and the evidence/gap packet was exported. The final status is `NEEDS_DATA`; no human review or execution authority was asserted.

The replay helper verifies the local CLI handoff without generating research or retrieving sources. This adds a narrow filesystem-host integration check to the historical build records above; it does not establish provider installation, automatic document ingestion or completed investment diligence.
