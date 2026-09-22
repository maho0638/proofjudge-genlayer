# SourceVerifier — Intelligent Contract Submission

## Summary

SourceVerifier is a reusable GenLayer Intelligent Contract that verifies a factual claim against two independent public web sources and stores a consensus-backed verdict on-chain.

## Contract

https://github.com/maho0638/proofjudge-genlayer/blob/main/contracts/source_verifier.py

## Why it needs GenLayer

The contract performs work that a deterministic smart contract cannot do on its own:

- fetches live public web content,
- semantically compares evidence with a natural-language claim,
- asks an LLM for a structured judgment,
- independently re-runs the evaluation in validator execution,
- reaches consensus over a non-deterministic result.

## Result schema

Each verification stores:

- verdict: supported / contradicted / insufficient
- confidence: 0–100
- sources_agree: 0–2
- rationale
- original claim
- both source URLs
- creator

## Safety / robustness

- HTTPS-only evidence sources
- two distinct source URLs required
- bounded input sizes
- duplicate verification IDs rejected
- prompt-injection hardening: webpage text is explicitly treated as untrusted evidence
- exact validator agreement on verdict
- exact validator agreement on source-agreement count
- bounded tolerance for confidence variance

## Tests

Direct-mode tests:
https://github.com/maho0638/proofjudge-genlayer/blob/main/tests/direct/test_source_verifier.py

CI:
https://github.com/maho0638/proofjudge-genlayer/actions/runs/35790271756

The CI run passed all direct tests and GenVM lint/validation.

## Live Studionet verification

Contract:
https://explorer-studio.genlayer.com/address/0x10F95C997358EfbFfc586979ED8E4c6568609B5c

Contract address:
`0x10F95C997358EfbFfc586979ED8E4c6568609B5c`

Live transaction:
https://explorer-studio.genlayer.com/tx/0xdff346bd4b4bd87546b577879c25f0f9ee805e2dd1d629d4263776aef6d2086d

Transaction hash:
`0xdff346bd4b4bd87546b577879c25f0f9ee805e2dd1d629d4263776aef6d2086d`

Studionet workflow:
https://github.com/maho0638/proofjudge-genlayer/actions/runs/35790275957

Live claim:
`example.com is intended for use in documentation examples.`

Sources:
- https://example.com
- https://www.iana.org/help/example-domains

Consensus-backed stored result:
- verdict: `supported`
- confidence: `98/100`
- sources_agree: `2/2`
- consensus: `MAJORITY_AGREE`
