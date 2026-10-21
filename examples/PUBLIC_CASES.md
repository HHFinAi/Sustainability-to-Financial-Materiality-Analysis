# Public-evidence research, 21 October 2026

These standalone cases use public primary evidence and original calculations. The background research reading guided question design, not conclusions or quantitative inputs. No proprietary report, chart or dataset is distributed. Models are offline and use only Python's standard library; they do not bypass the workflow engine's review gates.

| Case | Finding | Remaining material evidence |
|---|---|---|
| [Battery storage](battery-storage/README.md) | Public costs become a dispatch/resilience hurdle; reserve and maintenance have economic costs. | Local quote, hourly dispatch, contract and outage economics. |
| [Climate and staples](climate-staples/README.md) | Lagged transmission matters; different COGS classifications distort apparent exposure. | Commodity/FX weights, hedge terms, inventory and pricing response. |
| [Water and waste](water-waste/README.md) | Order concentration, segment growth, pricing and volume are different signals. | Order conversion, comparable capital returns and valuation expectations. |

Each folder contains a memo, `sources.json`, `inputs.json`, a runnable `model.py`, generated `results.json` / `RESULTS.md`, and an original chart. Source review is an assistant's recorded check, not independently authenticated human adjudication. Missing raw-document hashes are explicit; manual bounded extracts are reproducible from cited documents but are not an automated ingestion pipeline.

Reproduce models with `python examples/<case>/model.py --check`. The unit suite checks result reproduction and selected economic invariants. `--write` is a deliberate regeneration action. Source schema and unit tests cannot establish source truth or investment merit.

With Matplotlib installed, regenerate all three figures with `python examples/render_public_case_charts.py`. Charts use archived numeric results and deterministic SVG settings. Matplotlib is optional and is not needed for model checks or ordinary CI. For local image inspection, append `--preview-dir /tmp/public-case-previews`; previews are not research data.

The [prospective register](../evaluation/prospective-research/README.md) adds future operating-hypothesis evaluation beside the existing [source-extraction comparison](../evaluation/claim-accuracy/README.md). Neither is an investment-performance backtest.
