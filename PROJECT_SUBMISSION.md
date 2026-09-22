# ProofJudge — Builder Project Submission

## What it is

ProofJudge is a GenLayer-native evidence verification application for bounties, freelance milestones, grants, and community tasks.

A user submits:

- a natural-language requirement,
- a public evidence URL,
- a unique review ID.

The Intelligent Contract fetches the evidence from the live web, evaluates it with an LLM, validates the subjective outcome through GenLayer validator consensus, and stores the final verdict on-chain.

## Why GenLayer is essential

This workflow cannot be implemented as a normal deterministic smart contract: the contract must read arbitrary web evidence and reason about whether that evidence satisfies a human-language requirement.

ProofJudge uses:

- `gl.nondet.web.render` for live web evidence,
- `gl.nondet.exec_prompt` for structured evaluation,
- `gl.vm.run_nondet_unsafe` with an independent validator function,
- GenLayer consensus for the final on-chain decision.

## Live deployment

- Network: GenLayer Studionet
- Chain ID: 61999
- Contract: `0x52D23490C660d184b14087007E6B56126ed0B069`
- Explorer: https://explorer-studio.genlayer.com/address/0x52D23490C660d184b14087007E6B56126ed0B069
- Live app: https://proofjudge-genlayer-frontend.vercel.app

## Verified end-to-end execution

A real Studionet smoke test executed the complete path:

1. submitted a requirement and public evidence URL,
2. stored the pending review,
3. fetched and evaluated the evidence,
4. reached validator consensus,
5. stored and read the final verdict.

Submit transaction:

`0xeddbd86a8b8fb29d95f213cb566d9649f988343ee613f6e0bb2953b1a14298d0`

Resolve transaction:

`0xc93a299c8fab59fc6f67a11858343a698786a74a335109e7a2b38b2500ec547f`

Verified result:

- status: `approved`
- confidence: `99/100`
- validator outcome: majority agree
- CI live Studionet smoke workflow: passing

## Repository quality

The repository includes:

- Intelligent Contract source
- direct deterministic tests
- live Studionet integration test
- GenVM linting
- GitHub Actions CI
- Next.js + GenLayerJS frontend
- fee estimation flow
- deployment script
- live Vercel application
- public deployment and transaction evidence

## Future milestones

- multiple evidence URLs per review
- challenge and appeal rounds
- escrow / payout integration
- reviewer and submitter reputation
- evidence snapshots and content hashes
- domain-specific verdict schemas
