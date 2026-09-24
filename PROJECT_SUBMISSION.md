# ProofJudge — Project Explorer Submission Dossier

## One-sentence summary

ProofJudge is a GenLayer-native milestone escrow where a sponsor locks GEN, an assigned contractor submits live public evidence, and validator consensus determines whether payment is released or the sponsor later recovers the escrow.

## Problem

Freelance milestones, grants, service deliverables and performance contracts often depend on subjective acceptance criteria. Deterministic smart contracts can escrow value, but they cannot open arbitrary live webpages and judge whether a delivered result satisfies a natural-language brief.

Centralized marketplaces solve that by appointing a trusted reviewer. ProofJudge replaces that single reviewer with GenLayer consensus.

## GenLayer-native solution

The sponsor commits:

- one assigned contractor;
- a natural-language requirement;
- a judging rubric;
- a deadline;
- native GEN escrow.

The contractor submits a public deliverable URL and an independent support URL. The Intelligent Contract fetches both live. A leader proposes a structured decision; validators independently re-fetch and re-evaluate the evidence. The accepted result changes contract state and therefore who can withdraw the escrow.

V4 adds an explicit **70/100 minimum approval threshold**, bounded on-chain evidence snapshots, exact validator equivalence over reason + evidence basis + snapshots, explicit unavailable/contradictory evidence failures, one-shot party challenges, stalled-resolution refund grace, lifecycle timestamps, retry limits and a policy version stored with every agreement.

## Verified live Studionet deployment

- Contract: `0x76D61aAec5bD4625346858acCd6dAb39966c4247`
- Explorer: https://explorer-studio.genlayer.com/address/0x76D61aAec5bD4625346858acCd6dAb39966c4247
- Live app: https://proofjudge-genlayer-frontend.vercel.app
- Full verification workflow: https://github.com/maho0638/proofjudge-genlayer/actions/runs/35993240108

### Live outcome 1: production ProofJudge release

`proofjudge-production-milestone-v4`

Real production page + independent repository evidence was judged:

`APPROVED · 100/100 · CROSS_CHECK → PAID`

The contractor then claimed the escrow.

### Live outcome 2: intentionally irrelevant evidence

`irrelevant-evidence-refund-v1`

Unrelated evidence was judged:

`REJECTED · 95/100 rejection confidence · EVIDENCE_GAP`

Contractor payout never opened. After the deadline the sponsor executed the guarded refund:

`REFUNDED`

## Product completeness

The production UI supports the full lifecycle:

- wallet connection;
- on-chain agreement discovery;
- GEN escrow creation;
- assigned contractor;
- natural-language requirement and rubric;
- deadline;
- two independent HTTPS evidence hosts;
- live contract state;
- role-aware actions;
- consensus resolution;
- contractor claim;
- rejected-evidence retry;
- sponsor refund;
- audit timestamps and policy version;
- finalized transaction activity;
- walletless live reviewer proof;
- live integrity gate over both economic outcomes.

## Verification and engineering quality

The canonical successful workflow also proves `DEPLOYED_SOURCE_MATCH=true`: the deployed Studionet source and repository `contracts/proof_judge.py` normalize to SHA-256 `0cba1187b5478d885f8c150e1597298d4bc550b7552a01862c43eaeaa4f79ca9`.

The repository includes:

- expanded direct and repository-safety tests;
- strict mocks and stored-state pickling checks;
- explicit validator-disagreement testing;
- GenVM lint/validation;
- Next.js production build;
- live Studionet integration that deploys a fresh contract and proves both PAID and REFUNDED paths.

## Differentiation

ProofJudge is a bilateral 1:1 performance agreement. It does not choose among competing researchers. Its core problem is acceptance of one assigned contractor's milestone and economic settlement based on consensus over live evidence.

Reviewer start point: `docs/STEWARD_VERIFICATION.md`.
