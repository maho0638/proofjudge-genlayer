# ProofJudge — Steward Remediation Map (V4)

This document maps every requested review item to a concrete implementation and reviewer-verifiable proof. The canonical successful Studionet contract is `0x76D61aAec5bD4625346858acCd6dAb39966c4247` and the canonical verification workflow is https://github.com/maho0638/proofjudge-genlayer/actions/runs/35993240108. The same values and transaction hashes are mirrored in `frontend/public/verified-demo.json` and `docs/STEWARD_VERIFICATION.md`.

## 1. One canonical deployed contract

All reviewer-facing surfaces are required by tests to use one canonical contract address:

- `frontend/lib/genlayer.ts`
- `frontend/public/verified-demo.json`
- README
- submission dossier
- steward guide
- quality mapping

`tests/direct/test_repo_consistency.py` rejects the two addresses cited in the original steward request plus superseded interim deployments, and enforces one canonical contract/workflow across reviewer-facing surfaces.

## 2. Exact deployment-source provenance

The live integration constructs its factory with the explicit path:

`get_contract_factory(contract_file_path="proof_judge.py")` (resolved by gltest against the configured `contracts/` directory)

Before deployment it verifies the factory's `contract_code` is exactly the repository file (newline normalization only), prints `PROOFJUDGE_DEPLOY_INPUT_MATCH=true`, and records the SHA-256 digest of that exact source. The same factory instance is then deployed in that workflow, and the resulting contract address is printed beside the digest and lifecycle transaction hashes.

This matches the public `genlayer-test` implementation: `ContractFactory.from_file_path` loads that file into `contract_code`, and `deploy_contract_tx` passes `self.contract_code` directly to the GenLayer client deployment call.

The live workflow additionally reads the deployed source back from Studionet with `getContractCode` and compares it against `contracts/proof_judge.py`. The canonical run reports deployed and repository normalized SHA-256 `0cba1187b5478d885f8c150e1597298d4bc550b7552a01862c43eaeaa4f79ca9` and `DEPLOYED_SOURCE_MATCH=true`. The reviewer UI verifies its mirrored source against that same digest, while CI enforces the source mirror against the repository file.

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
4. Open the successful **Deploy & Verify Studionet** workflow (run 35993240108) and confirm `PROOFJUDGE_DEPLOY_INPUT_MATCH=true`, canonical address `0x76D61aAec5bD4625346858acCd6dAb39966c4247`, matching deployed/repository SHA-256, and `DEPLOYED_SOURCE_MATCH=true`.
5. Review `contracts/proof_judge.py`, `tests/direct/test_proof_judge.py`, and this remediation map.
