"""Replay archived AI-authored artifacts through the actual local CLI.

This is a host/engine integration check, not an embedded LLM or a new research
run. It never retrieves sources, generates analysis or calls human review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples/host-integration"


def run(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    commands = []
    run_dir = output / "run"
    transcript = output / "transcript.txt"

    def cli(*arguments: str, expected: int = 0):
        command = [sys.executable, "-m", "sf_agent", *map(str, arguments)]
        process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=30)
        entry = {"argv": command, "returncode": process.returncode,
                 "stdout": process.stdout, "stderr": process.stderr}
        commands.append(entry)
        with transcript.open("a", encoding="utf-8") as stream:
            stream.write("$ " + " ".join(command) + "\n")
            stream.write(process.stdout)
            stream.write(process.stderr)
            stream.write(f"[exit {process.returncode}]\n\n")
        if process.returncode != expected:
            raise RuntimeError(f"CLI returned {process.returncode}, expected {expected}: {arguments[0]}")
        return json.loads(process.stdout) if process.returncode == 0 else process.stderr

    initial = cli("init", "--request", CASE / "request.json", "--out", run_dir)
    packets = cli("next", "--run", run_dir)
    if [packet["stage"]["id"] for packet in packets] != ["mandate"]:
        raise RuntimeError("fresh run did not emit the mandate packet")

    def artifact(name: str, packet: dict) -> Path:
        data = json.loads((CASE / name).read_text(encoding="utf-8"))
        data.update(run_id=packet["run_id"], input_digest=packet["input_digest"])
        target = output / (name.removesuffix(".json") + f"-r{packet['revision']}.json")
        target.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        return target

    mandate = artifact("mandate.json", packets[0])
    first = cli("submit", "--run", run_dir, "--stage", "mandate",
                "--artifact", mandate, "--revision", packets[0]["revision"])
    packets = cli("next", "--run", run_dir)
    evidence = artifact("evidence.json", packets[0])
    stale_error = cli("submit", "--run", run_dir, "--stage", "evidence",
                      "--artifact", evidence, "--revision", 0, expected=2)
    unchanged = cli("status", "--run", run_dir)
    if "stale revision" not in stale_error or unchanged["revision"] != first["revision"]:
        raise RuntimeError("stale submission was not rejected without changing state")
    cli("submit", "--run", run_dir, "--stage", "evidence",
        "--artifact", evidence, "--revision", packets[0]["revision"])
    packets = cli("next", "--run", run_dir)
    exposure = artifact("exposure-needs-data.json", packets[0])
    stopped = cli("submit", "--run", run_dir, "--stage", "exposure",
                  "--artifact", exposure, "--revision", packets[0]["revision"])

    # Revision of an upstream artifact is a real submission, not direct state editing.
    revised_packet = dict(packets[0], revision=stopped["revision"])
    revised = artifact("mandate-revised.json", revised_packet)
    invalidated = cli("submit", "--run", run_dir, "--stage", "mandate",
                      "--artifact", revised, "--revision", stopped["revision"])
    if invalidated["stages"]["evidence"] != "PENDING" or invalidated["stages"]["exposure"] != "PENDING":
        raise RuntimeError("upstream revision failed to invalidate downstream artifacts")
    packets = cli("next", "--run", run_dir)
    evidence = artifact("evidence.json", packets[0])
    cli("submit", "--run", run_dir, "--stage", "evidence",
        "--artifact", evidence, "--revision", packets[0]["revision"])
    packets = cli("next", "--run", run_dir)
    exposure = artifact("exposure-needs-data.json", packets[0])
    final = cli("submit", "--run", run_dir, "--stage", "exposure",
                "--artifact", exposure, "--revision", packets[0]["revision"])
    exports = cli("export", "--run", run_dir, "--out", output / "export")
    state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
    if final["mode"] != "research" or final["status"] != "NEEDS_DATA":
        raise RuntimeError("research sample did not stop on material missing data")
    if final["human_review"] is not None or final["execution_authorized"] is not False:
        raise RuntimeError("integration check unexpectedly asserted approval or authority")
    archived = sorted({item["stage_id"] for item in state["history"]})
    if archived != ["evidence", "exposure", "mandate"]:
        raise RuntimeError("superseded artifacts were not archived")
    facts = [claim for a in state["artifacts"].values() for claim in a["claims"] if claim["kind"] == "FACT"]
    if not facts or any(claim["evidence_ids"] != ["HM-OPENING-2025"] for claim in facts):
        raise RuntimeError("reviewed evidence lineage was not retained")
    result = {
        "status": "PASS", "verification_kind": "preauthored_ai_artifact_cli_replay",
        "embedded_model": False, "new_source_retrieval": False,
        "separate_cli_processes": True, "python_version": sys.version.split()[0],
        "initial_revision": initial["revision"], "final_revision": final["revision"],
        "stale_revision_rejected": True, "downstream_invalidated_and_archived": archived,
        "final_research_status": final["status"], "mode": final["mode"],
        "open_material_issues": final["blockers"], "human_review": None,
        "execution_authorized": False, "export_files": [Path(p).name for p in exports],
        "source_document_ingestion_tested": False, "provider_installation_tested": False,
        "input_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(CASE.glob("*.json")) if p.name not in {"session-result.json", "session-commands.json"}},
        "transcript_sha256": hashlib.sha256(transcript.read_bytes()).hexdigest(),
    }
    (output / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="New output directory; never overwritten")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.out), indent=2))
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
