# ProofJudge — Project Quality Bar

| Review dimension | ProofJudge implementation | Verifiable proof |
| --- | --- | --- |
| Real trust problem | A sponsor and contractor need objective settlement infrastructure for subjective deliverables without trusting one platform operator. | Native GEN is escrowed and claimability is contract-controlled. |
| GenLayer is central | Removing GenLayer removes the live evidence judge that authorizes payment. | `resolve_job` uses live web retrieval, LLM evaluation and validator re-execution before state changes. |
| Economic consequence | Consensus approval changes who can withdraw value. | APPROVED → contractor claim; expired OPEN/REJECTED → sponsor refund. |
| Precommitted rules | Requirement and rubric are stored before evidence is submitted. | `create_job` state. |
| Independent evidence | Contractor must provide two HTTPS URLs from distinct hostnames. | `submit_evidence` guards + direct test. |
| Prompt-injection resistance | Fetched pages are explicitly untrusted; output is schema-bounded. | `_evaluate` prompt and structured fields. |
| Validator verification | Validators independently fetch and judge the same live sources. | custom `validator_fn`; exact approved/rejected agreement + confidence tolerance. |
| Contractor accountability | Only the assigned contractor may submit or claim. | sender guards + direct tests. |
| Retry path | Rejected evidence can be replaced before deadline without creating a new agreement. | REJECTED → SUBMITTED, max 3 attempts. |
| Refund safety | Sponsor cannot bypass unresolved submitted work. | `refund_expired` rejects SUBMITTED state. |
| On-chain discovery | Jobs can be enumerated without a pre-known ID. | `get_job_count`, `get_job_id`, production cards. |
| Reviewer-proof demo | Canonical live settlement loads without wallet and self-checks against a pinned benchmark. | 8/8 integrity gate + Explorer lifecycle. |
| Complete application | Sponsor, contractor and settlement actions exist in the production UI. | Next.js frontend + GenLayerJS writes/reads. |
| Reproducibility | Direct tests, lint, build and a fresh live Studionet lifecycle are automated. | CI + run 35925077495. |

## Verified benchmark

- Contract: `0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc`
- Workflow: https://github.com/maho0638/proofjudge-genlayer/actions/runs/35925077495
- Job: `example-domain-milestone-v2`
- Status: `PAID`
- Confidence: `97/100`
- Reason: `CROSS_CHECK`
- Reward claimed: `true`

This mapping is a reviewer aid, not a guarantee of a specific Portal point award.
