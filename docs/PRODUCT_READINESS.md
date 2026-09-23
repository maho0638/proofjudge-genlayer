# ProofJudge — Product Readiness

ProofJudge is designed as a complete bilateral milestone-settlement application rather than an AI verdict demo.

## Product contract

1. Sponsor assigns one contractor and commits requirement, rubric and deadline.
2. Sponsor locks native GEN in the Intelligent Contract.
3. Contractor submits a primary public deliverable and independent supporting evidence.
4. GenLayer fetches both sources live.
5. The leader returns a bounded structured verdict.
6. Validators independently repeat the evidence review.
7. Consensus updates job state to APPROVED or REJECTED.
8. Rejected evidence can be replaced before deadline, up to three attempts.
9. APPROVED work becomes claimable only by the assigned contractor.
10. Expired OPEN/REJECTED work can be refunded only to the sponsor.
11. SUBMITTED evidence must be resolved before funds can move.

## Product completeness checklist

- [x] Native GEN escrow
- [x] Assigned contractor
- [x] Natural-language requirement
- [x] Precommitted judging rubric
- [x] Deadline
- [x] Two independent HTTPS evidence hosts
- [x] Live web retrieval inside the Intelligent Contract
- [x] Structured approved/rejected verdict
- [x] Confidence score
- [x] Structured reason metadata
- [x] Independent validator re-execution
- [x] Deterministic stored rationale
- [x] Contractor-only claim
- [x] Guarded sponsor refund
- [x] Retry path capped at three attempts
- [x] On-chain agreement index
- [x] Full sponsor / contractor / settlement frontend
- [x] Client-side preflight validation
- [x] Read-only reviewer benchmark requiring no wallet
- [x] Honest RPC failure fallback
- [x] Reviewer integrity gate
- [x] Direct Explorer lifecycle proof
- [x] 9 direct contract tests
- [x] GenVM lint
- [x] Next.js production build
- [x] Fresh live Studionet integration lifecycle

## Verified live lifecycle

Contract: `0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc`

Workflow:
https://github.com/maho0638/proofjudge-genlayer/actions/runs/35925077495

Canonical job: `example-domain-milestone-v2`

Result: `PAID · 97/100 · CROSS_CHECK · reward_claimed=true`

## Product boundary

ProofJudge is intentionally bilateral. It does not select a winner among competing researchers; that is the distinct ResearchArena product. ProofJudge's purpose is acceptance and economic settlement of one assigned contractor's milestone.
