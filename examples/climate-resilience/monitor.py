"""Primary-source Q3 2026 operating indicators; NOT climate attribution or valuation."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

class EvidenceError(ValueError):
    pass

def positive(x, label):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or x <= 0:
        raise EvidenceError(f"{label} must be a positive recorded numeric observation")
    return float(x)

def calculate(row):
    if row["ticker"] not in {"TT", "GEV", "HEI.DE"}:
        raise EvidenceError("new issuers require independently verified source registration")
    if not row.get("source_url") or not row.get("source_date"):
        raise EvidenceError("primary source locator missing")
    if row.get("quantified_climate_attribution") is not None or row["adaptation_revenue_verified"]:
        raise EvidenceError("no source-backed climate revenue attribution")
    m = row["metrics"]
    revenue, prior = positive(m["revenue_m"], "revenue_m"), positive(m["revenue_prior_m"], "revenue_prior_m")
    ans = {"ticker":row["ticker"], "scope":row["scope"], "currency":row["currency"],
           "reported_revenue_growth_pct":round(100*(revenue/prior-1), 2),
           "climate_attribution":"NEEDS_DATA", "investment_valuation":"NEEDS_DATA",
           "do_not_cross_rank":True}
    if "orders_m" in m:
        orders = positive(m["orders_m"], "orders_m")
        ans["reported_book_to_bill"] = round(orders/revenue, 3)
        ans["reported_orders_yoy_pct"] = round(100*(orders/positive(m["orders_prior_m"],"orders_prior_m")-1), 2)
    if row["ticker"] == "GEV":
        ans["electrification_segment_ebitda_margin_pct"] = round(100*positive(m["segment_ebitda_m"],"segment_ebitda_m")/revenue, 2)
        ans["organic_orders_yoy_pct_as_disclosed"] = m["organic_orders_yoy_pct"]
    if row["ticker"] == "HEI.DE":
        ans["rco_margin_pct"] = round(100*positive(m["rco_m"],"rco_m")/revenue, 2)
        ans["rco_yoy_pct"] = round(100*(m["rco_m"]/positive(m["rco_prior_m"],"rco_prior_m")-1), 2)
    return ans

def run():
    doc=json.loads((HERE/"issuer-observations.json").read_text(encoding="utf-8"))
    if doc.get("cutoff")!="2026-11-18":
        raise EvidenceError("unexpected source vintage")
    return {"cutoff":doc["cutoff"],"results":[calculate(row) for row in doc["observations"]]}

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
