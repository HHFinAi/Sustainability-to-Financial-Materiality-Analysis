# Validation scope and review record

Prepared 16 October 2026. Source collection, writing, programming and review used AI assistance under Ed's brief. No independent human source validation, issuer engagement or workflow research approval is represented.

## Executable checks

The case includes tests for facility-versus-IT energy, capital/working-capital timing, a fixed common horizon, holding costs, hardware replacement, economic/tax-life separation, retired basis, cash-tax floors and disposal gains, revenue breakpoints, gas-cost components, recoverable workload, incident timing, terminal recovery and cancellation before hardware commitment. A replacement-boundary test documents a nonmonotonic horizon effect rather than hiding it.

`model.py --check` reproduces monthly cash flows and all displayed sensitivities. `issuer_scale.py --check` reproduces the dated-denominator scale table. `public-data/analysis.py --check` reproduces growth rates and summary arithmetic; `refresh_eia.py` independently re-extracts source XLSX cells. `check_case.py` verifies source/project/policy joins, explicit unknowns, NPV tie-outs and underwriting-status boundaries. Repository validation also checks local links and the release inventory.

```bash
python examples/ai-infrastructure/check_case.py
python -m unittest discover -s tests -p test_ai_infrastructure.py -v
python scripts/validate_repository.py --out runs/ai-infrastructure-validation
```

The final command requires a new output directory; it archives actual logs. A successful program exit is a software result, not investment approval.

## Executed local release checks

The 16 October release preparation passed on Python 3.12.14: all **206 repository unit tests**, including **18 new AI infrastructure tests**; repository contracts and local links; release inventory; and all six registered example/evaluation checks. The new case check reproduced the financial outputs, issuer-scale illustration and public-data results, with 10 primary source records, six project/phase records, two policy instruments and eight open material issues. The EIA extract contains 21 annual observations. These counts describe the executed scope, not a source-accuracy rate.

## Review changes incorporated

A separate AI code-review pass identified coupled economic/tax hardware lives, misleading pretax wording in the scale boundary, and sensitivity to a fixed terminal horizon. The model now separates tax and economic lives, identifies after-tax unlevered cash flows, specifies a real discount rate, and displays residual-value and terminal-boundary challenges. That review is an AI check, not independent human adjudication.

## What is not established

- Company-specific project return, market mispricing, optimal capital allocation or portfolio suitability.
- Causal attribution of state electricity inflation to data-center demand.
- LBNL project-level aggregation or duration reconstruction: source workbook access returned HTTP 403.
- Legal applicability or current permit compliance for a named site.
- Actual resilience/control effectiveness, failure frequency or insured recoveries.
- Human time saved, improved LLM accuracy or investment alpha.

The [open issue register](open_issues.json) keeps these dependencies visible. New source evidence and an accountable human review are required before upgrading issuer underwriting from NEEDS_DATA.
