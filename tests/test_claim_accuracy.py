"""Scoring and archive-integrity tests; synthetic fixtures are not model accuracy."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hhfinai_claim_accuracy", ROOT / "evaluation" / "claim-accuracy" / "score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)


class ClaimAccuracyTests(unittest.TestCase):
    def setUp(self):
        self.corpus = {"dataset_id": "test-fixture", "items": [{"id": name, "source_id": "T"} for name in ("A", "B", "C")]}
        record = {"value": 10, "unit": "EUR_million", "entity_id": "T", "period": "CY2024", "scope": "GROUP"}
        self.key = {"items": [{"id": "A", "decision": "supported", "record": record, "rationale": "fixture"},
                              {"id": "B", "decision": "contradicted", "record": {**record, "value": 20}, "rationale": "fixture"},
                              {"id": "C", "decision": "insufficient", "record": None, "rationale": "fixture"}]}
        self.response = {"schema_version": 1, "dataset_id": "test-fixture", "candidate_file_sha256": "fixture-sha",
                         "answer_key_access": False,
                         "items": [{"id": row["id"], "decision": row["decision"], "record": deepcopy(row["record"]), "reason": "Test fixture only"}
                                   for row in self.key["items"]]}

    def evaluate(self, response=None):
        return score.evaluate(self.corpus, self.key, response or self.response, "fixture-sha")

    def test_exact_and_field_scores_are_separate(self):
        result = self.evaluate()
        self.assertEqual(result["complete_item_accuracy"], 1)
        self.assertEqual(result["counts"]["answerable_requests"], 2)
        self.response["items"][0]["record"]["scope"] = "SEGMENT"
        result = self.evaluate()
        self.assertEqual(result["decision_accuracy"], 1)
        self.assertEqual(result["extraction_field_accuracy"]["value"], 1)
        self.assertEqual(result["extraction_field_accuracy"]["scope"], .5)
        self.assertEqual(result["answerable_extraction_accuracy"], .5)
        self.assertEqual(result["complete_item_accuracy"], 2 / 3)

    def test_abstention_has_zero_coverage_and_no_selective_score(self):
        for row in self.response["items"]:
            row.update(decision="abstain", record=None)
        result = self.evaluate()
        self.assertEqual(result["decision_accuracy"], 0)
        self.assertEqual(result["decision_coverage"], 0)
        self.assertEqual(result["abstention_rate"], 1)
        self.assertIsNone(result["selective_decision_accuracy"])
        self.assertIsNone(result["unsupported_fraction_of_accepted_claims"])
        self.assertEqual(result["answerable_extraction_accuracy"], 0)

    def test_insufficient_is_not_abstention(self):
        result = self.evaluate()
        self.assertEqual(result["abstention_rate"], 0)
        self.assertEqual(result["confusion"]["insufficient"]["insufficient"], 1)

    def test_unsupported_acceptance_denominators_and_numeric_fabrication(self):
        for row in self.response["items"]:
            row["decision"] = "supported"
        self.response["items"][2]["record"] = deepcopy(self.response["items"][0]["record"])
        result = self.evaluate()
        self.assertEqual(result["unsupported_acceptance_rate"], 1)
        self.assertEqual(result["unsupported_fraction_of_accepted_claims"], 2 / 3)
        self.assertEqual(result["unsupported_numeric_fabrication_rate"], 1)

    def test_numeric_tolerance_and_canonical_unit(self):
        self.response["items"][0]["record"]["value"] = 10 + 1e-9
        self.assertEqual(self.evaluate()["extraction_field_accuracy"]["value"], 1)
        self.response["items"][0]["record"].update(value=10000, unit="EUR_thousand")
        result = self.evaluate()
        self.assertEqual(result["extraction_field_accuracy"]["value"], .5)
        self.assertEqual(result["extraction_field_accuracy"]["unit"], .5)

    def test_duplicate_missing_unknown_and_dataset_rejected(self):
        variants = [deepcopy(self.response) for _ in range(4)]
        variants[0]["items"].append(deepcopy(variants[0]["items"][0]))
        variants[1]["items"].pop()
        variants[2]["items"][0]["id"] = "UNKNOWN"
        variants[3]["candidate_file_sha256"] = "different"
        for response in variants:
            with self.subTest(response=response), self.assertRaises(ValueError):
                self.evaluate(response)

    def test_bool_nonfinite_and_partial_record_rejected(self):
        for bad in (True, float("nan"), float("inf"), "10"):
            response = deepcopy(self.response)
            response["items"][0]["record"]["value"] = bad
            with self.subTest(value=bad), self.assertRaises(ValueError):
                self.evaluate(response)
        del self.response["items"][0]["record"]["period"]
        with self.assertRaises(ValueError):
            self.evaluate()

    def test_key_access_or_missing_reason_rejected(self):
        self.response["answer_key_access"] = True
        with self.assertRaises(ValueError):
            self.evaluate()
        self.response["answer_key_access"] = False
        self.response["items"][0].pop("reason")
        with self.assertRaises(ValueError):
            self.evaluate()

    def test_nonfinite_json_and_path_escape_rejected(self):
        with TemporaryDirectory() as name:
            root = Path(name)
            (root / "bad.json").write_text('{"value":NaN}')
            with self.assertRaises(ValueError):
                score.read(root / "bad.json")
            with self.assertRaises(ValueError):
                score.safe_archive_path(root, "../outside.json")

    def make_archive(self, root):
        root = Path(root)
        (root / "runs").mkdir()
        def write(name, value):
            (root / name).write_text(json.dumps(value, indent=2) + "\n")
        write("candidate-corpus.json", self.corpus)
        write("sources.json", {"sources": [{"id": "T"}]})
        write("answer-key.json", self.key)
        corpus_sha = score.digest(root / "candidate-corpus.json")
        response = {**self.response, "candidate_file_sha256": corpus_sha}
        write("blind-review.json", response)
        write("gold-review.json", {"status": "BLIND_AI_REVIEW_COMPLETED", "human_adjudication": False,
                                   "response_file": "blind-review.json", "response_sha256": score.digest(root / "blind-review.json"),
                                   "disagreement_ids": []})
        prompts = {}
        for name in ("baseline", "structured"):
            prompt_name = f"{name}-prompt.md"
            (root / prompt_name).write_text("Synthetic test prompt")
            prompts[prompt_name] = score.digest(root / prompt_name)
            response_name = f"runs/{name}-response.json"
            write(response_name, response)
            write(f"runs/{name}-metadata.json", {"run_kind": f"{name}_session", "candidate_file_sha256": corpus_sha,
                                                "prompt_file": prompt_name, "prompt_sha256": prompts[prompt_name],
                                                "response_file": response_name, "response_sha256": score.digest(root / response_name),
                                                "answer_key_access": False, "model_revision": "synthetic test fixture"})
        write("freeze.json", {"candidate_file_sha256": corpus_sha, "candidate_canonical_sha256": score.canonical_digest(self.corpus),
                              "sources_file_sha256": score.digest(root / "sources.json"), "prompt_file_sha256": prompts,
                              "answer_key_file_sha256": score.digest(root / "answer-key.json"),
                              "answer_key_items_sha256": score.canonical_digest(self.key["items"])})

    def test_archive_hashes_and_label_drift_fail_closed(self):
        for changed in ("candidate-corpus.json", "sources.json", "baseline-prompt.md", "runs/baseline-response.json", "blind-review.json"):
            with self.subTest(changed=changed), TemporaryDirectory() as name:
                root = Path(name)
                self.make_archive(root)
                self.assertEqual(score.compare_archives(root)["runs"]["baseline"]["metrics_by_reference"]["author"]["decision_accuracy"], 1)
                with (root / changed).open("a") as out:
                    out.write(" ")
                with self.assertRaises(ValueError):
                    score.compare_archives(root)
        with TemporaryDirectory() as name:
            root = Path(name)
            self.make_archive(root)
            key = score.read(root / "answer-key.json")
            key["items"][0]["record"]["value"] = 99
            (root / "answer-key.json").write_text(json.dumps(key))
            with self.assertRaises(ValueError):
                score.compare_archives(root)

    def test_blind_review_disagreement_requires_accurate_register(self):
        with TemporaryDirectory() as name:
            root = Path(name)
            self.make_archive(root)
            response = score.read(root / "blind-review.json")
            response["items"][0]["decision"] = "contradicted"
            (root / "blind-review.json").write_text(json.dumps(response))
            review = score.read(root / "gold-review.json")
            review.update(response_sha256=score.digest(root / "blind-review.json"), disagreement_ids=[])
            (root / "gold-review.json").write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError, "disagreements"):
                score.compare_archives(root)

    def test_exact_reference_sensitivity_and_common_subset(self):
        with TemporaryDirectory() as name:
            root = Path(name)
            self.make_archive(root)
            response = score.read(root / "blind-review.json")
            response["items"][0]["record"]["period"] = "FY2024"
            (root / "blind-review.json").write_text(json.dumps(response))
            review = score.read(root / "gold-review.json")
            review.update(response_sha256=score.digest(root / "blind-review.json"), disagreement_ids=["A"])
            (root / "gold-review.json").write_text(json.dumps(review))
            result = score.compare_archives(root)
            metrics = result["runs"]["baseline"]["metrics_by_reference"]
            self.assertEqual(metrics["author"]["complete_item_accuracy"], 1)
            self.assertEqual(metrics["blind_reviewer"]["complete_item_accuracy"], 2 / 3)
            self.assertEqual(metrics["blind_reviewer"]["extraction_field_accuracy"]["period"], .5)
            self.assertEqual(metrics["common_agreement"]["item_count"], 2)
            self.assertEqual(metrics["common_agreement"]["complete_item_accuracy"], 1)
            self.assertEqual(result["gold_review"]["status"], "UNADJUDICATED_REFERENCE_DISAGREEMENT")
            self.assertEqual(result["gold_review"]["label_differences"][0]["fields"], ["period"])

    def test_empty_common_subset_reports_null_instead_of_perfect(self):
        result = score.evaluate(self.corpus, self.key, self.response, "fixture-sha", item_ids=[])
        self.assertEqual(result["item_count"], 0)
        self.assertIsNone(result["decision_accuracy"])
        self.assertIsNone(result["complete_item_accuracy"])


if __name__ == "__main__":
    unittest.main()
