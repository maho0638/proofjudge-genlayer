# ProofJudge — AI Evidence Verification on GenLayer

[![CI](https://github.com/maho0638/proofjudge-genlayer/actions/workflows/ci.yml/badge.svg)](https://github.com/maho0638/proofjudge-genlayer/actions/workflows/ci.yml)

ProofJudge is a GenLayer-native application for reviewing bounty submissions, freelance deliverables, grant milestones, and community tasks using real web evidence plus validator consensus.

## Why GenLayer is central

Traditional smart contracts cannot open an arbitrary evidence URL, understand a natural-language requirement, and decide whether the submitted work satisfies it. ProofJudge uses a GenLayer Intelligent Contract to:

1. store a human-readable requirement and evidence URL,
2. fetch the live evidence with `gl.nondet.web.render`,
3. ask an LLM for a structured verdict,
4. reach validator consensus through GenLayer's equivalence principle,
5. store the final verdict, confidence and rationale on-chain.

This maps directly to real bounty review, milestone verification and performance-based contracting.

## Project status

MVP source is included:
- GenLayer Intelligent Contract
- direct-mode tests with deterministic web/LLM mocks
- deployment script
- browser frontend for submit / resolve / read flows
- environment template and local setup

## Architecture

```
User
  |
  v
Next.js frontend
  |
  v
GenLayerJS
  |
  v
ProofJudge Intelligent Contract
  |        |
  |        +--> LLM structured evaluation
  +------------> Live evidence URL
                   |
                   v
            GenLayer consensus
                   |
                   v
       approved / rejected + reason
```

## Contract workflow

### 1. Submit a review

`submit_review(review_id, requirement, evidence_url)`

The sender creates an immutable review request.

### 2. Resolve

`resolve_review(review_id)`

The contract fetches the evidence, asks the LLM to evaluate it against the requirement, and finalizes a consensus-backed verdict.

### 3. Read

`get_review(review_id)` and `get_reviews()`

The frontend can render all review results and their stored rationale.

## Quick start

### Requirements

- Python 3.12+
- Node.js 18+
- GenLayer CLI
- GenLayer Studio or Studionet

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
```

### Lint the contract

```bash
genvm-lint check contracts/proof_judge.py
```

### Run direct tests

```bash
pytest tests/direct -v
```

### Deploy

```bash
npm run deploy
```

Copy the deployed address into `frontend/.env.local` using the template in `frontend/.env.example`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000.

## Example use cases

- **Bounty review** — verify whether a GitHub PR, article, design, or demo meets a task brief.
- **Freelance milestones** — compare a delivered URL with agreed acceptance criteria.
- **Grant verification** — evaluate milestone evidence before releasing the next stage.
- **Community rewards** — turn subjective contribution review into a transparent consensus workflow.

## Safety and limitations

ProofJudge does not treat an LLM as a single trusted oracle. The contract is designed around GenLayer's validator execution model and stores a structured verdict after consensus.

The MVP evaluates public URLs only. Future versions can add:
- multiple evidence URLs,
- challenge / appeal rounds,
- escrow and payout,
- reviewer reputation,
- specialized verdict schemas,
- content hashes and evidence snapshots.

## Built for GenLayer

This project intentionally uses GenLayer features that ordinary deterministic smart contracts cannot provide: live web access, natural-language evaluation and consensus over non-deterministic computation.
