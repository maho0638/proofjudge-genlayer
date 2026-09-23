# ProofJudge — Security and Failure Modes

## Funds safety

- A positive native GEN escrow is required when an agreement is created.
- Sponsor and contractor must be different wallets.
- Only the assigned contractor can claim an APPROVED agreement.
- Claim state is set before the external value transfer.
- Payment is single-use.
- Refund is sponsor-only and deadline-gated.
- SUBMITTED evidence cannot be bypassed by refund; it must first be resolved.
- Contract balance is checked before payout or refund.

## Evidence integrity

- Both evidence URLs must use HTTPS.
- Primary and supporting URLs must be different.
- Their normalized hostnames must be different.
- Evidence is fetched at resolution time rather than accepted as client-supplied page text.
- The requirement and rubric are committed before evidence submission.

Distinct hostnames are an anti-duplication boundary, not a claim that two websites are always organizationally independent. Source authority and corroboration are part of the live judgment.

## Prompt-injection resistance

Web content is explicitly marked as untrusted evidence. The model is instructed not to follow instructions inside fetched pages and not to use outside knowledge. Output is restricted to:

- `approved`: boolean
- `confidence`: integer 0–100
- `reason_code`: one allowed category

Unconstrained model prose does not control payout.

## Consensus integrity

The validator independently repeats the same evidence retrieval and evaluation. Acceptance requires:

- exact agreement on approved/rejected;
- bounded confidence difference of at most 15;
- both reason codes to be valid schema values.

Reason-code equality is intentionally not required because the label is explanatory metadata; payout safety is tied to the exact approved/rejected decision.

## Retry policy

A rejected contractor may replace evidence before the deadline. Attempts are capped at three. This supports legitimate iteration while preventing unlimited consensus retries.

## Known trade-offs

Public webpages can change, disappear or become inaccessible. ProofJudge therefore records stable URLs and the on-chain result, but it does not claim to permanently snapshot web content. It is a Studionet prototype and not legal arbitration or a production financial service.
