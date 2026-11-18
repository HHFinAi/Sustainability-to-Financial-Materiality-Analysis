"""Original illustrative contract-to-cash / reverse valuation bridge.

The source JSON is synthetic and cannot be treated as issuer revenue or fair value.
No market prices, climate projections, grants or other third-party inputs are fetched.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

class ModelError(ValueError):
    pass

def n(row, key, limit=None):
    x = row.get(key)
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0:
        raise ModelError(f"{key}: finite nonnegative input required")
    if limit is not None and x > limit:
        raise ModelError(f"{key}: exceeds allowed limit")
    return float(x)

def evaluate(case):
    if case.get("status") != "ILLUSTRATIVE_ONLY":
        raise ModelError("non-synthetic status unsupported; issuer claims require separately verified workflow")
    if case.get("currency") not in {"EUR", "USD", "GBP"}:
        raise ModelError("must declare currency; no FX conversion")
    if not case.get("case_id"):
        raise ModelError("case_id is required")
    x = case["assumptions"]
    years = n(x, "years")
    if years < 1 or years > 40 or int(years) != years:
        raise ModelError("years must be an integer between 1 and 40")
    r = n(x, "discount_rate", 1)
    funded = n(x, "funded_fraction", 1)
    share = n(x, "supplier_award_share", 1)
    convert = n(x, "delivery_conversion", 1)
    gross = n(x, "potential_project_spend_m")
    realized_revenue = gross * funded * share * convert
    ebitda = (realized_revenue * n(x, "contribution_margin", 1)
              - n(x, "annual_fixed_cost_m"))
    ebit = ebitda - n(x, "annual_depreciation_m")
    tax = max(0, ebit) * n(x, "cash_tax_rate", 1)
    annual_fcf = ebitda - tax - n(x, "annual_recurring_capex_m") - n(x, "annual_wc_add_m")
    annuity = sum(1 / (1+r)**t for t in range(1, int(years)+1))
    upfront = n(x, "upfront_capex_m")
    npv = annual_fcf * annuity - upfront
    # A reverse hurdle is meaningful only relative to an explicitly hypothetical market premium.
    premium = n(x, "hypothetical_entry_price_premium_m")
    required_annual_fcf = (premium + upfront) / annuity
    return {"case_id": case["case_id"], "currency": case["currency"], "units": "millions",
            "recognized_revenue_m": round(realized_revenue, 5),
            "annual_incremental_fcf_m": round(annual_fcf, 5),
            "illustrative_incremental_project_npv_m": round(npv, 5),
            "annual_fcf_required_by_hypothetical_premium_m": round(required_annual_fcf, 5),
            "hurdle_surplus_annual_m": round(annual_fcf - required_annual_fcf, 5),
            "status": "NEEDS_DATA", "security_valuation": False}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=Path(__file__).with_name("inputs.json"))
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    doc = json.loads(args.input.read_text())
    if doc.get("schema_version") != "1.0":
        raise ModelError("unsupported schema")
    rows = doc.get("cases", [])
    if len({c["case_id"] for c in rows}) != len(rows) or not rows:
        raise ModelError("empty or duplicate cases")
    results = [evaluate(c) for c in rows]
    if args.check and not all(x["status"]=="NEEDS_DATA" and not x["security_valuation"] for x in results):
        raise ModelError("unsafe research status")
    print(json.dumps({"schema_version": "1.0", "results": results}, indent=2))

if __name__ == "__main__":
    main()
