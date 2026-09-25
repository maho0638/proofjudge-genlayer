"""Live V5 verification: ordered two-stage project plus rejected/refunded safety path."""

import hashlib
import time
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def _field(value, name):
    return value.get(name) if isinstance(value, dict) else getattr(value, name)


@pytest.mark.integration
def test_proofjudge_v5_composable_project(default_account, accounts):
    assert len(accounts) >= 2

    factory = get_contract_factory(contract_file_path="proof_judge_v5.py")
    local_source = Path("contracts/proof_judge_v5.py").read_text()
    assert (
        factory.contract_code.replace("\r\n", "\n").strip()
        == local_source.replace("\r\n", "\n").strip()
    )
    print("PROOFJUDGE_V5_DEPLOY_INPUT_MATCH=true", flush=True)
    print(
        "PROOFJUDGE_V5_DEPLOY_SOURCE_SHA256="
        + hashlib.sha256(local_source.encode()).hexdigest(),
        flush=True,
    )

    contract = factory.deploy(account=default_account, consensus_max_rotations=2)
    print(f"PROOFJUDGE_V5_CONTRACT_ADDRESS={contract.address}", flush=True)

    sponsor = contract.connect(account=default_account)
    contractor_account = accounts[1]
    contractor = contract.connect(account=contractor_account)
    reward = 1_000_000_000_000
    now = int(time.time())
    project = "proofjudge-v5-composable-project"
    stage1 = "proofjudge-v5-protocol"
    stage2 = "proofjudge-v5-sdk"

    create_stage1 = sponsor.create_milestone(
        args=[
            project,
            stage1,
            "",
            str(contractor_account.address),
            (
                "The public evidence must show ProofJudge V5 adds ordered multi-milestone "
                "chains, project progress, and participant settlement statistics."
            ),
            (
                "Approve only when both sources directly describe V5 composable milestones "
                "and the dependency rule that later stages wait for PAID."
            ),
            now + 3600,
        ]
    ).transact(value=reward, wait_interval=10000, wait_retries=40)
    assert tx_execution_succeeded(create_stage1)
    print(
        f"PROOFJUDGE_V5_STAGE1_CREATE_TX={create_stage1.get('hash', '')}",
        flush=True,
    )

    create_stage2 = sponsor.create_milestone(
        args=[
            project,
            stage2,
            stage1,
            str(contractor_account.address),
            (
                "The public evidence must show a reusable TypeScript SDK for project reads, "
                "participant stats, settlement auditing, and write-request builders."
            ),
            (
                "Approve only when both sources directly describe the reusable V5 SDK "
                "integration surface for dApps or agents."
            ),
            now + 7200,
        ]
    ).transact(value=reward, wait_interval=10000, wait_retries=40)
    assert tx_execution_succeeded(create_stage2)
    print(
        f"PROOFJUDGE_V5_STAGE2_CREATE_TX={create_stage2.get('hash', '')}",
        flush=True,
    )

    assert int(contract.get_project_job_count(args=[project]).call()) == 2
    assert str(contract.get_project_job_id(args=[project, 0]).call()) == stage1
    assert str(contract.get_project_job_id(args=[project, 1]).call()) == stage2
    assert bool(contract.is_milestone_unlocked(args=[stage2]).call()) is False
    print("PROOFJUDGE_V5_STAGE2_LOCKED_BEFORE_STAGE1_PAID=true", flush=True)

    primary = "https://proofjudge-genlayer-frontend.vercel.app/milestone-v5.txt"
    support = (
        "https://raw.githubusercontent.com/maho0638/"
        "proofjudge-genlayer/main/docs/MILESTONE_V5.md"
    )

    submit1 = contractor.submit_evidence(
        args=[stage1, primary, support]
    ).transact(wait_interval=10000, wait_retries=40)
    assert tx_execution_succeeded(submit1)
    print(f"PROOFJUDGE_V5_STAGE1_SUBMIT_TX={submit1.get('hash', '')}", flush=True)

    resolve1 = sponsor.resolve_job(args=[stage1]).transact(
        consensus_max_rotations=3,
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(resolve1)
    print(f"PROOFJUDGE_V5_STAGE1_RESOLVE_TX={resolve1.get('hash', '')}", flush=True)

    job1 = contract.get_job(args=[stage1]).call()
    assert str(_field(job1, "status")) == "APPROVED"
    assert str(_field(job1, "policy_version")) == "PJ_V5_COMPOSABLE_MILESTONES"

    claim1 = contractor.claim_payment(args=[stage1]).transact(
        wait_interval=10000, wait_retries=40
    )
    assert tx_execution_succeeded(claim1)
    print(f"PROOFJUDGE_V5_STAGE1_CLAIM_TX={claim1.get('hash', '')}", flush=True)

    assert bool(contract.is_milestone_unlocked(args=[stage2]).call()) is True
    print("PROOFJUDGE_V5_STAGE2_UNLOCKED_AFTER_STAGE1_PAID=true", flush=True)

    submit2 = contractor.submit_evidence(
        args=[stage2, primary, support]
    ).transact(wait_interval=10000, wait_retries=40)
    assert tx_execution_succeeded(submit2)
    print(f"PROOFJUDGE_V5_STAGE2_SUBMIT_TX={submit2.get('hash', '')}", flush=True)

    resolve2 = sponsor.resolve_job(args=[stage2]).transact(
        consensus_max_rotations=3,
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(resolve2)
    print(f"PROOFJUDGE_V5_STAGE2_RESOLVE_TX={resolve2.get('hash', '')}", flush=True)

    job2 = contract.get_job(args=[stage2]).call()
    assert str(_field(job2, "status")) == "APPROVED"

    claim2 = contractor.claim_payment(args=[stage2]).transact(
        wait_interval=10000, wait_retries=40
    )
    assert tx_execution_succeeded(claim2)
    print(f"PROOFJUDGE_V5_STAGE2_CLAIM_TX={claim2.get('hash', '')}", flush=True)

    progress = contract.get_project_progress(args=[project]).call()
    assert int(_field(progress, "total_milestones")) == 2
    assert int(_field(progress, "paid_milestones")) == 2
    assert int(_field(progress, "total_reward")) == reward * 2
    assert int(_field(progress, "settled_reward")) == reward * 2

    contractor_stats = contract.get_participant_stats(
        args=[str(contractor_account.address)]
    ).call()
    assert int(_field(contractor_stats, "paid_jobs")) == 2
    assert int(_field(contractor_stats, "total_earned")) == reward * 2
    print("PROOFJUDGE_V5_COMPOSABLE_PROJECT_VERIFIED=true", flush=True)

    # ------------------------------------------------------------------
    # Negative economic path on the SAME V5 contract:
    # irrelevant evidence must reject, then expired escrow returns to sponsor.
    # ------------------------------------------------------------------
    refund_job = "proofjudge-v5-bad-evidence-refund"
    refund_deadline = int(time.time()) + 120

    create_refund = sponsor.create_job(
        args=[
            refund_job,
            str(contractor_account.address),
            (
                "Both evidence sources must directly prove the ProofJudge V5 composable "
                "milestone protocol and its GenLayer settlement behavior."
            ),
            (
                "Reject generic, unrelated, unavailable, or contradictory evidence that "
                "does not prove the specified ProofJudge V5 milestone."
            ),
            refund_deadline,
        ]
    ).transact(value=reward, wait_interval=10000, wait_retries=40)
    assert tx_execution_succeeded(create_refund)
    print(
        f"PROOFJUDGE_V5_REFUND_CREATE_TX={create_refund.get('hash', '')}",
        flush=True,
    )

    submit_bad = contractor.submit_evidence(
        args=[
            refund_job,
            "https://example.com",
            "https://www.iana.org/help/example-domains",
        ]
    ).transact(wait_interval=10000, wait_retries=40)
    assert tx_execution_succeeded(submit_bad)
    print(
        f"PROOFJUDGE_V5_REFUND_SUBMIT_TX={submit_bad.get('hash', '')}",
        flush=True,
    )

    resolve_bad = sponsor.resolve_job(args=[refund_job]).transact(
        consensus_max_rotations=3,
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(resolve_bad)
    print(
        f"PROOFJUDGE_V5_REFUND_RESOLVE_TX={resolve_bad.get('hash', '')}",
        flush=True,
    )

    rejected = contract.get_job(args=[refund_job]).call()
    assert str(_field(rejected, "status")) == "REJECTED"
    assert str(_field(rejected, "reason_code")) in {
        "EVIDENCE_GAP",
        "SOURCE_UNAVAILABLE",
        "CONTRADICTORY_EVIDENCE",
    }
    print(
        f"PROOFJUDGE_V5_REFUND_REASON={_field(rejected, 'reason_code')}",
        flush=True,
    )

    sleep_for = max(0, refund_deadline - int(time.time()) + 12)
    if sleep_for:
        print(f"PROOFJUDGE_V5_WAITING_FOR_REFUND_SECONDS={sleep_for}", flush=True)
        time.sleep(sleep_for)

    refund = sponsor.refund_expired(args=[refund_job]).transact(
        wait_interval=10000, wait_retries=40
    )
    assert tx_execution_succeeded(refund)
    print(f"PROOFJUDGE_V5_REFUND_TX={refund.get('hash', '')}", flush=True)

    refunded = contract.get_job(args=[refund_job]).call()
    assert str(_field(refunded, "status")) == "REFUNDED"
    assert bool(_field(refunded, "reward_claimed")) is True

    final_contractor_stats = contract.get_participant_stats(
        args=[str(contractor_account.address)]
    ).call()
    sponsor_stats = contract.get_participant_stats(
        args=[str(default_account.address)]
    ).call()
    assert int(_field(final_contractor_stats, "paid_jobs")) == 2
    assert int(_field(final_contractor_stats, "refunded_jobs")) == 1
    assert int(_field(sponsor_stats, "total_recovered")) == reward

    print("PROOFJUDGE_V5_REFUNDED=true", flush=True)
    print("PROOFJUDGE_V5_ALL_ECONOMIC_PATHS_VERIFIED=true", flush=True)
