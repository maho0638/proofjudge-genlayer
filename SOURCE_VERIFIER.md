# SourceVerifier — Reusable GenLayer Intelligent Contract

SourceVerifier is a standalone GenLayer Intelligent Contract for verifying a factual claim against **two independent public web sources**.

It is intentionally small and reusable: any dApp, bounty system, oracle workflow, agent, or governance process can call it to turn ambiguous web evidence into a consensus-backed on-chain verification record.

## What it does

`verify_claim(verification_id, claim, source_url_1, source_url_2)`

1. Fetches both HTTPS sources with `gl.nondet.web.render`.
2. Gives only those source contents and the claim to an LLM.
3. Produces a structured verdict:
   - `supported`
   - `contradicted`
   - `insufficient`
4. Independently re-evaluates the evidence in validator execution.
5. Requires validators to agree on the verdict and number of agreeing sources.
6. Stores the consensus-backed verdict, confidence, source agreement count, and rationale on-chain.

## Why GenLayer

A deterministic smart contract cannot open arbitrary public webpages and reason about their meaning. SourceVerifier uses GenLayer specifically for:

- live web access,
- LLM-based semantic evaluation,
- non-deterministic execution,
- validator consensus over a subjective result.

## Safety properties

- HTTPS-only sources
- two distinct sources required
- prompt-injection defense: source text is explicitly treated as untrusted evidence
- bounded claim, ID, confidence, and rationale
- duplicate verification IDs rejected
- validators independently recompute the verdict
- exact consensus required for verdict and source-agreement count
- confidence may vary only within a small tolerance

## Files

- Contract: `contracts/source_verifier.py`
- Direct tests: `tests/direct/test_source_verifier.py`
- Studionet smoke test: `tests/integration/test_source_verifier_studionet.py`

## Current verification status

Direct tests and GenVM lint are executed by GitHub Actions. A separate live Studionet workflow deploys the contract and verifies a stable factual claim against two public sources.
