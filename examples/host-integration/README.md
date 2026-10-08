# A filesystem host completing a bounded research loop

On 8 October 2026, a ChatGPT Work / Codex session read Heidelberg Materials’ [18 June 2025 Brevik announcement](https://www.heidelbergmaterials.com/en/pr-2025-06-18), authored the adjacent research artifacts and submitted them through the actual Python CLI in a fresh local Git clone. The host copied the current packet identifiers into each artifact. No synthetic evidence or human-review command was used.

The scoped source fact is announced design capacity of around **400,000 tonnes of CO2 annually**. Capacity does not establish delivered capture, permanent storage, avoided emissions, operating cash flows or a tradable equity valuation. The register preserves the source date, retrieval date, entity boundary, locator and that limitation. Source-review status is an AI-host attestation, not authenticated or independent human certification.

| Host operation | Observed result |
|---|---|
| Initialize and read a work packet | Research mode, revision 0, mandate ready |
| Submit a researched mandate and evidence register | Current run ID and input digest accepted |
| Attempt an evidence submission with stale revision 0 | Exit 2; state remains at revision 1 |
| Submit the capacity fact and named economic gaps | Exposure returns `NEEDS_DATA` |
| Revise the upstream mandate | Evidence and exposure become pending; superseded artifacts archived |
| Refresh packets and resubmit affected artifacts | Final revision 6; `NEEDS_DATA` retained |
| Export the actual packet and evidence lineage | Four export files; no human review; execution unauthorized |

Inspect [session-result.json](session-result.json), the [raw command transcript](session-transcript.txt), [structured commands](session-commands.json) and the [exported research packet](session-export/research-packet.md). The fresh checkout used the recorded base commit plus the explicitly listed host-example overlay; it was not a claim that the uncommitted example already existed remotely.

## Reproduce the integration behavior

From a fresh clone or source download, with Python 3.10 or later:

```bash
python3 scripts/verify_host_integration.py --out runs/host-integration-01
```

Use a new directory. The helper replays the archived AI-authored artifacts and binds the current run identifiers before submission. Its checks use separate CLI processes and fail if stale revisions, invalidation, missing data or export behavior differ. It does not retrieve documents, call an LLM, generate new research or attest human approval. Replaying the fixed example is software verification. The initial session’s document reading and artifact authoring occurred outside the helper.

## What this verifies

The actual session demonstrates a filesystem-enabled host’s ability to read repository instructions, author evidence-linked artifacts, execute the CLI and carry them through the gated workflow. It covers a narrow local host/engine handoff, revision discipline, material-gap handling and export. A stage marked `COMPLETE` means its scoped record satisfies the structural contract; OPEN material issues still prevent research approval. The complete issuer workflow is deliberately unfinished.

No product-specific plugin installation, automatic skill activation, embedded model, source-document ingestion connector, market feed, independent analyst review, legal certification or investment performance was tested. Text-only use of the prompts does not enforce the engine. Adding or correcting frozen evidence requires a new run; the recorded revision revises analysis, not evidence.
