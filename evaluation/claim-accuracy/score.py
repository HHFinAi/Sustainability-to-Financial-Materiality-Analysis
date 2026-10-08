"""Score archived issuer-claim sessions. No network calls or model inference."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECISIONS = ("supported", "contradicted", "insufficient", "abstain")
FIELDS = ("value", "unit", "entity_id", "period", "scope")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read(path):
    def invalid_constant(value):
        raise ValueError(f"Nonfinite JSON constant: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=invalid_constant)


def rate(numerator, denominator):
    return numerator / denominator if denominator else None


def validate_response(response, corpus, corpus_sha):
    if response.get("schema_version") != 1 or response.get("dataset_id") != corpus["dataset_id"]:
        raise ValueError("Wrong response schema or dataset")
    if response.get("candidate_file_sha256") != corpus_sha:
        raise ValueError("Response refers to a different candidate corpus")
    if response.get("answer_key_access") is not False:
        raise ValueError("Run does not attest absence of answer-key access")
    items = response.get("items")
    if not isinstance(items, list):
        raise ValueError("Response items must be a list")
    expected_ids = {item["id"] for item in corpus["items"]}
    seen = set()
    for item in items:
        item_id = item.get("id")
        if item_id not in expected_ids or item_id in seen:
            raise ValueError(f"Unknown or duplicate item ID: {item_id}")
        seen.add(item_id)
        if item.get("decision") not in DECISIONS:
            raise ValueError(f"Invalid decision: {item_id}")
        if "record" not in item:
            raise ValueError(f"Missing extraction record: {item_id}")
        record = item["record"]
        if record is not None:
            if not isinstance(record, dict) or set(record) != set(FIELDS):
                raise ValueError(f"Extraction record must have exactly five fields: {item_id}")
            value = record["value"]
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
                raise ValueError(f"Nonfinite/non-numeric extraction: {item_id}")
            for field in FIELDS[1:]:
                if not isinstance(record[field], str) or not record[field]:
                    raise ValueError(f"Invalid {field}: {item_id}")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise ValueError(f"Missing archived reason: {item_id}")
    if seen != expected_ids:
        raise ValueError(f"Missing item IDs: {sorted(expected_ids - seen)}")
    return {item["id"]: item for item in items}


def evaluate(corpus, key, response, corpus_sha, item_ids=None):
    """Return descriptive metrics; abstention never increases overall accuracy."""
    predictions = validate_response(response, corpus, corpus_sha)
    labels = {item["id"]: item for item in key["items"]}
    expected_ids = {item["id"] for item in corpus["items"]}
    if len(labels) != len(key["items"]) or set(labels) != expected_ids:
        raise ValueError("Answer-key IDs differ from candidate IDs")
    selected_ids = expected_ids if item_ids is None else set(item_ids)
    if not selected_ids.issubset(expected_ids):
        raise ValueError("Evaluation subset contains unknown candidate IDs")
    counts = Counter()
    fields = Counter()
    confusion = {label: {prediction: 0 for prediction in DECISIONS} for label in DECISIONS[:-1]}
    details = []
    groups = {}
    for candidate in corpus["items"]:
        item_id = candidate["id"]
        if item_id not in selected_ids:
            continue
        gold, pred = labels[item_id], predictions[item_id]
        truth, decision = gold["decision"], pred["decision"]
        if truth not in DECISIONS[:-1]:
            raise ValueError(f"Invalid gold decision: {item_id}")
        confusion[truth][decision] += 1
        decision_ok = truth == decision
        counts["correct_decisions"] += decision_ok
        counts["abstentions"] += decision == "abstain"
        counts["accepted"] += decision == "supported"
        counts["not_supported_gold"] += truth != "supported"
        counts["unsupported_accepted"] += decision == "supported" and truth != "supported"
        expected_record, actual_record = gold["record"], pred["record"]
        mismatches = []
        if expected_record is None:
            counts["unanswerable_requests"] += 1
            record_ok = actual_record is None
            counts["unsupported_numeric_records"] += not record_ok
            counts["correct_null_records"] += record_ok
            if not record_ok:
                mismatches.append("record_should_be_null")
        else:
            counts["answerable_requests"] += 1
            for field in FIELDS:
                expected = expected_record[field]
                actual = actual_record[field] if actual_record is not None else None
                ok = (actual is not None and math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-8)) if field == "value" else actual == expected
                fields[field] += ok
                if not ok:
                    mismatches.append(field)
            record_ok = not mismatches
            counts["exact_answerable_records"] += record_ok
        complete_ok = decision_ok and record_ok
        counts["complete_correct"] += complete_ok
        group = groups.setdefault(candidate["source_id"], {"items": 0, "decision_correct": 0, "complete_correct": 0})
        group["items"] += 1
        group["decision_correct"] += decision_ok
        group["complete_correct"] += complete_ok
        details.append({"id": item_id, "gold_decision": truth, "predicted_decision": decision,
                        "decision_correct": decision_ok, "record_correct": record_ok,
                        "mismatched_fields": mismatches})
    n = len(selected_ids)
    class_metrics = {}
    for label in DECISIONS[:-1]:
        tp = confusion[label][label]
        precision = rate(tp, sum(row[label] for row in confusion.values()))
        recall = rate(tp, sum(confusion[label].values()))
        f1 = None if precision is None or recall is None else (2 * precision * recall / (precision + recall) if precision + recall else 0.0)
        class_metrics[label] = {"precision": precision, "recall": recall, "f1": f1}
    return {
        "item_count": n, "counts": dict(counts), "decision_accuracy": rate(counts["correct_decisions"], n),
        "complete_item_accuracy": rate(counts["complete_correct"], n),
        "abstention_rate": rate(counts["abstentions"], n),
        "decision_coverage": rate(n - counts["abstentions"], n),
        "selective_decision_accuracy": rate(counts["correct_decisions"], n - counts["abstentions"]),
        "answerable_extraction_accuracy": rate(counts["exact_answerable_records"], counts["answerable_requests"]),
        "extraction_field_accuracy": {field: rate(fields[field], counts["answerable_requests"]) for field in FIELDS},
        "unsupported_acceptance_rate": rate(counts["unsupported_accepted"], counts["not_supported_gold"]),
        "unsupported_fraction_of_accepted_claims": rate(counts["unsupported_accepted"], counts["accepted"]),
        "unsupported_numeric_fabrication_rate": rate(counts["unsupported_numeric_records"], counts["unanswerable_requests"]),
        "confusion": confusion, "class_metrics": class_metrics, "source_groups": groups, "items": details,
    }


def safe_archive_path(root, relative):
    if not isinstance(relative, str):
        raise ValueError("Archive path must be a string")
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("Archive path escapes evaluation directory")
    return target


def compare_archives(root=HERE):
    """Reproduce both archived runs without reading source URLs or editing files."""
    root = Path(root)
    freeze = read(root / "freeze.json")
    corpus = read(root / "candidate-corpus.json")
    corpus_sha = digest(root / "candidate-corpus.json")
    if corpus_sha != freeze["candidate_file_sha256"] or canonical_digest(corpus) != freeze["candidate_canonical_sha256"]:
        raise ValueError("Candidate corpus changed after freeze")
    if digest(root / "sources.json") != freeze["sources_file_sha256"]:
        raise ValueError("Source manifest changed after freeze")
    for name, expected in freeze["prompt_file_sha256"].items():
        if digest(safe_archive_path(root, name)) != expected:
            raise ValueError(f"Frozen prompt or contract changed: {name}")
    key = read(root / "answer-key.json")
    if digest(root / "answer-key.json") != freeze["answer_key_file_sha256"]:
        raise ValueError("Frozen author answer-key file changed")
    if canonical_digest(key["items"]) != freeze["answer_key_items_sha256"]:
        raise ValueError("Author label records changed after freeze")
    review = read(root / "gold-review.json")
    if review.get("status") != "BLIND_AI_REVIEW_COMPLETED" or review.get("human_adjudication") is not False:
        raise ValueError("Blind assistant gold review has not completed or is misrepresented")
    review_response = safe_archive_path(root, review["response_file"])
    if digest(review_response) != review["response_sha256"]:
        raise ValueError("Blind gold-review response archive changed")
    reviewed = read(review_response)
    reviewed_by_id = validate_response(reviewed, corpus, corpus_sha)
    if "metadata_file" in review:
        review_metadata = safe_archive_path(root, review["metadata_file"])
        if digest(review_metadata) != review["metadata_sha256"]:
            raise ValueError("Blind gold-review metadata archive changed")
    disagreement_ids = [item["id"] for item in key["items"]
                        if any(reviewed_by_id[item["id"]][field] != item[field] for field in ("decision", "record"))]
    if disagreement_ids != review.get("disagreement_ids"):
        raise ValueError("Recorded gold-review disagreements differ from archives")
    common_ids = [item["id"] for item in key["items"] if item["id"] not in disagreement_ids]
    label_differences = []
    for item in key["items"]:
        if item["id"] not in disagreement_ids:
            continue
        other = reviewed_by_id[item["id"]]
        differing_fields = []
        if item["decision"] != other["decision"]:
            differing_fields.append("decision")
        if item["record"] is None or other["record"] is None:
            if item["record"] != other["record"]:
                differing_fields.append("record_presence")
        else:
            differing_fields.extend(field for field in FIELDS if item["record"][field] != other["record"][field])
        label_differences.append({"id": item["id"], "fields": differing_fields,
                                  "author_reference": {"decision": item["decision"], "record": item["record"]},
                                  "reviewer_reference": {"decision": other["decision"], "record": other["record"]}})
    result = {"schema_version": 1, "dataset_id": corpus["dataset_id"], "candidate_file_sha256": corpus_sha,
              "source_count": len(read(root / "sources.json")["sources"]),
              "gold_review": {"method": "Two frozen assistant reference labels: author and fresh blind reviewer", "human_adjudication": False,
                              "status": "UNADJUDICATED_REFERENCE_DISAGREEMENT" if disagreement_ids else "REFERENCE_LABEL_AGREEMENT",
                              "disagreement_ids": disagreement_ids, "common_agreement_ids": common_ids,
                              "common_agreement_count": len(common_ids), "label_differences": label_differences,
                              "response_sha256": review["response_sha256"]},
              "scoring_policy": "Identical frozen exact-field scoring applied separately to both complete reference sets and to their common-agreement subset. No consensus labels, normalization or human adjudication are inferred.",
              "not_measured": ["Independent human accuracy", "Production extraction accuracy", "Investment alpha", "Review-time saving", "Cost saving"],
              "runs": {}}
    for name, kind in (("baseline", "baseline_session"), ("structured", "structured_session")):
        meta = read(root / "runs" / f"{name}-metadata.json")
        if meta.get("run_kind") != kind or meta.get("candidate_file_sha256") != corpus_sha or meta.get("answer_key_access") is not False:
            raise ValueError(f"Invalid run metadata: {name}")
        prompt = safe_archive_path(root, meta["prompt_file"])
        expected_prompt = f"{name}-prompt.md"
        if meta["prompt_file"] != expected_prompt or digest(prompt) != meta["prompt_sha256"]:
            raise ValueError(f"Prompt metadata/archive mismatch: {name}")
        response_path = safe_archive_path(root, meta["response_file"])
        if digest(response_path) != meta["response_sha256"]:
            raise ValueError(f"Response metadata/archive mismatch: {name}")
        response = read(response_path)
        result["runs"][name] = {"metadata": meta, "metrics_by_reference": {
            "author": evaluate(corpus, key, response, corpus_sha),
            "blind_reviewer": evaluate(corpus, reviewed, response, corpus_sha),
            "common_agreement": evaluate(corpus, key, response, corpus_sha, item_ids=common_ids),
        }}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify frozen inputs and exactly reproduce committed results; no writes")
    parser.add_argument("--output", type=Path, help="Write reproduced results to this requested path")
    args = parser.parse_args()
    result = compare_archives()
    if args.check:
        if result != read(HERE / "comparison-results.json"):
            raise ValueError("Archived comparison-results.json does not reproduce")
        print("PASS: frozen corpus, both reference-label sets, both session archives and reference-sensitivity results reproduce")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not args.check and not args.output:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
