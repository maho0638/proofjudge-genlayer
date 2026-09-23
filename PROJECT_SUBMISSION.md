# ProofJudge — Project Explorer Submission Dossier

## One-sentence summary

ProofJudge is a GenLayer-native milestone escrow where sponsors lock GEN, contractors submit live public evidence, and validator consensus determines whether the contractor can claim payment.

## Problem

Freelance milestones, grant stages, service deliverables and performance contracts often depend on subjective acceptance criteria. A deterministic smart contract can escrow funds but cannot open a live website and decide whether a delivered result actually satisfies a natural-language brief.

Centralized review solves the reasoning problem by reintroducing trust in one platform operator.

## GenLayer-native solution

ProofJudge makes GenLayer the adjudication and settlement layer:

- the sponsor locks native GEN and precommits the requirement and rubric;
- one assigned contractor submits a primary deliverable URL plus independent supporting evidence;
- the Intelligent Contract fetches both live sources at resolution time;
- a leader produces a structured approved/rejected verdict, confidence and reason code;
- validators independently repeat the web retrieval and judgment;
- the accepted result changes on-chain state;
- only APPROVED work can unlock the contractor's escrowed GEN.

Rejected work can be resubmitted before deadline, up to three attempts. Expired OPEN or REJECTED work has a guarded sponsor refund path, while unresolved SUBMITTED evidence cannot be bypassed.

## Live Studionet evidence

- Network: GenLayer Studionet
- Chain ID: 61999
- Contract: `0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc`
- Explorer: https://explorer-studio.genlayer.com/address/0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc
- Live app: https://proofjudge-genlayer-frontend.vercel.app
- Successful full lifecycle: https://github.com/maho0638/proofjudge-genlayer/actions/runs/35925077495

Verified job: `example-domain-milestone-v2`

Create escrow:
https://explorer-studio.genlayer.com/tx/0x0b42a662a7e9f6da6b09ff5fdb49f593781ba28f6bb508d3b70a18936a0838c6

Submit evidence:
https://explorer-studio.genlayer.com/tx/0x021ec1dc5c5afa5181c236b59a56b424b1e53953dd5459bcb9492165872db77d

Resolve by consensus:
https://explorer-studio.genlayer.com/tx/0x2621e4f4a2ecedb901c5e1ad25c975d4762e999918e37c6f56c70a255e7fb7db

Claim payment:
https://explorer-studio.genlayer.com/tx/0x3d183cafb0ac32e5cd319f0059e53dce220982b0c4e8c43b5a58be044ce5e1dd

Verified settlement:

- `status = PAID`
- `confidence = 97`
- `reason_code = CROSS_CHECK`
- `reward_claimed = true`
- rationale: `Approved because independent support corroborates the primary evidence. Confidence 97/100.`

## Product completeness

The production UI supports:

- wallet connection;
- sponsor creation with native GEN escrow;
- contractor assignment;
- natural-language acceptance requirement and rubric;
- two-source evidence submission with client-side HTTPS/domain checks;
- live on-chain job discovery;
- read-only reviewer benchmark requiring no wallet;
- consensus resolution;
- contractor payment claim;
- expired-work refund;
- retry visibility and attempt count;
- direct Explorer links for the canonical lifecycle;
- a reviewer integrity gate comparing live contract state against the pinned benchmark.

## Differentiation

ProofJudge is not ResearchArena.

ResearchArena is a multi-participant competitive research marketplace that selects one winning research submission. ProofJudge is a bilateral 1:1 performance contract: one sponsor, one assigned contractor, explicit acceptance criteria, retryable evidence and escrow release only after consensus approval.

## Reviewer verification

Start with:

- `docs/STEWARD_VERIFICATION.md`
- `docs/QUALITY_BAR.md`
- `docs/SECURITY.md`
- `docs/PRODUCT_READINESS.md`
- `frontend/public/verified-demo.json`

The repository also includes 9 direct contract tests, GenVM linting, production frontend build checks and a live Studionet integration workflow.
