# ProofJudge — Reviewer Quality Mapping

| Review dimension | Implementation | Verifiable evidence |
| --- | --- | --- |
| Clear real use case | Bilateral milestone acceptance and payment without one centralized reviewer. | Production sponsor/contractor UI and native GEN escrow. |
| GenLayer is central | Live public evidence and natural-language criteria are adjudicated inside the Intelligent Contract. | `_evaluate`, `gl.nondet.web.render`, `gl.nondet.exec_prompt`. |
| Independent consensus | Validators independently re-fetch evidence; exact reason, evidence basis and normalized snapshots must match. | custom validator + dissent + mutation tests. |
| Economic consequence | Consensus decides whether contractor claim becomes possible. | live PAID lifecycle. |
| Negative economic safety | Irrelevant evidence does not unlock funds. | live REJECTED → REFUNDED lifecycle. |
| Confidence safety | Approval below 70/100 cannot become economically actionable. | normalization + claim guard + direct test. |
| Source failure safety | Missing evidence cannot approve and contradictory evidence has an explicit failure path. | `SOURCE_UNAVAILABLE` / `CONTRADICTORY_EVIDENCE` tests. |
| Mutable URL protection | The exact normalized evidence text judged by consensus is stored on-chain. | snapshot fields + mutation validator test. |
| Challenge path | Either economic party can challenge one resolved result before settlement. | `challenge_resolution` / `resolve_challenge` + authorization tests. |
| Stalled-job recovery | Unresolved submitted/challenged work cannot lock escrow forever. | 24-hour resolution grace + refund tests. |
| Precommitted rules | Requirement and rubric exist before submission. | `create_job`. |
| Contractor accountability | Only assigned contractor submits and claims. | sender guards + tests. |
| Evidence independence | Two HTTPS sources from distinct hostnames are required. | submit guards + test. |
| Retry control | Rejected work can retry without unlimited consensus shopping. | maximum three attempts + test. |
| Refund control | Submitted evidence cannot be bypassed by sponsor refund. | refund state guard. |
| Accidental lock protection | zero-address contractor and >365-day deadlines are rejected. | contract guards + tests. |
| Auditability | lifecycle timestamps and policy version are stored on-chain. | v3 Job state + UI. |
| Discovery | agreements are indexed on-chain. | `get_job_count`, `get_job_id`. |
| Reviewer proof | walletless app reads both canonical outcomes live. | live integrity gate. |
| Reproducibility | fresh network deployment proves positive and negative paths. | workflow 35985412296. |
| Engineering checks | direct tests, strict mocks, pickling, lint, production build. | CI. |

## Canonical proof

Contract:
`0x699f62FA0f53B92D85949B1F046f6B50209707eE`

Workflow:
https://github.com/maho0638/proofjudge-genlayer/actions/runs/35985412296

Paid:
`proofjudge-production-milestone-v4 · PAID · 98/100 · CROSS_CHECK`

Rejected/refunded:
`irrelevant-evidence-refund-v1 · EVIDENCE_GAP · 2/100 · REFUNDED`

This document maps product qualities to evidence. It is not a promise of a particular Portal score.
