"""Supplemental metadata checks; not NLP extraction or source-entailment scoring."""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
from typing import Any

FIELDS = ("entity", "metric", "unit", "period", "scope", "classification", "source_id")
HERE = Path(__file__).resolve().parent


def check_claim(claim: dict[str, Any], anchor: dict[str, Any]) -> list[str]:
    """Return mismatching fields against a supplied reference record.

    A correct reference is a precondition, not a conclusion of this function.
    No unit conversion or correction is silently inferred.
    """
    issues = [key for key in FIELDS if not anchor.get(key) or claim.get(key) != anchor[key]]
    a, b = claim.get("value"), anchor.get("value")
    valid = all(isinstance(x, (int, float)) and not isinstance(x, bool)
                and math.isfinite(x) for x in (a, b))
    if not valid or not math.isclose(a, b, rel_tol=0, abs_tol=1e-9):
        issues.append("value")
    return issues


def evaluate(records: list[dict[str, Any]]) -> dict[str, Any]:
    """One unchanged case and five controlled corruptions per reference record."""
    results = []
    for record in records:
        changes = [("unchanged", None, None), ("value", "value", record["value"] + 1),
                   ("unit", "unit", "incorrect-unit"),
                   ("period", "period", "incorrect-period"),
                   ("scope", "scope", "unsupported AI-only attribution"),
                   ("classification", "classification", "UNSUPPORTED_RECLASSIFICATION")]
        for label, key, value in changes:
            claim = deepcopy(record)
            if key is not None:
                claim[key] = value
            detected = check_claim(claim, record)
            expected = [] if key is None else [key]
            results.append({"case": f"{record['id']}:{label}", "expected": expected,
                            "observed": detected, "pass": detected == expected})
    return {"evaluation_type": "engineered metadata contract checks",
            "record_count": len(records), "case_count": len(results),
            "passed": sum(item["pass"] for item in results),
            "independent_human_review": False,
            "llm_accuracy_measured": False, "research_alpha_measured": False,
            "results": results}


if __name__ == "__main__":
    payload = json.loads((HERE / "evidence.json").read_text(encoding="utf-8"))
    result = evaluate(payload["records"])
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] == result["case_count"] else 1)
