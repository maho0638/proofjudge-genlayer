# ProofJudge V5 Milestone — Composable Project Settlement

ProofJudge V4 was accepted as a complete bilateral milestone escrow. V5 turns the one-off agreement into reusable project infrastructure.

GenLayer's Builder Program states that points are assigned based on **novelty, complexity, and impact**. This milestone targets those dimensions directly.

## Novelty
- Ordered on-chain milestone dependencies.
- A later milestone cannot submit evidence until the prior milestone is actually PAID.
- Neutral, machine-readable participant settlement history instead of a subjective reputation score.

## Complexity
- Up to 12 ordered milestones per project.
- Same sponsor/contractor continuity, increasing deadlines, independent GEN escrow per stage.
- Project progress aggregation across lifecycle states and settled reward.
- Full V4 regression suite is rerun against V5, plus V5 dependency/stats tests.

## Impact
- A reusable TypeScript SDK lets other dApps and agents read projects, read participant stats, audit settlements, and build write requests.
- A dedicated /developers page documents integration.
- A live Studionet workflow proves a two-stage project and deployed-source equality before V5 is promoted.

## New contract surface
- create_milestone
- is_milestone_unlocked
- get_project_job_count
- get_project_job_id
- get_project_progress
- get_participant_stats

## Promotion gates
V5 becomes canonical only after direct tests, GenVM lint, SDK tests, frontend build, live two-stage Studionet settlement, and deployed-source equality all pass.
