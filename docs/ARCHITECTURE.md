# ProofJudge — Architecture

```
Sponsor wallet
   |
   | create_job + native GEN
   v
ProofJudge Intelligent Contract
   |
   | stores contractor + requirement + rubric + deadline + escrow
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
   +--> validator re-execution
   |
   v
APPROVED / REJECTED
   |
   +--> APPROVED: assigned contractor claim_payment
   +--> REJECTED: retry before deadline
   +--> expired OPEN/REJECTED: sponsor refund_expired
```

## State model

`OPEN → SUBMITTED → APPROVED → PAID`

`SUBMITTED → REJECTED → SUBMITTED` while attempts remain and deadline has not passed.

`OPEN/REJECTED → REFUNDED` only after deadline.

A SUBMITTED agreement cannot be refunded because unresolved evidence must not be bypassed.

## Frontend boundary

The frontend does not decide settlement. It validates inputs, submits contract calls, waits for finalized successful execution and reads contract state. The reviewer proof section reads the canonical Studionet job directly without requesting a wallet.
