# ProofJudge — Reviewer Quality Mapping

| Review dimension | Implementation | Verifiable evidence |
| --- | --- | --- |
| Clear real use case | Bilateral milestone acceptance and payment without one centralized reviewer. | Sponsor/contractor UI + native GEN escrow. |
| GenLayer is central | Live public evidence and natural-language criteria are adjudicated inside the Intelligent Contract. | `_evaluate`, `gl.nondet.web.render`, `gl.nondet.exec_prompt`. |
| Independent consensus | Validators independently re-fetch evidence; decision, reason, evidence basis and normalized snapshots must agree. | custom validator + dissent/mutation tests. |
| Economic consequence | Consensus decides whether contractor claim becomes possible. | canonical live PAID lifecycle. |
| Negative economic safety | Irrelevant evidence does not unlock contractor funds. | canonical REJECTED → REFUNDED lifecycle. |
| Confidence safety | Approval below 70/100 cannot become economically actionable. | normalization + claim guard + tests. |
| Source failure safety | Missing evidence cannot approve; contradictory evidence has an explicit failure path. | `SOURCE_UNAVAILABLE` / `CONTRADICTORY_EVIDENCE` tests. |
| Mutable URL protection | Normalized evidence actually judged by consensus is stored on-chain. | snapshot fields + mutation validator test. |
| Challenge path | Sponsor or assigned contractor can challenge one resolved result before settlement. | `challenge_resolution` / `resolve_challenge` + authorization tests. |
| Stalled-job recovery | Unresolved submitted/challenged work cannot lock escrow forever. | 24-hour post-deadline resolution grace + refund tests. |
| Precommitted rules | Requirement and rubric exist before evidence submission. | `create_job`. |
| Contractor accountability | Only assigned contractor submits and claims. | sender guards + tests. |
| Evidence independence | Two HTTPS sources from distinct hostnames are required. | submit guards + test. |
| Retry control | Rejected work may retry without unlimited consensus shopping. | maximum three attempts + test. |
| Refund control | Submitted evidence cannot be immediately bypassed by sponsor refund. | refund state/grace guards. |
| Transfer safety | Insufficient balance, unauthorized claim/refund, early refund and double claim fail. | direct tests. |
| Auditability | lifecycle timestamps, challenge state and V4 policy version are stored on-chain. | V4 Job state + UI. |
| Discovery | agreements are indexed on-chain. | `get_job_count`, `get_job_id`. |
| Reviewer proof | walletless UI reads both canonical outcomes live and does not substitute cached verdicts. | live integrity gate + consistency tests. |
| Deployment provenance | deploy input is repository source and post-deploy source is read back from Studionet. | workflow source hashes + `DEPLOYED_SOURCE_MATCH=true`. |
| Reproducibility | fresh network deployment proves positive and negative economic paths. | workflow 35993240108. |
| Engineering checks | 28 contract behavior tests, repository consistency checks, GenVM lint and exact prefix frontend build. | CI. |

## Canonical V4 proof

Contract:

`0x76D61aAec5bD4625346858acCd6dAb39966c4247`

Workflow:

https://github.com/maho0638/proofjudge-genlayer/actions/runs/35993240108

Paid:

`proofjudge-production-milestone-v4 · PAID · 100/100 · CROSS_CHECK · INDEPENDENT_CORROBORATION`

Rejected/refunded:

`irrelevant-evidence-refund-v1 · REJECTED · 95/100 rejection confidence · EVIDENCE_GAP → REFUNDED`

Deployed source:

`0cba1187b5478d885f8c150e1597298d4bc550b7552a01862c43eaeaa4f79ca9`

Repository source:

`0cba1187b5478d885f8c150e1597298d4bc550b7552a01862c43eaeaa4f79ca9`

`DEPLOYED_SOURCE_MATCH=true`

This document maps product qualities to evidence. Portal scoring remains a steward decision.
