# Sources, boundaries and source challenges

**Prepared/retrieved: 4 October 2026.** Public issuer pages below were inspected for the specified passages, not exhaustively audited. Source classification and observation periods are retained in [evidence.json](evidence.json). Linked webpages can change; no third-party PDF or page image is redistributed.

## MS1 — Financial baseline

[Microsoft Annual Report 2025](https://www.microsoft.com/investor/reports/ar25/index.html), **Cash Flows Statements**, years ended June 30, 2025, 2024 and 2023. Amounts are USD million. Cash additions to property and equipment are stored as positive expenditure for subtraction from CFO. These are consolidated historical amounts, not an AI-only investment series and not the latest available financial-period assertion.

## MS2 — Engineering disclosure

Steve Solomon, Microsoft, [Sustainable by design: Next-generation datacenters consume zero water for cooling](https://www.microsoft.com/en-us/microsoft-cloud/blog/2024/12/09/sustainable-by-design-next-generation-datacenters-consume-zero-water-for-cooling/), **9 December 2024**. Relevant headings: “Zero-water evaporation and the quest for ultra-low Water Usage Effectiveness,” “Mitigating energy impacts,” and “Pilot projects and implementation.”

Treat design claims and deployment dates as dated management statements. “Zero water for cooling” is not zero site water or zero supply-chain water. The article defines WUE using consumption but calls the 0.30 baseline withdrawal WUE in its footnote. That wording requires reconciliation before using it as a calibrated site metric. No error correction or updated deployment claim is inferred here.

## MS3 — Responsible-AI disclosure

[Microsoft Responsible AI Transparency Report 2026 — public HTML overview](https://www.microsoft.com/en-us/corporate-responsibility/topics/responsible-ai/reports/transparency-report/). Relevant sections: **Scaling adaptable governance; Meeting the agentic moment; Lessons from deploying AI**. This is a 2026 disclosure observation, separate from FY2025 financial context. Only the inspected HTML overview is used; the complete underlying report and all product controls have not been independently verified.

## Methodological reading — not issuer inputs

| ID | Reading supplied for private review | Relevant location | Use in the original implementation |
|---|---|---|---|
| NUV-AI | Ovidiu Patrascu, Nuveen, *A sustainable investor's guide to AI*; publication date not established from the supplied cover | pp. 3–4 and 7–8 | Power/water trade-offs and transparency, accountability and impact engagement framing |
| UBS-FAQ | UBS, *11 Investor FAQs from our Physical Risk Deep Dive*, 1 October 2026 | pp. 2–3 | Adaptation spending versus economic value; exposure is not financial loss |
| UBS-NV | UBS, *ESG news & views, Vol. 63*, 24 September 2026 | pp. 1–2, 14, 24 | Financial transmission, changed evidence and the distinction between backtested and post-publication results |
| BARC-ADAPT | Barclays, *Adaptation in Action: A Global Universe of Solution Providers*, 21 September 2026 | pp. 2–4, 22–23 | Hazard → solution → deployment evidence; not a copied company universe |
| JPM-LIB | J.P. Morgan, *Global Sustainable Investing Research Library: Must-Reads and Highlights — September 2026*, 2 October 2026 | pp. 1–2, 5, 23 | Organisation by research question, sector and investment use; a catalogue is not the underlying methodology |

These readings motivate questions; they do not validate this model, endorse HHFinAi or substantiate Microsoft-specific figures. Later methodological readings are not represented as information available to a historical trade. Proprietary bank forecasts, source PDFs, charts and company datasets are excluded.

## Two source challenges from the Nuveen guide

**Attribution:** the opening AI-datacentre spending claim is supported by an endnote referring to capital expenditure of five companies during 2020–2024. The supplied guide does not reconcile that total to AI-only spending. The safe result is an attribution question, not a corrected estimate.

**Population and denominator:** page 3 describes a proportion of US datacentres exposed to water stress; endnote 11 instead discusses proportions of two companies' freshwater withdrawals from stressed areas. Facility counts and water volumes are not interchangeable. Resolve with the underlying evidence before calibration.

The [claim checks](claim_checks.py) demonstrate selected metadata controls inspired by such problems. They do not automatically read those reports or establish that arbitrary prose is supported by a citation.

## MS4 — Arizona design history (extension)

Microsoft Azure, [Expanding cloud services: Microsoft launches its sustainable datacenter region in Arizona](https://azure.microsoft.com/en-us/blog/expanding-cloud-services-microsoft-launches-its-sustainable-datacenter-region-in-arizona/), **15 June 2021**, reviewed 8 October 2026. Locators: “West US 3 region delivers highly resilient, secure cloud services”; “Sustainable datacenter design, operations”; “Beyond the datacenter.” The cooling description and regional availability-zone design are dated issuer statements. Neither quantifies historical outages, realized contribution or benefits caused by a later redesign.

## MS5 — Arizona design-specific disclosure (extension)

Microsoft Local, [Microsoft datacenters in Arizona](https://local.microsoft.com/wp-content/uploads/2024/04/Microsoft-datacenters-in-Arizona.pdf), **internally dated December 2024**, reviewed 8 October 2026. Locator: **PDF page 5, WATER bullets**; page image was also inspected. The document distinguishes existing direct evaporative cooling from planned air-cooled/direct-to-chip designs. The URL folder is not a reliable publication date. It does not provide a matched campus's capex, tariffs, measured new-design PUE or commercial economics. Only those cooling bullets are used; commitments elsewhere are not assumed achieved.

## MS6 — Basin context (extension)

Arizona Department of Water Resources, [Phoenix AMA Model FAQs](https://www.azwater.gov/sites/default/files/2023-11/PHX_Model_FAQs_new.pdf), **2023 model release**, reviewed 8 October 2026. Locator: **page 1, “What are the results of the Phoenix AMA model run?” and “Is growth going to slow…”**. This is a regional long-horizon groundwater projection and water-supply-program explanation, not the latest hydrology estimate, a Microsoft service contract, a site-specific restriction or an annual outage-frequency estimate. No permit or tariff conclusion is drawn. Later regional model versions require separate review for live underwriting.

## Extension review record

The additional passages were inspected by the AI assistant, including the Arizona PDF page image. No independent human attestation or site-economic verification is recorded. These sources establish design/basin context only. The six unresolved input gates are retained in [inputs.json](inputs.json) and [results.json](results.json); scenario completion cannot close them. Original sources, dates, records and methodological caveats above remain intact.

## MS4 — Arizona design history (extension)

Microsoft Azure, [Expanding cloud services: Microsoft launches its sustainable datacenter region in Arizona](https://azure.microsoft.com/en-us/blog/expanding-cloud-services-microsoft-launches-its-sustainable-datacenter-region-in-arizona/), **15 June 2021**, reviewed 8 October 2026. Locators: “West US 3 region delivers highly resilient, secure cloud services”; “Sustainable datacenter design, operations”; “Beyond the datacenter.” The cooling description and regional availability-zone design are dated issuer statements. Neither quantifies historical outages, realized contribution or benefits caused by a later redesign.

## MS5 — Arizona design-specific disclosure (extension)

Microsoft Local, [Microsoft datacenters in Arizona](https://local.microsoft.com/wp-content/uploads/2024/04/Microsoft-datacenters-in-Arizona.pdf), **internally dated December 2024**, reviewed 8 October 2026. Locator: **PDF page 5, WATER bullets**; page image was also inspected. The document distinguishes existing direct evaporative cooling from planned air-cooled/direct-to-chip designs. The URL folder is not a reliable publication date. It does not provide a matched campus's capex, tariffs, measured new-design PUE or commercial economics. Only those cooling bullets are used; commitments elsewhere are not assumed achieved.

## MS6 — Basin context (extension)

Arizona Department of Water Resources, [Phoenix AMA Model FAQs](https://www.azwater.gov/sites/default/files/2023-11/PHX_Model_FAQs_new.pdf), **2023 model release**, reviewed 8 October 2026. Locator: **page 1, “What are the results of the Phoenix AMA model run?” and “Is growth going to slow…”**. This is a regional long-horizon groundwater projection and water-supply-program explanation, not the latest hydrology estimate, a Microsoft service contract, a site-specific restriction or an annual outage-frequency estimate. No permit or tariff conclusion is drawn. Later regional model versions require separate review for live underwriting.

## Extension review record

The additional passages were inspected by the AI assistant, including the Arizona PDF page image. No independent human attestation or site-economic verification is recorded. These sources establish design/basin context only. The six unresolved input gates are retained in [inputs.json](inputs.json) and [results.json](results.json); scenario completion cannot close them. Original sources, dates, records and methodological caveats above remain intact.
