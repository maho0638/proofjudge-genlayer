# Steward Verification — ProofJudge

ProofJudge is a GenLayer-native milestone escrow. The fastest verification path does not require a wallet.

## 1. Open the production app

https://proofjudge-genlayer-frontend.vercel.app

Scroll to **Verified Live Proof**. The page should read job `example-domain-milestone-v2` directly from the deployed Studionet Intelligent Contract.

Expected live state:

- contract: `0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc`
- status: `PAID`
- confidence: `97/100`
- reason code: `CROSS_CHECK`
- reward claimed: `true`
- attempt count: `1`
- primary evidence host: `example.com`
- independent support host: `iana.org`

The reviewer integrity gate should show **8/8 live checks match — PASS** when the public Studionet RPC is available.

If RPC access is temporarily unavailable, the UI clearly labels the pinned benchmark as a fallback and does not call cached data live.

## 2. Verify the economic lifecycle

Contract:
https://explorer-studio.genlayer.com/address/0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc

Create native GEN escrow:
https://explorer-studio.genlayer.com/tx/0x0b42a662a7e9f6da6b09ff5fdb49f593781ba28f6bb508d3b70a18936a0838c6

Assigned contractor submits two independent evidence URLs:
https://explorer-studio.genlayer.com/tx/0x021ec1dc5c5afa5181c236b59a56b424b1e53953dd5459bcb9492165872db77d

Resolve by validator consensus:
https://explorer-studio.genlayer.com/tx/0x2621e4f4a2ecedb901c5e1ad25c975d4762e999918e37c6f56c70a255e7fb7db

Contractor claims the approved escrow:
https://explorer-studio.genlayer.com/tx/0x3d183cafb0ac32e5cd319f0059e53dce220982b0c4e8c43b5a58be044ce5e1dd

## 3. Reproduce a fresh lifecycle

Workflow:
https://github.com/maho0638/proofjudge-genlayer/actions/runs/35925077495

The integration test deploys a fresh contract and executes:

`deploy → create escrow → submit evidence → consensus resolve → contractor claim`

It asserts the live result is APPROVED with a valid structured reason, then asserts the post-claim job is PAID and `reward_claimed=true`.

## 4. Inspect settlement-critical source

- Contract: `contracts/proof_judge.py`
- Direct tests: `tests/direct/test_proof_judge.py`
- Live integration: `tests/integration/test_studionet_smoke.py`
- Browser client: `frontend/lib/genlayer.ts`
- Machine-readable proof: `frontend/public/verified-demo.json`

## 5. What GenLayer changes

The UI never submits an already-decided verdict. It submits the agreement and evidence references. The Intelligent Contract itself fetches the public evidence, evaluates the natural-language criteria, asks validators to independently repeat the evaluation, stores the accepted result and controls whether the contractor can claim escrowed GEN.
