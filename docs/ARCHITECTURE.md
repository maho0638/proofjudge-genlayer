# ProofJudge — Architecture

```
Sponsor wallet
   |
   | create_job + native GEN
   v
ProofJudge Intelligent Contract
   |
   | stores contractor + requirement + rubric + deadline
   | stores policy PJ_V3_MINCONF70 + audit timestamps
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
   |
   v
APPROVED (confidence >= 70) / REJECTED
   |
   +--> APPROVED: assigned contractor claim_payment -> PAID
   +--> REJECTED: retry before deadline (max 3)
   +--> expired OPEN/REJECTED: sponsor refund_expired -> REFUNDED
```

## State model

`OPEN → SUBMITTED → APPROVED → PAID`

`SUBMITTED → REJECTED → SUBMITTED` while attempts remain and deadline has not passed.

`OPEN/REJECTED → REFUNDED` only after deadline.

A SUBMITTED agreement cannot be refunded because unresolved evidence must first receive a consensus outcome.

## Consensus boundary

The client submits criteria and URLs, not a verdict. The accepted decision is created and verified inside GenLayer. A low-confidence approval cannot unlock payment.

## Frontend boundary

The Next.js frontend:

- discovers jobs from the contract index;
- reads the canonical PAID and REFUNDED proofs without a wallet;
- validates obvious input errors before transactions;
- submits writes through GenLayerJS;
- waits for FINALIZED + FINISHED_WITH_RETURN;
- displays role-aware controls and Explorer-verifiable transaction activity.

The frontend never substitutes its own acceptance decision for contract consensus.
