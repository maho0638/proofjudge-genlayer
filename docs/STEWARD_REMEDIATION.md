# ProofJudge — Steward Remediation Map (V4)

This document maps every requested review item to a concrete implementation and reviewer-verifiable proof. The final canonical Studionet address and transaction hashes are also mirrored in `frontend/public/verified-demo.json` and `docs/STEWARD_VERIFICATION.md`.

## 1. One canonical deployed contract

All reviewer-facing surfaces are required by tests to use one canonical contract address:

- `frontend/lib/genlayer.ts`
- `frontend/public/verified-demo.json`
- README
- submission dossier
- steward guide
- quality mapping

`tests/direct/test_repo_consistency.py` also rejects the two stale addresses cited in the steward request.

## 2. Deployed byte/source identity

The live deployment workflow captures the freshly deployed Studionet address and runs:

`node scripts/verify-deployed-source.mjs`

The script calls GenLayer `getContractCode` for that exact address and compares it, after newline normalization only, with `contracts/proof_judge.py`. A mismatch fails the workflow.

The production reviewer UI performs the same source comparison against `frontend/public/deployed-contract-source.txt`, whose exact equality with the repository contract is enforced by a direct repository test.

## 3. Live RPC only — no cached verdict presented as live proof

The production UI reads both canonical jobs directly from the configured Studionet contract.

If the RPC read fails:

- the verified jobs are cleared;
- no pinned/cached verdict is substituted;
- evidence links are withheld;
- the UI explicitly says live state is unavailable and points reviewers to Explorer / CI proof.

`test_frontend_never_presents_cached_verdict_as_live_state` enforces this behavior in CI.

## 4. “Lock GEN & create” is an explicit wallet transaction

The sponsor form uses an explicit `type="submit"` action. Submission:

1. validates job, contractor, rubric, reward and deadline;
2. requests the user's EIP-1193 wallet;
3. sends payable `create_job` with the native GEN value;
4. waits for `FINALIZED / FINISHED_WITH_RETURN`;
5. reports the finalized transaction in the UI.

The status area is an `aria-live` region so wallet or transaction failures are visible rather than appearing as a dead button.

## 5. Real escrow and settlement controls

The Intelligent Contract requires positive native GEN at creation and stores the reward with the agreement.

Economic guards include:

- sponsor and contractor must differ;
- zero-address contractor rejected;
- only assigned contractor submits and claims;
- only sponsor refunds;
- claim requires APPROVED + confidence >= 70;
- payout/refund are single-use;
- sufficient contract balance is checked;
- early refunds fail;
- stalled SUBMITTED / CHALLENGED jobs use a 24-hour post-deadline resolution grace;
- finalized Studionet PAID and REFUNDED paths are linked from the reviewer proof.

## 6. Frontend build reproducibility

CI runs the exact commands from repository root:

`npm --prefix frontend install`

`npm --prefix frontend run build`

A build failure blocks the PR.

## 7. Mutable evidence protection

V4 stores normalized bounded primary/support evidence snapshots with every accepted resolution.

Leader and validators independently fetch the public URLs. Consensus requires exact equality on:

- approved/rejected result;
- reason code;
- evidence-basis code;
- primary snapshot;
- support snapshot;

with confidence within a 10-point tolerance.

If a URL changes between leader and validator reads, snapshot equality fails.

## 8. Missing and contradictory evidence

Missing/empty render output fails closed as:

`SOURCE_UNAVAILABLE`

Materially conflicting evidence has the explicit:

`CONTRADICTORY_EVIDENCE`

reason and evidence-basis path.

## 9. Challenge / appeal path

Sponsor or assigned contractor can challenge one APPROVED or REJECTED decision with a written note.

The job becomes `CHALLENGED`, which blocks claim. `resolve_challenge` performs a fresh permissionless consensus evaluation. The UI exposes both challenge and re-resolution.

## 10. Requested edge-case coverage

The direct/repository test suite covers, among other cases:

- validator disagreement;
- evidence mutation between leader and validator;
- exact reason/evidence-basis equivalence;
- on-chain snapshot storage;
- contradictory evidence;
- low-confidence “yes” denial;
- maximum evidence attempts;
- one-shot challenge and authorization;
- claim blocked during challenge;
- submitted-job refund grace;
- stalled submitted-job recovery;
- early refund denial;
- unauthorized refund;
- unauthorized claim;
- insufficient contract balance;
- double claim;
- HTTPS and independent-host requirements;
- canonical frontend/docs/proof contract-address consistency;
- exact frontend source mirror;
- no cached-verdict fallback.

## Reviewer shortest path

1. Open the production app and inspect **Reviewer Fast Track** / **Verified Live Proof**.
2. Confirm the live integrity gate reports the configured contract and deployed-source match.
3. Open the canonical Explorer contract and finalized lifecycle transactions.
4. Open the successful **Deploy & Verify Studionet** workflow and confirm `DEPLOYED_SOURCE_MATCH=true`.
5. Review `contracts/proof_judge.py`, `tests/direct/test_proof_judge.py`, and this remediation map.
