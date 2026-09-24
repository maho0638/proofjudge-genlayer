# Steward Verification — ProofJudge v3

The fastest review path requires no wallet and takes only a few minutes.

## 1. Open the production app

https://proofjudge-genlayer-frontend.vercel.app

Scroll to **Verified Live Proof**.

The page reads two jobs directly from the deployed Studionet contract:

Contract:
`0x699f62FA0f53B92D85949B1F046f6B50209707eE`

Explorer:
https://explorer-studio.genlayer.com/address/0x699f62FA0f53B92D85949B1F046f6B50209707eE

The reviewer integrity gate should show **12/12 live checks match — PASS** when the public Studionet RPC is reachable.

## 2. Verify the paid path

Job: `proofjudge-production-milestone-v3`

Expected:

- status: `PAID`
- confidence: `98/100`
- reason: `CROSS_CHECK`
- reward claimed: `true`
- policy: `PJ_V3_MINCONF70`

Primary evidence:
https://proofjudge-genlayer-frontend.vercel.app

Independent support:
https://raw.githubusercontent.com/maho0638/proofjudge-genlayer/main/README.md

Transactions:

1. create escrow  
   https://explorer-studio.genlayer.com/tx/0xb9cdb9211b7775911b70e4af93b0408644c5d9ddafb0123d20fbcfc20dd62c9b
2. submit evidence  
   https://explorer-studio.genlayer.com/tx/0x82e871f6510cf5e8af66e778a7b879e4a19d04f01c717103862d43bd5c19eb6d
3. consensus resolution  
   https://explorer-studio.genlayer.com/tx/0x3fa02241eb60d23604ab3bde2d1eee9334794557f73af280f3ae3abdc2752bef
4. contractor claim  
   https://explorer-studio.genlayer.com/tx/0x8c98e573115a3a41a28456c59aa4eef1060ab1fdc713a69db74b50bd05d18013

## 3. Verify the rejection + refund path

Job: `irrelevant-evidence-refund-v1`

Expected decision:

- `REJECTED`
- confidence: `2/100`
- reason: `EVIDENCE_GAP`

Expected final state:

- `REFUNDED`
- escrow settled back to sponsor

Transactions:

1. create escrow  
   https://explorer-studio.genlayer.com/tx/0xd29492ee5f16e2d595b6792d17058c325ab0a9b4456cd7763eedfa2a01ebf637
2. submit irrelevant evidence  
   https://explorer-studio.genlayer.com/tx/0xa790bb59991bd38e6e211cebcccba62fe2ea3870d1163cb1313d47dc7eeb18d0
3. consensus rejects  
   https://explorer-studio.genlayer.com/tx/0xdab3ff727e806eda7b716290eececea0def16f2b5fd846cb1f29a89d21c86dfb
4. sponsor refund  
   https://explorer-studio.genlayer.com/tx/0x794aabd5d29b0391503a969108342b96a350e654bcea8d9ad2831810d94f05dc

This proves the system does not merely demonstrate payout. It also demonstrates that bad evidence fails to unlock contractor funds.

## 4. Reproduce both outcomes

Successful workflow:
https://github.com/maho0638/proofjudge-genlayer/actions/runs/35985412296

It deploys a fresh contract and executes both outcomes end to end.

## 5. Inspect settlement-critical source

- contract: `contracts/proof_judge.py`
- direct tests: `tests/direct/test_proof_judge.py`
- live integration: `tests/integration/test_studionet_smoke.py`
- browser client: `frontend/lib/genlayer.ts`
- machine-readable proof: `frontend/public/verified-demo.json`

The frontend never supplies a pre-decided verdict. The Intelligent Contract fetches evidence, obtains the proposed result, validators independently re-evaluate, and accepted consensus controls economic state.
