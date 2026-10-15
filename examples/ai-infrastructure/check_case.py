"""Read-only provenance/status joins and published-output checks for this case."""
import json
import math
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def check():
    sources = json.loads((HERE / "evidence/sources.json").read_text())["sources"]
    ids = {s["id"] for s in sources}
    require(len(ids) == len(sources), "Duplicate source ID")
    for source in sources:
        require(source["review_status"] == "assistant-reviewed", "Do not imply human review")
        require(source["url"].startswith("https://") and source["locator"], "Source URL/locator required")
    projects = json.loads((HERE / "evidence/projects.json").read_text())
    require(projects["record_count"] == len(projects["projects"]), "Record count mismatch")
    require(len({p["id"] for p in projects["projects"]}) == len(projects["projects"]), "Duplicate project ID")
    for p in projects["projects"]:
        require(set(p["source_ids"]).issubset(ids), "Unknown project source")
        require(p["verified_capacity_mw"] is None and p["permit_verified"] is False, "New permit/capacity evidence requires review of this frozen case")
        require(p["company_scenario_ready"] is False and p["evidence_gap"], "Unresolved economic boundary required")
    policies = json.loads((HERE / "evidence/policies.json").read_text())["policies"]
    for policy in policies:
        require(set(policy["source_ids"]).issubset(ids), "Unknown policy source")
        require(policy["named_project_impact_verified"] is False, "Policy/project applicability unverified")
    issues = json.loads((HERE / "open_issues.json").read_text())
    require(issues["issuer_underwriting"] == "NEEDS_DATA", "Uncalibrated model cannot be decision-ready")
    require(not issues["human_review_recorded"] and not issues["workflow_research_approval_recorded"], "No approval attestation recorded")
    require(all(x["status"] == "OPEN" for x in issues["issues"]), "Issue closure requires new evidence/review")
    result = json.loads((HERE / "results.json").read_text())
    require(result["issuer_underwriting"] == "NEEDS_DATA", "Scenario output cannot close evidence gaps")
    for route in ("reference_grid", "reference_gas"):
        r = result[route]
        require(len(r["cash_flows"]) == r["horizon_months"] + 1, "Missing monthly cash flow")
        require(math.isclose(sum(x["pv_m"] for x in r["cash_flows"]), r["npv_m"], abs_tol=1e-7), "Cash flows do not tie to NPV")
    # Check the manually curated memo's load-bearing model numbers too.
    memo = (HERE / "README.md").read_text()
    for amount in (result["reference_grid"]["npv_m"], result["reference_gas"]["npv_m"]):
        require(f"${amount:.2f}m" in memo, "Memo headline differs from model")
    for script in (HERE / "model.py", HERE / "issuer_scale.py", HERE / "public-data/analysis.py"):
        subprocess.run([sys.executable, str(script), "--check"], check=True)
    return {"status": "PASS", "source_records": len(sources), "project_phase_records": len(projects["projects"]),
            "policy_instruments": len(policies), "open_material_issues": len(issues["issues"]),
            "scope": "Arithmetic, source-ID joins and explicit status boundaries; no source-truth, legal or human-approval certification"}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
