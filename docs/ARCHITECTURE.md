# ProofJudge — Architecture

Canonical Studionet deployment:

`0x76D61aAec5bD4625346858acCd6dAb39966c4247`

```
Sponsor wallet
   |
   | create_job + native GEN
   v
ProofJudge Intelligent Contract
   |
   | stores contractor + requirement + rubric + deadline
   | stores policy PJ_V4_SNAPSHOT_CHALLENGE + lifecycle timestamps
   |
Contractor wallet
   |
   | submit_evidence(primary URL, independent support URL)
   v
ProofJudge Intelligent Contract
   |
   +--> gl.nondet.web.render(primary)
   +--> gl.nondet.web.render(support)
   +--> gl.nondet.exec_prompt(structured verdict)
   +--> custom validator re-fetch + re-evaluation
   +--> exact reason/evidence-basis/snapshot equivalence
   |
   v
APPROVED (confidence >= 70) / REJECTED
   |
   +--> APPROVED: challenge window or assigned contractor claim_payment -> PAID
   +--> REJECTED: challenge or retry before deadline (max 3)
   +--> CHALLENGED: permissionless resolve_challenge -> fresh consensus
   +--> expired OPEN/REJECTED: sponsor refund_expired -> REFUNDED
   +--> stalled SUBMITTED/CHALLENGED: 24h grace -> sponsor recovery
```

## State model

`OPEN → SUBMITTED → APPROVED → PAID`

`SUBMITTED → REJECTED → SUBMITTED` while attempts remain and deadline has not passed.

`APPROVED/REJECTED → CHALLENGED → APPROVED/REJECTED` through one party challenge and fresh consensus.

`OPEN/REJECTED → REFUNDED` after deadline.

`SUBMITTED/CHALLENGED → REFUNDED` only after the additional resolution grace period.

## Evidence integrity

V4 stores bounded normalized snapshots of the primary and support material accepted by consensus. Validators independently fetch both sources and require exact agreement on the decision, reason code, evidence basis and both snapshots, with confidence within a 10-point tolerance. A mutable URL that serves materially different content therefore fails equivalence instead of silently changing what the settlement means.

Missing evidence fails closed as `SOURCE_UNAVAILABLE`; materially conflicting evidence has an explicit `CONTRADICTORY_EVIDENCE` path.

## Consensus boundary

The client submits acceptance criteria and public evidence URLs, never a pre-decided verdict. The accepted decision is created and verified inside GenLayer. A low-confidence approval cannot unlock payment.

## Economic boundary

- positive native GEN is escrowed at creation;
- only the assigned contractor may submit or claim;
- only the sponsor may refund;
- payout requires APPROVED with confidence >= 70;
- challenged state blocks claim;
- transfers are single-use and balance checked;
- early refund, unauthorized payout/refund and double claim are covered by direct tests.

## Frontend boundary

The Next.js frontend:

- discovers jobs from the contract index;
- reads canonical PAID and REFUNDED proofs live without a wallet;
- never substitutes cached verdicts when RPC reads fail;
- validates obvious input errors before transactions;
- submits payable/writable calls through GenLayerJS;
- waits for FINALIZED + FINISHED_WITH_RETURN;
- exposes role-aware challenge, re-resolution, claim and refund controls;
- displays evidence snapshots, policy state and Explorer-verifiable transaction activity;
- derives canonical reviewer proof from `frontend/public/verified-demo.json`.

## Deployment provenance

Canonical workflow:

https://github.com/maho0638/proofjudge-genlayer/actions/runs/35993240108

After the fresh V4 lifecycle completes, the workflow reads the deployed contract source back from Studionet. Deployed and repository normalized SHA-256 are both:

`0cba1187b5478d885f8c150e1597298d4bc550b7552a01862c43eaeaa4f79ca9`

The workflow reports `DEPLOYED_SOURCE_MATCH=true`.
