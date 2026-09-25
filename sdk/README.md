# @proofjudge/sdk

Reusable TypeScript helpers for ProofJudge V5. The SDK does not own a wallet: it exposes read helpers, settlement auditing, and GenLayer write-request builders so dApps and agents can use their own signing stack.

Core reads: `getJob`, `getProjectProgress`, `listProject`, `getParticipantStats`, `isMilestoneUnlocked`.

Core write builders: create milestone, submit evidence, resolve, challenge, claim, refund.
