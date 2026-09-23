# ProofJudge — Consensus Milestone Escrow on GenLayer

[![CI](https://github.com/maho0638/proofjudge-genlayer/actions/workflows/ci.yml/badge.svg)](https://github.com/maho0638/proofjudge-genlayer/actions/workflows/ci.yml)

**Live app:** https://proofjudge-genlayer-frontend.vercel.app

ProofJudge is a GenLayer-native performance-based contracting product. A sponsor creates a milestone agreement and escrows native GEN, an assigned contractor submits a public deliverable plus independent supporting evidence, and GenLayer validator consensus decides whether the precommitted acceptance criteria were satisfied. Only approved work can unlock the contractor's payment.

## Why GenLayer is central

A deterministic smart contract can hold funds, but it cannot open arbitrary webpages and judge whether a real-world deliverable satisfies a natural-language requirement. ProofJudge puts that settlement-critical judgment inside the Intelligent Contract.

The contract uses:

- `gl.nondet.web.render` to fetch the primary deliverable and independent support at judgment time;
- `gl.nondet.exec_prompt` for a bounded structured verdict;
- `gl.vm.run_nondet_unsafe` with independent validator re-execution;
- `@gl.public.write.payable` and `gl.message.value` for native GEN escrow;
- GenLayer value transfer for contractor payout or guarded sponsor refund.

The consensus result is not advisory: it changes who can withdraw value held by the contract.

## Product lifecycle

1. **Create agreement** — sponsor locks native GEN and commits to a contractor, requirement, rubric and deadline.
2. **Submit evidence** — the assigned contractor provides the primary deliverable URL plus an independent supporting URL.
3. **Resolve** — the Intelligent Contract fetches both live sources and validators independently judge the same precommitted criteria.
4. **Retry or approve** — rejected evidence may be replaced before deadline, up to three attempts.
5. **Claim** — an approved contractor can claim the escrowed GEN.
6. **Refund** — expired OPEN or REJECTED work has a sponsor-only refund path; unresolved SUBMITTED evidence cannot be bypassed.

## Verified live Studionet deployment

- **Network:** GenLayer Studionet
- **Chain ID:** 61999
- **Contract:** `0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc`
- **Explorer:** https://explorer-studio.genlayer.com/address/0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc
- **Successful full lifecycle workflow:** https://github.com/maho0638/proofjudge-genlayer/actions/runs/35925077495
- **Verified job:** `example-domain-milestone-v2`

### Real end-to-end transactions

- Create GEN escrow: https://explorer-studio.genlayer.com/tx/0x0b42a662a7e9f6da6b09ff5fdb49f593781ba28f6bb508d3b70a18936a0838c6
- Submit independent evidence: https://explorer-studio.genlayer.com/tx/0x021ec1dc5c5afa5181c236b59a56b424b1e53953dd5459bcb9492165872db77d
- Resolve by validator consensus: https://explorer-studio.genlayer.com/tx/0x2621e4f4a2ecedb901c5e1ad25c975d4762e999918e37c6f56c70a255e7fb7db
- Contractor claims payment: https://explorer-studio.genlayer.com/tx/0x3d183cafb0ac32e5cd319f0059e53dce220982b0c4e8c43b5a58be044ce5e1dd

### Stored settlement

- status: `PAID`
- confidence: `97/100`
- reason code: `CROSS_CHECK`
- reward claimed: `true`
- primary evidence: `https://example.com`
- independent support: `https://www.iana.org/help/example-domains`

Rationale:

> Approved because independent support corroborates the primary evidence. Confidence 97/100.

## Safety and market integrity

- positive GEN reward is required at creation;
- sponsor and contractor must be different wallets;
- only the assigned contractor can submit evidence and claim payment;
- both evidence URLs must use HTTPS and distinct hostnames;
- evidence text is explicitly treated as untrusted prompt input;
- verdict output is restricted to approved/rejected, bounded confidence and one allowed reason code;
- validators independently re-fetch and re-evaluate the evidence;
- rejected work may be retried, but attempts are capped at three;
- payment is single-use and state changes before external transfer;
- expired OPEN/REJECTED work can be refunded only by the sponsor;
- SUBMITTED evidence must be resolved before funds can move;
- an on-chain job index lets the UI discover agreements without pre-known IDs.

## Automated verification

The repository includes:

- 9 direct contract tests;
- GenVM lint;
- Next.js production build;
- live Studionet deploy → escrow → evidence → consensus → claim integration test;
- machine-readable verified settlement manifest.

## Source map

- Intelligent Contract: `contracts/proof_judge.py`
- Direct tests: `tests/direct/test_proof_judge.py`
- Live integration test: `tests/integration/test_studionet_smoke.py`
- Frontend: `frontend/app/page.tsx`
- GenLayer browser client: `frontend/lib/genlayer.ts`
- CI: `.github/workflows/ci.yml`
- Studionet verification: `.github/workflows/deploy-studionet.yml`
- Submission dossier: `PROJECT_SUBMISSION.md`
- Steward walkthrough: `docs/STEWARD_VERIFICATION.md`
- Quality mapping: `docs/QUALITY_BAR.md`
- Security/failure modes: `docs/SECURITY.md`
- Product readiness: `docs/PRODUCT_READINESS.md`
- Machine-readable proof: `frontend/public/verified-demo.json`

ProofJudge is a working Studionet prototype, not a production financial service. Portal point awards remain a reviewer decision.
