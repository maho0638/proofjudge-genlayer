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

The validator does not merely validate JSON shape. It independently re-fetches the evidence and repeats the judgment. V4 additionally requires exact equality for the reason code, evidence basis and normalized evidence snapshots; changed web content therefore fails validator equivalence instead of silently inheriting the leader's decision. This follows GenLayer's current Equivalence Principle guidance: https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle

## V4 settlement policy

The current contract hardens the economic decision:

- approvals require at least **70/100 confidence**;
- low-confidence “yes” responses are normalized to rejection and cannot unlock GEN;
- evidence-fetch failures become `SOURCE_UNAVAILABLE`, never an approval;
- positive and failure reason codes are semantically constrained;
- a zero-address contractor is rejected;
- agreement deadlines cannot exceed 365 days;
- rejected evidence may be retried, but attempts are capped at three;
- leader and validators must match the exact decision reason, evidence basis and normalized evidence snapshots;
- normalized primary/support snapshots are stored on-chain so later URL changes cannot rewrite what was judged;
- missing sources fail closed as `SOURCE_UNAVAILABLE`, while material contradictions use `CONTRADICTORY_EVIDENCE`;
- sponsor or contractor may challenge one resolved decision and force fresh consensus before settlement;
- submitted/challenged work cannot be immediately bypassed by refund; a 24-hour post-deadline resolution grace prevents permanent lock;
- creation, submission, resolution, challenge and settlement timestamps are stored on-chain;
- every job records `policy_version = PJ_V4_SNAPSHOT_CHALLENGE`.

## Product lifecycle

1. **Create** — sponsor selects a contractor, commits requirement/rubric/deadline and locks native GEN.
2. **Submit** — assigned contractor supplies two HTTPS evidence URLs from distinct hostnames.
3. **Resolve** — the Intelligent Contract fetches both sources; leader and validators independently judge the precommitted criteria.
4. **Approve or reject** — accepted consensus stores a bounded confidence score and structured reason.
5. **Claim** — only an APPROVED contractor with confidence ≥70 can claim.
6. **Retry** — rejected work may replace evidence before the deadline, up to three attempts.
7. **Refund** — expired OPEN or REJECTED work can be refunded only by the sponsor.

## Verified Studionet v4

- **Network:** GenLayer Studionet
- **Chain ID:** 61999
- **Contract:** `0x76D61aAec5bD4625346858acCd6dAb39966c4247`
- **Explorer:** https://explorer-studio.genlayer.com/address/0x76D61aAec5bD4625346858acCd6dAb39966c4247
- **Successful full live workflow:** https://github.com/maho0638/proofjudge-genlayer/actions/runs/35993240108

### Outcome A — real production milestone → PAID

Job: `proofjudge-production-milestone-v4`

The primary evidence was the real ProofJudge production deployment and the independent support was the public repository README.

- production evidence: https://proofjudge-genlayer-frontend.vercel.app
- independent support: https://raw.githubusercontent.com/maho0638/proofjudge-genlayer/main/README.md
- decision: `APPROVED`
- confidence: `100/100`
- reason: `CROSS_CHECK`
- final state: `PAID`
- contractor reward claimed: `true`

Transactions:

- create escrow: https://explorer-studio.genlayer.com/tx/0x837404d9b4d0b68fdb62fabe7f5e3149cd63d8a60bb3c7bf237cb1c41dada4a5
- submit evidence: https://explorer-studio.genlayer.com/tx/0x142aa651083f34586dda375a390e18a78d82c47a51b639fe056de1e9da0bd23e
- resolve consensus: https://explorer-studio.genlayer.com/tx/0x18ecf17cdfea62dba009b76900dc928e1e068b2f3a27880dc9b98774decf8c9b
- claim payment: https://explorer-studio.genlayer.com/tx/0x47948c1f269f7aeb6386a57e6a85063b3c110b082965c9292d9c359799884e78

### Outcome B — irrelevant evidence → REJECTED → REFUNDED

Job: `irrelevant-evidence-refund-v1`

The submitted pages were intentionally unrelated to the committed ProofJudge milestone.

- consensus decision: `REJECTED`
- rejection confidence: `95/100`
- reason: `EVIDENCE_GAP`
- contractor payout never opened
- after deadline the sponsor recovered escrow
- final state: `REFUNDED`

Transactions:

- create escrow: https://explorer-studio.genlayer.com/tx/0xed33290bff46f59aa60e9ecedd01075ad3ee7e0fa89db60bfaee7a2d0bb368ac
- submit irrelevant evidence: https://explorer-studio.genlayer.com/tx/0x22a31fe953b3de027ae57bd38fff6d9bcd1afe823f0dc5c4f3d5722177d4720d
- consensus rejects: https://explorer-studio.genlayer.com/tx/0x7f4d829bc8f1524a31262e8df7dc8e8b290989c9bf06a9f947a8eaa810eb3a32
- sponsor refund: https://explorer-studio.genlayer.com/tx/0x99573fc7dc9d079ad7b3335a466339e452514c4d42a98df5930f8f8961562e49

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
- a walletless reviewer benchmark with no cached-verdict fallback;
- deployment-source provenance checking via the exact source passed to the GenLayer test deployer;
- on-chain evidence snapshots and challenge state;
- a **live integrity gate** covering contract address, deployed source and both PAID/REFUNDED outcomes.

## Automated quality gates

CI verifies:

- **expanded direct and repository-safety tests**;
- adversarial validator disagreement;
- low-confidence approval denial;
- authorization and source-domain guards;
- retry cap and job indexing;
- strict mock matching;
- stored-state pickling/serialization;
- GenVM lint and validation;
- Next.js production build.

The live workflow separately deploys a fresh contract on Studionet, executes both economic outcomes end to end, and then reads the deployed source back from Studionet to prove it matches `contracts/proof_judge.py`.

## Deployed-source attestation

The canonical successful workflow reports:

- deploy-input SHA-256: `9d523f2014dd502fc696f58d9ddfd832d856f2c2a55885e7fde2672a546a850b`
- deployed normalized SHA-256: `0cba1187b5478d885f8c150e1597298d4bc550b7552a01862c43eaeaa4f79ca9`
- repository normalized SHA-256: `0cba1187b5478d885f8c150e1597298d4bc550b7552a01862c43eaeaa4f79ca9`
- `DEPLOYED_SOURCE_MATCH=true`

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


## V5 milestone release candidate — composable project settlement

The accepted V4 product settles one bilateral milestone safely. V5 expands ProofJudge into reusable project infrastructure:

- ordered multi-milestone project chains with on-chain dependencies;
- later stages locked until the previous milestone is actually `PAID`;
- bounded project progress views and neutral participant settlement statistics;
- a reusable TypeScript SDK for dApps and agents;
- a dedicated developer integration surface;
- a separate Studionet workflow proving a two-stage project end to end before V5 becomes canonical.

See [docs/MILESTONE_V5.md](docs/MILESTONE_V5.md) and [sdk/](sdk/).

V4 remains the canonical production contract until V5 live verification and deployed-source equality pass.
