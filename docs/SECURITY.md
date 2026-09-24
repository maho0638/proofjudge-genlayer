# ProofJudge — Security and Failure Modes

## Funds safety

- positive native GEN escrow is required;
- sponsor and contractor must be different;
- zero-address contractor is rejected;
- only assigned contractor can submit or claim;
- only sponsor can refund;
- claim requires APPROVED state **and confidence ≥70**;
- state is marked settled before external transfer;
- payout/refund is single-use;
- SUBMITTED evidence cannot be bypassed by refund;
- contract balance is checked before transfers;
- deadlines are capped at 365 days.

## Consensus safety

The leader returns only:

- `approved`
- `confidence` from 0–100
- one structured reason code.

Validators independently repeat live retrieval and judgment.

Acceptance requires:

- exact agreement on approved/rejected;
- confidence values within a 10-point tolerance;
- semantically valid positive/failure reason families;
- both leader and validator confidence ≥70 for an approval.

A low-confidence “yes” is normalized to `REJECTED / EVIDENCE_GAP`.

## Source failure safety

If web rendering raises an exception, the verdict is:

`approved=false · confidence=100 · SOURCE_UNAVAILABLE`

A source outage therefore fails closed instead of unlocking funds.

## Prompt-injection resistance

Fetched pages are explicitly labeled untrusted evidence. The prompt instructs the model not to follow instructions contained in those pages and not to use outside knowledge. Free-form generated prose never controls payment.

## Evidence rules

- HTTPS only;
- URL length cap;
- primary and support URLs must differ;
- normalized hostnames must differ.

Distinct hostnames are an anti-duplication boundary, not a guarantee of organizational independence. The rubric and consensus judgment must still assess authority and corroboration.

## Retry policy

A rejected contractor may replace evidence before the deadline. Attempts are capped at three to prevent unlimited consensus shopping.

## Audit trail

Each agreement stores:

- `created_at`
- `submitted_at`
- `resolved_at`
- `settled_at`
- `policy_version`

Current policy: `PJ_V4_SNAPSHOT_CHALLENGE`.

## Verified adverse path

The canonical live Studionet workflow intentionally submitted irrelevant evidence. Consensus rejected it with 95/100 rejection confidence and `EVIDENCE_GAP`; contractor payout did not open; after deadline the sponsor recovered escrow.

Canonical contract:
`0x76D61aAec5bD4625346858acCd6dAb39966c4247`

Workflow:
https://github.com/maho0638/proofjudge-genlayer/actions/runs/35993240108

The same workflow reads the deployed contract source back from Studionet and proves `DEPLOYED_SOURCE_MATCH=true` against repository `contracts/proof_judge.py`.

ProofJudge remains a Studionet prototype, not legal arbitration or a production financial service.


## V4 evidence immutability and equivalence

During resolution, leader and validators independently render both public URLs and normalize bounded text snapshots. Consensus accepts only when the validator matches the leader on:

- approved/rejected state;
- exact reason code;
- exact evidence-basis code;
- exact primary evidence snapshot;
- exact support evidence snapshot;
- confidence within a 10-point tolerance.

The accepted snapshots are stored on-chain with the result. If a mutable URL serves different material to the validator, snapshot equality fails and the validator rejects the leader result.

Missing/empty rendered evidence fails closed as `SOURCE_UNAVAILABLE`. Materially conflicting evidence has the explicit `CONTRADICTORY_EVIDENCE` failure path.

## Challenge and stalled-resolution recovery

A sponsor or assigned contractor may challenge one APPROVED or REJECTED result. The agreement becomes `CHALLENGED`; claim is blocked until permissionless `resolve_challenge` performs fresh consensus.

To avoid permanent escrow lock when resolution cannot complete, SUBMITTED or CHALLENGED work receives a 24-hour grace period after the deadline. Only after that grace may the sponsor recover stalled escrow. OPEN/REJECTED expiry keeps the ordinary refund path.

## Transfer safety evidence

Before emitting a payout/refund, the contract verifies sufficient balance and marks settlement single-use. Direct tests prove insufficient balance cannot flip an APPROVED job to paid, unauthorized callers cannot claim/refund, early refunds fail, and repeated claims fail. The live Studionet workflow separately proves finalized native-GEN contractor claim and sponsor refund transactions.
