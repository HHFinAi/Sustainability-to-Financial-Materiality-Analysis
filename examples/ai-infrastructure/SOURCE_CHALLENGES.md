# Source challenges that change the investment input

Original HHFinAi review, 16 October 2026. This note starts from the primary records and identifies common inference errors. It does not reproduce or annotate a broker report.

| Primary evidence | Tempting but unsupported inference | Original check and investment consequence |
|---|---|---|
| EIA state all-sector annual electricity prices | A state average is a data-center tariff; cents/kWh are dollars/kWh | Preserve the sector, annual period and unit. Texas 2025 converts from 9.97 cents/kWh to $99.70/MWh. A named site's bill also depends on demand charges and contract terms. |
| EIA historical workbook | A stable URL always contains the latest observations | The legacy file downloaded here ends in 2020; the current HS861 workbook includes 2025. Register source bytes, release date and selected cells. |
| EIA state price and sales growth | Faster demand or prices prove an AI-driven causal effect | These are selected state aggregates. Fuel, rate-base changes, weather and customer mix are uncontrolled. Do not allocate the price change to AI demand. |
| LBNL transmission generation/storage queue | Queued GW is new data-center load, or storage GW is firm supply | Preserve generation versus load and MW versus MWh boundaries. The data do not supply a named campus's service date. |
| LBNL completed-project timing | A completed-cohort median is the expected wait for all applicants | Pending and withdrawn projects are different populations. No project probability or data-center load delay is inferred. |
| Microsoft's dated Mount Pleasant announcement | Both phases are operational | First-facility status and second-facility completion target are separate fields. |
| Microsoft's Caledonia page | A withdrawn site is proof of a regulator rejection or a quantified loss | Use the dated company decision; capital committed, reasons and recoverability need additional evidence. |
| Microsoft's Atlanta architecture | Every AI datacenter is single-storey or requires captive generation | The described design is two-storey and uses a specified grid-resilience approach. Check the actual workload and facility boundary. |
| Microsoft FY2026 accounting policy | Book depreciation proves a GPU's economic life or its resale value | Keep accounting, tax and economic-life assumptions separate; test replacement cash spending explicitly. |
| New York EO62 and Texas's signed letter | All moratoriums share a fixed duration and blanket scope | Extract the operative agency, application stage, size definition, exclusions and release condition. Match the actual permit file before changing a project model. |
| NIST OT security guidance | General cyber exposure yields a company-specific annual outage probability | Use it to define governance and recovery questions. Model conditional severity only until incidence and controls can be calibrated. |

Primary-source links and locators: [EIA and LBNL](public-data/SOURCES.md); [issuer, policy and NIST register](evidence/sources.json); [operative policy fields](evidence/policies.json).

## What was actually reproduced

EIA: 21 annual state/year observations, extracted from a downloaded source workbook with exact cell locators and a source-file SHA-256. Revenue/sales independently checks the rounded price. Growth and unit conversions are computed by [analysis.py](public-data/analysis.py); [refresh_eia.py](public-data/refresh_eia.py) re-extracts the underlying XLSX without third-party packages.

LBNL: arithmetic on a small official-summary extract. The raw workbook returned HTTP 403. Neither the national project aggregation nor the duration distribution is represented as independently recomputed. Its unavailable file hash remains null.

The project/policy ledger records assistant-reviewed passages and unknown permit/capacity fields. An identifier join or passing software check does not establish legal applicability, source truth or independent human review.

## Next evaluation, with a preserved null result

The existing [32-item claim-accuracy comparison](../../evaluation/claim-accuracy/README.md) remains unchanged, including its finding of no observed advantage from the structured prompt. This case does not supply new LLM accuracy, human productivity or alpha statistics.

A future evaluation should freeze unseen primary documents, expected fields, allowed abstentions and independently adjudicated labels before testing. Candidate failure types are stale dates, cents/dollars, load/generation, project/phase joins, proposal/enacted instrument and target/actual operation. Measure whether a wrong extraction changes a commissioning input, cash-flow sign or return hurdle. Any new run must report its actual outputs and review time; this proposal is not a completed experiment.
