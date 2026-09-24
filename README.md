# ProofJudge — Consensus Milestone Escrow on GenLayer

[![CI](https://github.com/maho0638/proofjudge-genlayer/actions/workflows/ci.yml/badge.svg)](https://github.com/maho0638/proofjudge-genlayer/actions/workflows/ci.yml)

**Live app:** https://proofjudge-genlayer-frontend.vercel.app

ProofJudge is a bilateral performance-contract product built around a GenLayer Intelligent Contract. A sponsor assigns one contractor, precommits a natural-language requirement and judging rubric, and escrows native GEN. The contractor submits a public deliverable plus independent supporting evidence. GenLayer fetches those sources live and validator consensus determines whether the contractor can claim payment.

This is not an AI answer displayed by a frontend. The consensus result changes economic state.

## Why GenLayer is essential

A deterministic smart contract can hold funds, but it cannot open arbitrary webpages and judge whether a real-world deliverable satisfies a human-readable acceptance criterion. ProofJudge puts that settlement-critical judgment inside the Intelligent Contract.

The contract uses:

- `gl.nondet.web.render` for live public evidence;
- `gl.nondet.exec_prompt` for a bounded structured verdict;
- `gl.vm.run_nondet_unsafe` with independent validator re-execution;
- `@gl.public.write.payable` and `gl.message.value` for native GEN escrow;
- GenLayer native value transfer for contractor payout and sponsor refund.

The validator does not merely validate JSON shape. It independently re-fetches the evidence and repeats the judgment. This follows GenLayer's current Equivalence Principle guidance: https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle

## V3 settlement policy

The current contract hardens the economic decision:

- approvals require at least **70/100 confidence**;
- low-confidence “yes” responses are normalized to rejection and cannot unlock GEN;
- evidence-fetch failures become `SOURCE_UNAVAILABLE`, never an approval;
- positive and failure reason codes are semantically constrained;
- a zero-address contractor is rejected;
- agreement deadlines cannot exceed 365 days;
- rejected evidence may be retried, but attempts are capped at three;
- submitted evidence cannot be bypassed by sponsor refund;
- creation, submission, resolution and settlement timestamps are stored on-chain;
- every job records `policy_version = PJ_V3_MINCONF70`.

## Product lifecycle

1. **Create** — sponsor selects a contractor, commits requirement/rubric/deadline and locks native GEN.
2. **Submit** — assigned contractor supplies two HTTPS evidence URLs from distinct hostnames.
3. **Resolve** — the Intelligent Contract fetches both sources; leader and validators independently judge the precommitted criteria.
4. **Approve or reject** — accepted consensus stores a bounded confidence score and structured reason.
5. **Claim** — only an APPROVED contractor with confidence ≥70 can claim.
6. **Retry** — rejected work may replace evidence before the deadline, up to three attempts.
7. **Refund** — expired OPEN or REJECTED work can be refunded only by the sponsor.

## Verified Studionet v3

- **Network:** GenLayer Studionet
- **Chain ID:** 61999
- **Contract:** `0x699f62FA0f53B92D85949B1F046f6B50209707eE`
- **Explorer:** https://explorer-studio.genlayer.com/address/0x699f62FA0f53B92D85949B1F046f6B50209707eE
- **Successful full live workflow:** https://github.com/maho0638/proofjudge-genlayer/actions/runs/35985412296

### Outcome A — real production milestone → PAID

Job: `proofjudge-production-milestone-v3`

The primary evidence was the real ProofJudge production deployment and the independent support was the public repository README.

- production evidence: https://proofjudge-genlayer-frontend.vercel.app
- independent support: https://raw.githubusercontent.com/maho0638/proofjudge-genlayer/main/README.md
- decision: `APPROVED`
- confidence: `98/100`
- reason: `CROSS_CHECK`
- final state: `PAID`
- contractor reward claimed: `true`

Transactions:

- create escrow: https://explorer-studio.genlayer.com/tx/0xb9cdb9211b7775911b70e4af93b0408644c5d9ddafb0123d20fbcfc20dd62c9b
- submit evidence: https://explorer-studio.genlayer.com/tx/0x82e871f6510cf5e8af66e778a7b879e4a19d04f01c717103862d43bd5c19eb6d
- resolve consensus: https://explorer-studio.genlayer.com/tx/0x3fa02241eb60d23604ab3bde2d1eee9334794557f73af280f3ae3abdc2752bef
- claim payment: https://explorer-studio.genlayer.com/tx/0x8c98e573115a3a41a28456c59aa4eef1060ab1fdc713a69db74b50bd05d18013

### Outcome B — irrelevant evidence → REJECTED → REFUNDED

Job: `irrelevant-evidence-refund-v1`

The submitted pages were intentionally unrelated to the committed ProofJudge milestone.

- consensus decision: `REJECTED`
- confidence in the rejected submission: `2/100`
- reason: `EVIDENCE_GAP`
- contractor payout never opened
- after deadline the sponsor recovered escrow
- final state: `REFUNDED`

Transactions:

- create escrow: https://explorer-studio.genlayer.com/tx/0xd29492ee5f16e2d595b6792d17058c325ab0a9b4456cd7763eedfa2a01ebf637
- submit irrelevant evidence: https://explorer-studio.genlayer.com/tx/0xa790bb59991bd38e6e211cebcccba62fe2ea3870d1163cb1313d47dc7eeb18d0
- consensus rejects: https://explorer-studio.genlayer.com/tx/0xdab3ff727e806eda7b716290eececea0def16f2b5fd846cb1f29a89d21c86dfb
- sponsor refund: https://explorer-studio.genlayer.com/tx/0x794aabd5d29b0391503a969108342b96a350e654bcea8d9ad2831810d94f05dc

## Frontend product

The production Next.js app includes:

- live on-chain agreement discovery;
- sponsor / contractor / settlement workspaces;
- native GEN escrow creation;
- evidence preflight validation;
- validator-consensus resolution;
- role-aware payout and refund controls;
- on-chain policy and lifecycle timestamps;
- finalized transaction activity with Explorer links;
- a walletless reviewer benchmark;
- a **12-check live integrity gate** covering both PAID and REFUNDED outcomes.

## Automated quality gates

CI verifies:

- **16 direct contract tests**;
- adversarial validator disagreement;
- low-confidence approval denial;
- authorization and source-domain guards;
- retry cap and job indexing;
- strict mock matching;
- stored-state pickling/serialization;
- GenVM lint and validation;
- Next.js production build.

The live workflow separately deploys a fresh contract on Studionet and executes both economic outcomes end to end.

## Reviewer map

- Contract: `contracts/proof_judge.py`
- Direct tests: `tests/direct/test_proof_judge.py`
- Live integration: `tests/integration/test_studionet_smoke.py`
- Browser client: `frontend/lib/genlayer.ts`
- Machine-readable proof: `frontend/public/verified-demo.json`
- Steward walkthrough: `docs/STEWARD_VERIFICATION.md`
- Review quality mapping: `docs/QUALITY_BAR.md`
- Architecture: `docs/ARCHITECTURE.md`
- Security and failure modes: `docs/SECURITY.md`
- Product readiness: `docs/PRODUCT_READINESS.md`

ProofJudge is a working Studionet prototype and not a production financial or legal arbitration service. Portal scoring remains a steward decision.
