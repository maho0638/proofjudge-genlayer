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
- confidence values within a 15-point tolerance;
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

Current policy: `PJ_V3_MINCONF70`.

## Verified adverse path

The live Studionet workflow intentionally submitted irrelevant evidence. Consensus rejected it at 2/100 with `EVIDENCE_GAP`; contractor payout did not open; after deadline the sponsor recovered escrow.

Workflow:
https://github.com/maho0638/proofjudge-genlayer/actions/runs/35985412296

ProofJudge remains a Studionet prototype, not legal arbitration or a production financial service.
