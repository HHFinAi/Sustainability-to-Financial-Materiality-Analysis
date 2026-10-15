#!/usr/bin/env python3
"""Recompute public-data comparisons from a small frozen primary-source extract.

Standard library only. Run with --check to validate saved outputs without writes.
No data-center causal estimate or issuer/project forecast is produced.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = {"US": "United States", "VA": "Virginia", "TX": "Texas", "OH": "Ohio",
         "GA": "Georgia", "OR": "Oregon", "WA": "Washington"}


def cagr(start, end, years):
    if not (start > 0 and end > 0 and years > 0):
        raise ValueError("CAGR requires positive values and elapsed years")
    return (end / start) ** (1 / years) - 1


def calculate(data):
    eia = data["eia"]
    assert eia["years"] == [2015, 2020, 2025]
    assert eia["unit"] == "nominal US cents/kWh"
    assert eia["worksheet"] == "Total Electric Industry"
    rows = eia["observations"]
    indexed = {(r["state"], r["year"]): r for r in rows}
    assert len(indexed) == len(rows) == 21, "Duplicate or missing state/year row"
    assert set(indexed) == {(s, y) for s in NAMES for y in eia["years"]}
    maximum_price_difference = 0
    for r in rows:
        assert r["price_cents_per_kwh"] > 0 and r["total_sales_mwh"] > 0
        # ($000 / MWh) has the same numeric value as $/kWh; x100 gives cents/kWh.
        recomputed = 100 * r["total_revenue_thousand_usd"] / r["total_sales_mwh"]
        difference = abs(recomputed - r["price_cents_per_kwh"])
        maximum_price_difference = max(maximum_price_difference, difference)
        assert difference <= 0.00501, (r["state"], r["year"], difference)
        assert r["source_id"] == eia["source_id"] and "price V" in r["locator"]
    us_growth = cagr(indexed["US", 2020]["price_cents_per_kwh"],
                     indexed["US", 2025]["price_cents_per_kwh"], 5)
    results = []
    for state in NAMES:
        points = {year: indexed[state, year] for year in eia["years"]}
        prices = {year: points[year]["price_cents_per_kwh"] for year in eia["years"]}
        recent = cagr(prices[2020], prices[2025], 5)
        results.append({
            "state": state,
            "name": NAMES[state],
            "prices_cents_per_kwh": prices,
            "price_cagr_2015_2020_pct": 100 * cagr(prices[2015], prices[2020], 5),
            "price_cagr_2020_2025_pct": 100 * recent,
            "price_cagr_2015_2025_pct": 100 * cagr(prices[2015], prices[2025], 10),
            "price_growth_2020_2025_pct": 100 * (prices[2025] / prices[2020] - 1),
            "recent_price_cagr_minus_us_pp": 100 * (recent - us_growth),
            "retail_sales_cagr_2020_2025_pct": 100 * cagr(
                points[2020]["total_sales_mwh"], points[2025]["total_sales_mwh"], 5),
            "price_2025_usd_per_kwh": prices[2025] / 100,
            "price_2025_usd_per_mwh": prices[2025] * 10,
        })
    queue = data["lbnl"]
    assert queue["median_ir_to_cod_years"]["comparison"] == ">"
    assert queue["median_ir_to_cod_years"]["completion_year"] == 2025
    total = queue["active_generation_gw"] + queue["active_storage_gw"]
    status = queue["request_cohort_capacity_outcome_pct"]
    residual = 100 - sum(status[k] for k in ["operational", "withdrawn", "active"])
    return {"as_of": data["as_of"], "classification": "CALCULATION",
            "electricity": results,
            "max_revenue_sales_vs_price_difference_cents_per_kwh": maximum_price_difference,
            "queue": {"sum_of_rounded_active_capacity_gw": total,
                      "storage_share_of_rounded_capacity_pct": 100 * queue["active_storage_gw"] / total,
                      "draft_or_executed_ia_share_of_rounded_capacity_pct":
                          100 * queue["draft_or_executed_ia_not_operational_gw"] / total,
                      "unallocated_outcome_percentage_points": residual}}


def render(data, result, digest):
    lines = ["# Electricity prices and grid queues: independently calculated context", "",
        f"As of **{data['as_of']} (Asia/Almaty)**. Calculations: **COMPLETE**; causal attribution and project underwriting: **NEEDS_DATA**.", "",
        "## Annual electricity comparison", "",
        "FACT: EIA annual total-electric-industry observations, all end-use sectors, one source vintage. "
        "Prices are nominal cents/kWh. CALCULATION: compounded growth uses elapsed years, not the number of observations. "
        "The national row is EIA's revenue/sales-weighted aggregate, not an average of the selected states. [Source register](SOURCES.md).", "",
        "| Geography | 2015 price | 2020 price | 2025 price | 2015–20 CAGR | 2020–25 CAGR | 2015–25 CAGR | Recent CAGR minus US |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in result["electricity"]:
        p = r["prices_cents_per_kwh"]
        lines.append(f"| {r['name']} | {p[2015]:.2f} | {p[2020]:.2f} | {p[2025]:.2f} | "
            f"{r['price_cagr_2015_2020_pct']:.2f}% | {r['price_cagr_2020_2025_pct']:.2f}% | "
            f"{r['price_cagr_2015_2025_pct']:.2f}% | {r['recent_price_cagr_minus_us_pp']:+.2f} pp |")
    rows = {r["state"]: r for r in result["electricity"]}
    lines.extend(["", "CALCULATION / interpretation:", "",
        f"- US prices rose {rows['US']['price_growth_2020_2025_pct']:.2f}% cumulatively in 2020–25. "
        f"Virginia's CAGR was {abs(rows['VA']['recent_price_cagr_minus_us_pp']):.2f} percentage points below the US CAGR; "
        f"Texas was {rows['TX']['recent_price_cagr_minus_us_pp']:.2f} points relative to the US.",
        f"- Washington's recent price CAGR was {rows['WA']['price_cagr_2020_2025_pct']:.2f}%, "
        f"against all-sector retail-sales CAGR of {rows['WA']['retail_sales_cagr_2020_2025_pct']:.2f}%. "
        f"Virginia's sales CAGR was {rows['VA']['retail_sales_cagr_2020_2025_pct']:.2f}%. "
        "These are descriptive comparisons, not a test that data centers caused either result.",
        f"- Texas's 2025 annual all-sector price is {rows['TX']['price_2025_usd_per_kwh']:.4f} USD/kWh "
        f"or {rows['TX']['price_2025_usd_per_mwh']:.2f} USD/MWh. "
        "Multiplying cents/kWh by 10 converts to USD/MWh; treating cents as dollars creates a 100-fold error.", "",
        "METHOD: CAGR = (ending price / starting price)^(1 / elapsed years) − 1. "
        "Reported EIA prices are rounded to two decimals; underlying revenue/sales ratios are used only as a validation check. "
        "All 21 rows reconcile to the reported rounded price within 0.00501 cents/kWh. "
        "No monthly or year-to-date observation is mixed with annual data.", "",
        "INFERENCE: this is a regional screening input, not a data-center procurement curve. "
        "A project needs its utility tariff or contract, demand charges, escalation, cost pass-through, and grid-upgrade allocation. "
        "The purposively selected jurisdictions are not a control group. Different customer mixes, fuel costs, rate cases, "
        "weather, and grid investment can affect observed prices. No inflation adjustment or causal identification is attempted.", "",
        "## Generation queues: scope before arithmetic", "",
        "FACT: Lawrence Berkeley National Laboratory and GridTracker's 2026 publication summarizes end-2025 "
        "transmission generation/storage requests. The public summary reports 1,312 GW generation, approximately 749 GW storage "
        "and roughly 8,200 active projects. [Original publication](https://emp.lbl.gov/publications/queued-2026-edition-characteristics).", "",
        "| Calculation from published rounded inputs | Result |",
        "|---|---:|",
        f"| Generation + storage nameplate capacity | {result['queue']['sum_of_rounded_active_capacity_gw']:,} GW |",
        f"| Storage share | {result['queue']['storage_share_of_rounded_capacity_pct']:.2f}% |",
        f"| 549 GW with draft/executed agreement, not operating, divided by total | {result['queue']['draft_or_executed_ia_share_of_rounded_capacity_pct']:.2f}% |", "",
        "FACT: the reported median from interconnection request to commercial operation exceeds five years "
        "for projects completed in 2025 in regions with available data. It is not the average wait of all applicants. "
        "Load connections, distribution-connected projects and behind-the-meter projects are excluded.", "",
        "FACT: for capacity requested in 2000–2020, the summary reports 13% operating, 75% withdrawn and 10% active "
        "at end-2025. Those rounded categories sum to 98%; the remaining two percentage points are left unallocated. "
        "The 13% figure is a historical capacity-weighted outcome, not a project's probability of success.", "",
        "LIMITATION: these queue inputs are transcribed public summary statistics; the underlying XLSX could not be "
        "downloaded in this run (HTTP 403). The national project-level aggregation and median were not independently recomputed. "
        "Only arithmetic on the extracted aggregates is reproduced. See the download link and access record in SOURCES.md.", "",
        "INFERENCE: requested nameplate GW is neither dependable power nor deliverable capacity for a specific data center. "
        "Do not put the published generation-queue duration into a data-center commissioning schedule. "
        "Use the named site's load study, service agreement, required upgrades, permits, and achievable energization date. "
        "Storage GW also says nothing about energy duration without GWh.", "",
        "## Reproduction and validation", "",
        "```bash", "python examples/ai-infrastructure/public-data/analysis.py",
        "python examples/ai-infrastructure/public-data/analysis.py --check", "```", "",
        "Both commands use Python's standard library and frozen inputs; no network or API key is needed. "
        "The first regenerates this page and results.json; --check verifies their exact contents. "
        "refresh_eia.py separately re-extracts or verifies the EIA workbook without silently changing the frozen input.", "",
        f"Frozen inputs SHA-256: `{digest}`.", "",
        "Confidence: **0.96** for EIA extraction and arithmetic; **0.88** for the scoped LBNL summary transcription. "
        "These confidence judgments do not quantify a project investment outcome. No human review is attested.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raw = (HERE / "inputs.json").read_bytes()
    data = json.loads(raw)
    result = calculate(data)
    assert math.isclose(cagr(100, 121, 2), 0.10, abs_tol=1e-12)
    outputs = {"RESULTS.md": render(data, result, hashlib.sha256(raw).hexdigest()),
               "results.json": json.dumps(result, indent=2) + "\n"}
    for name, content in outputs.items():
        path = HERE / name
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit(f"STALE_OR_MISSING_OUTPUT: {name}; run analysis.py")
        else:
            path.write_text(content)
    print("PASS: 21 annual EIA rows, revenue/sales and units reconciled; scoped queue arithmetic; outputs "
          + ("verified" if args.check else "regenerated"))


if __name__ == "__main__":
    main()
