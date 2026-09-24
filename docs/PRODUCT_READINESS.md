# ProofJudge — Product Readiness

ProofJudge is a complete bilateral milestone-settlement prototype rather than a verdict widget.

## End-to-end product contract

1. Sponsor assigns a contractor.
2. Sponsor commits requirement, rubric and deadline.
3. Sponsor escrows native GEN.
4. Contractor submits primary + independent public evidence.
5. GenLayer fetches both sources live.
6. Leader proposes a bounded structured verdict.
7. Validators independently re-fetch and re-evaluate.
8. Consensus stores APPROVED or REJECTED.
9. Approval requires at least 70/100 confidence.
10. Rejected evidence may retry, capped at three attempts.
11. Approved contractor may claim.
12. Expired OPEN/REJECTED escrow may return to sponsor.
13. Lifecycle timestamps remain auditable on-chain.

## Completeness checklist

- [x] native GEN escrow
- [x] sponsor and assigned contractor roles
- [x] natural-language requirement
- [x] precommitted rubric
- [x] deadline and 365-day cap
- [x] zero-address protection
- [x] two HTTPS evidence sources
- [x] live public web retrieval inside contract
- [x] prompt-injection instruction boundary
- [x] structured verdict
- [x] 70/100 minimum approval confidence
- [x] fail-closed source outage behavior
- [x] independent validator re-execution
- [x] deterministic stored rationale
- [x] contractor-only claim
- [x] guarded sponsor refund
- [x] retry cap
- [x] on-chain agreement index
- [x] lifecycle audit timestamps
- [x] policy version
- [x] role-aware frontend actions
- [x] finalized transaction activity
- [x] walletless reviewer proof
- [x] live dual-outcome integrity gate
- [x] 16 direct tests
- [x] validator dissent test
- [x] strict mocks
- [x] storage pickling checks
- [x] GenVM lint/validation
- [x] Next.js production build
- [x] fresh Studionet PAID lifecycle
- [x] fresh Studionet REJECTED → REFUNDED lifecycle

## Canonical live proof

Contract:
`0x699f62FA0f53B92D85949B1F046f6B50209707eE`

Workflow:
https://github.com/maho0638/proofjudge-genlayer/actions/runs/35985412296

Paid production milestone:
`PAID · 98/100 · CROSS_CHECK`

Bad-evidence path:
`REJECTED · 2/100 · EVIDENCE_GAP → REFUNDED`

## Product boundary

ProofJudge is bilateral settlement for one assigned contractor. It intentionally does not perform multi-entrant winner selection.


## Steward-requested v4 hardening

- [x] Evidence mutation protection with normalized on-chain primary/support snapshots
- [x] Exact validator equality for reason code, evidence basis and snapshots
- [x] Explicit SOURCE_UNAVAILABLE and CONTRADICTORY_EVIDENCE failure paths
- [x] One-shot sponsor/contractor challenge with fresh consensus
- [x] Claim blocked while CHALLENGED
- [x] 24-hour resolution grace before stalled SUBMITTED/CHALLENGED refund
- [x] Insufficient-balance, unauthorized claim/refund, early refund and double-claim tests
- [x] Canonical frontend/docs/proof address consistency test
- [x] Explicit `npm --prefix frontend run build` CI gate
- [x] Post-deploy source equality attestation using GenLayer `getContractCode`
- [x] Reviewer UI does not substitute cached verdicts when live RPC fails
