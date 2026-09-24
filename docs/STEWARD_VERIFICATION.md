# Steward Verification — ProofJudge V4

This is the shortest reviewer path. No wallet is required to verify the canonical live evidence.

## 1. Open the production app

https://proofjudge-genlayer-frontend.vercel.app

Open **Reviewer Fast Track** and **Verified Live Proof**.

Canonical Studionet contract:

`0x76D61aAec5bD4625346858acCd6dAb39966c4247`

Explorer:

https://explorer-studio.genlayer.com/address/0x76D61aAec5bD4625346858acCd6dAb39966c4247

The reviewer panel reads both canonical outcomes directly from this contract. If live RPC reads fail, ProofJudge clears the live result instead of substituting a cached verdict.

## 2. Verify the paid path

Job:

`proofjudge-production-milestone-v4`

Expected live state:

- final status: `PAID`
- approval confidence: `100/100`
- reason: `CROSS_CHECK`
- evidence basis: `INDEPENDENT_CORROBORATION`
- reward claimed: `true`
- policy: `PJ_V4_SNAPSHOT_CHALLENGE`
- primary/support evidence snapshots: present on-chain

Transactions:

1. create native GEN escrow  
   https://explorer-studio.genlayer.com/tx/0x837404d9b4d0b68fdb62fabe7f5e3149cd63d8a60bb3c7bf237cb1c41dada4a5
2. submit independent evidence  
   https://explorer-studio.genlayer.com/tx/0x142aa651083f34586dda375a390e18a78d82c47a51b639fe056de1e9da0bd23e
3. resolve by validator consensus  
   https://explorer-studio.genlayer.com/tx/0x18ecf17cdfea62dba009b76900dc928e1e068b2f3a27880dc9b98774decf8c9b
4. contractor claims payment  
   https://explorer-studio.genlayer.com/tx/0x47948c1f269f7aeb6386a57e6a85063b3c110b082965c9292d9c359799884e78

## 3. Verify the rejected + refunded path

Job:

`irrelevant-evidence-refund-v1`

The submitted pages were intentionally irrelevant to the committed ProofJudge milestone.

Expected decision/final state:

- consensus decision: `REJECTED`
- rejection confidence: `95/100`
- reason: `EVIDENCE_GAP`
- contractor payout never opens
- final status after deadline: `REFUNDED`
- escrow settled back to sponsor

Transactions:

1. create native GEN escrow  
   https://explorer-studio.genlayer.com/tx/0xed33290bff46f59aa60e9ecedd01075ad3ee7e0fa89db60bfaee7a2d0bb368ac
2. submit irrelevant evidence  
   https://explorer-studio.genlayer.com/tx/0x22a31fe953b3de027ae57bd38fff6d9bcd1afe823f0dc5c4f3d5722177d4720d
3. consensus rejects  
   https://explorer-studio.genlayer.com/tx/0x7f4d829bc8f1524a31262e8df7dc8e8b290989c9bf06a9f947a8eaa810eb3a32
4. sponsor refund  
   https://explorer-studio.genlayer.com/tx/0x99573fc7dc9d079ad7b3335a466339e452514c4d42a98df5930f8f8961562e49

This proves both economic directions: valid work can unlock contractor payment, while bad evidence cannot unlock contractor funds and the sponsor can recover expired escrow.

## 4. Reproduce the fresh deployment

Successful workflow:

https://github.com/maho0638/proofjudge-genlayer/actions/runs/35993240108

The workflow deploys a fresh V4 Intelligent Contract and executes both paths. It reports:

- `PROOFJUDGE_DEPLOY_INPUT_MATCH=true`
- deploy-input SHA-256: `9d523f2014dd502fc696f58d9ddfd832d856f2c2a55885e7fde2672a546a850b`
- deployed normalized SHA-256: `0cba1187b5478d885f8c150e1597298d4bc550b7552a01862c43eaeaa4f79ca9`
- repository normalized SHA-256: `0cba1187b5478d885f8c150e1597298d4bc550b7552a01862c43eaeaa4f79ca9`
- `DEPLOYED_SOURCE_MATCH=true`

The post-deploy check reads the source back from Studionet and compares it with `contracts/proof_judge.py`.

## 5. Inspect steward-requested hardening

- contract: `contracts/proof_judge.py`
- direct/adversarial tests: `tests/direct/test_proof_judge.py`
- repository consistency tests: `tests/direct/test_repo_consistency.py`
- live integration: `tests/integration/test_studionet_smoke.py`
- browser client: `frontend/lib/genlayer.ts`
- canonical machine proof: `frontend/public/verified-demo.json`
- remediation map: `docs/STEWARD_REMEDIATION.md`
- security model: `docs/SECURITY.md`

V4 stores bounded evidence snapshots, requires exact validator agreement on reason/evidence basis/snapshots, fails closed on unavailable evidence, models contradictory evidence explicitly, supports one challenge by either economic party, blocks claim while challenged, and provides stalled-resolution refund recovery after a 24-hour grace period.
