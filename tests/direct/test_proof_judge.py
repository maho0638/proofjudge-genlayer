import json
import time
from datetime import datetime, timedelta, timezone

import pytest


REQUIREMENT = "The delivered page must clearly identify itself as Example Domain."
RUBRIC = "Approve only if the primary deliverable directly satisfies the requirement and independent support corroborates it."


@pytest.fixture(autouse=True)
def strict_direct_vm(direct_vm):
    direct_vm.strict_mocks = True
    direct_vm.check_pickling = True


def future_deadline(seconds=3600):
    return int(time.time()) + seconds


def create_demo_job(direct_vm, contract, sponsor, contractor, job_id="milestone-1"):
    direct_vm.sender = sponsor
    direct_vm.value = 2500
    contract.create_job(
        job_id,
        "0x" + contractor.hex(),
        REQUIREMENT,
        RUBRIC,
        future_deadline(),
    )
    direct_vm.value = 0


def submit_demo_evidence(direct_vm, contract, contractor, job_id="milestone-1"):
    direct_vm.sender = contractor
    contract.submit_evidence(
        job_id,
        "https://example.com",
        "https://www.iana.org/help/example-domains",
    )


def mock_verdict(direct_vm, approved, confidence, reason_code, evidence_basis=None, body=None):
    if evidence_basis is None:
        evidence_basis = {
            "DIRECT_EVIDENCE": "PRIMARY_DIRECT",
            "REQUIREMENT_FIT": "RUBRIC_MATCH",
            "SOURCE_AUTHORITY": "AUTHORITATIVE_PRIMARY",
            "CROSS_CHECK": "INDEPENDENT_CORROBORATION",
            "CONTRADICTORY_EVIDENCE": "CONTRADICTORY_EVIDENCE",
            "SOURCE_UNAVAILABLE": "SOURCE_UNAVAILABLE",
            "EVIDENCE_GAP": "MISSING_EVIDENCE",
        }.get(reason_code, "MISSING_EVIDENCE")

    direct_vm.mock_web(
        r".*",
        {"status": 200, "body": body or "Public evidence content used by the milestone judge."},
    )
    direct_vm.mock_llm(
        r"(?s).*neutral settlement judge for a milestone escrow.*",
        json.dumps(
            {
                "approved": approved,
                "confidence": confidence,
                "reason_code": reason_code,
                "evidence_basis": evidence_basis,
            }
        ),
    )


def mock_approved(direct_vm):
    mock_verdict(direct_vm, True, 97, "CROSS_CHECK")


def mock_rejected(direct_vm):
    mock_verdict(direct_vm, False, 94, "EVIDENCE_GAP")


def test_create_job_escrows_gen_indexes_and_audits(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)

    job = contract.get_job("milestone-1")
    assert job.reward == 2500
    assert job.status == "OPEN"
    assert str(job.contractor).lower() == "0x" + direct_bob.hex()
    assert contract.get_job_count() == 1
    assert contract.get_job_id(0) == "milestone-1"
    assert int(job.created_at) > 0
    assert int(job.submitted_at) == 0
    assert int(job.resolved_at) == 0
    assert int(job.settled_at) == 0
    assert job.policy_version == "PJ_V4_SNAPSHOT_CHALLENGE"


def test_zero_reward_is_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 0

    with direct_vm.expect_revert("greater than zero"):
        contract.create_job(
            "no-reward",
            "0x" + direct_bob.hex(),
            REQUIREMENT,
            RUBRIC,
            future_deadline(),
        )


def test_zero_address_contractor_is_rejected(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 1000

    with direct_vm.expect_revert("zero address"):
        contract.create_job(
            "zero-contractor",
            "0x0000000000000000000000000000000000000000",
            REQUIREMENT,
            RUBRIC,
            future_deadline(),
        )


def test_sponsor_cannot_assign_self(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 1000

    with direct_vm.expect_revert("must be different"):
        contract.create_job(
            "self-job",
            "0x" + direct_alice.hex(),
            REQUIREMENT,
            RUBRIC,
            future_deadline(),
        )


def test_duplicate_job_id_is_rejected(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)

    direct_vm.sender = direct_alice
    direct_vm.value = 1000
    with direct_vm.expect_revert("already exists"):
        contract.create_job(
            "milestone-1",
            "0x" + direct_charlie.hex(),
            REQUIREMENT,
            RUBRIC,
            future_deadline(),
        )


def test_overlong_deadline_is_rejected(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 1000

    with direct_vm.expect_revert("365 days"):
        contract.create_job(
            "too-long",
            "0x" + direct_bob.hex(),
            REQUIREMENT,
            RUBRIC,
            future_deadline(366 * 24 * 60 * 60),
        )


def test_only_assigned_contractor_can_submit(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)

    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("assigned contractor"):
        contract.submit_evidence(
            "milestone-1",
            "https://example.com",
            "https://www.iana.org/help/example-domains",
        )


def test_evidence_requires_https(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("must use HTTPS"):
        contract.submit_evidence(
            "milestone-1",
            "http://example.com",
            "https://www.iana.org/help/example-domains",
        )


def test_evidence_requires_independent_domains(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("independent domains"):
        contract.submit_evidence(
            "milestone-1",
            "https://example.com/a",
            "https://www.example.com/b",
        )


def test_consensus_approval_unlocks_claim_state_and_records_audit_time(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_approved(direct_vm)

    direct_vm.sender = direct_alice
    contract.resolve_job("milestone-1")

    job = contract.get_job("milestone-1")
    assert job.status == "APPROVED"
    assert job.confidence == 97
    assert job.reason_code == "CROSS_CHECK"
    assert "independent support" in job.rationale
    assert job.reward_claimed is False
    assert int(job.submitted_at) > 0
    assert int(job.resolved_at) >= int(job.submitted_at)


def test_low_confidence_yes_cannot_unlock_payment(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_verdict(direct_vm, True, 61, "REQUIREMENT_FIT")

    contract.resolve_job("milestone-1")
    job = contract.get_job("milestone-1")

    assert job.status == "REJECTED"
    assert job.confidence == 61
    assert job.reason_code == "EVIDENCE_GAP"

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("not approved"):
        contract.claim_payment("milestone-1")


def test_rejection_can_be_resubmitted_before_deadline(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_rejected(direct_vm)

    contract.resolve_job("milestone-1")
    rejected = contract.get_job("milestone-1")
    assert rejected.status == "REJECTED"
    assert rejected.attempt_count == 1

    direct_vm.sender = direct_bob
    contract.submit_evidence(
        "milestone-1",
        "https://example.org/retry",
        "https://www.rfc-editor.org/rfc/rfc2606",
    )
    retried = contract.get_job("milestone-1")
    assert retried.status == "SUBMITTED"
    assert retried.attempt_count == 2
    assert retried.confidence == 0
    assert retried.reason_code == ""


def test_attempts_are_capped_at_three(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    mock_rejected(direct_vm)

    for attempt in range(3):
        direct_vm.sender = direct_bob
        contract.submit_evidence(
            "milestone-1",
            f"https://primary-{attempt}.example.net/proof",
            f"https://support-{attempt}.independent.org/proof",
        )
        contract.resolve_job("milestone-1")
        assert contract.get_job("milestone-1").status == "REJECTED"

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Maximum evidence attempts"):
        contract.submit_evidence(
            "milestone-1",
            "https://fourth.example.net/proof",
            "https://fourth.independent.org/proof",
        )


def test_validator_rejects_dissenting_decision(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_approved(direct_vm)

    contract.resolve_job("milestone-1")

    direct_vm.clear_mocks()
    direct_vm.mock_web(
        r".*",
        {"status": 200, "body": "The validator independently sees insufficient evidence."},
    )
    direct_vm.mock_llm(
        r"(?s).*neutral settlement judge for a milestone escrow.*",
        json.dumps(
            {
                "approved": False,
                "confidence": 96,
                "reason_code": "EVIDENCE_GAP",
            }
        ),
    )

    assert direct_vm.run_validator() is False


def test_non_contractor_cannot_claim(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_approved(direct_vm)
    contract.resolve_job("milestone-1")

    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("assigned contractor"):
        contract.claim_payment("milestone-1")


def test_cannot_resolve_without_submitted_evidence(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)

    with direct_vm.expect_revert("no unresolved evidence"):
        contract.resolve_job("milestone-1")


def test_validator_rejects_mutated_evidence_even_with_same_verdict(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_verdict(
        direct_vm,
        True,
        96,
        "CROSS_CHECK",
        "INDEPENDENT_CORROBORATION",
        body="Version A of the public evidence proves the milestone.",
    )

    contract.resolve_job("milestone-1")

    direct_vm.clear_mocks()
    mock_verdict(
        direct_vm,
        True,
        96,
        "CROSS_CHECK",
        "INDEPENDENT_CORROBORATION",
        body="Version B changed after the leader evaluated the URL.",
    )

    assert direct_vm.run_validator() is False


def test_validator_requires_exact_reason_and_evidence_basis(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_verdict(
        direct_vm,
        True,
        95,
        "CROSS_CHECK",
        "INDEPENDENT_CORROBORATION",
    )
    contract.resolve_job("milestone-1")

    direct_vm.clear_mocks()
    mock_verdict(
        direct_vm,
        True,
        95,
        "REQUIREMENT_FIT",
        "RUBRIC_MATCH",
    )

    assert direct_vm.run_validator() is False


def test_resolution_stores_evidence_snapshots_and_basis(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_approved(direct_vm)

    contract.resolve_job("milestone-1")
    job = contract.get_job("milestone-1")

    assert job.evidence_basis == "INDEPENDENT_CORROBORATION"
    assert "Public evidence content" in job.primary_snapshot
    assert "Public evidence content" in job.support_snapshot
    assert len(job.primary_snapshot) <= 700
    assert len(job.support_snapshot) <= 700


def test_contradictory_evidence_is_explicitly_rejected(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_verdict(
        direct_vm,
        False,
        99,
        "CONTRADICTORY_EVIDENCE",
        "CONTRADICTORY_EVIDENCE",
        body="The primary and independent evidence materially contradict each other.",
    )

    contract.resolve_job("milestone-1")
    job = contract.get_job("milestone-1")
    assert job.status == "REJECTED"
    assert job.reason_code == "CONTRADICTORY_EVIDENCE"
    assert job.evidence_basis == "CONTRADICTORY_EVIDENCE"


def test_sponsor_can_challenge_once_and_claim_is_blocked_until_reresolution(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_approved(direct_vm)
    contract.resolve_job("milestone-1")

    direct_vm.sender = direct_alice
    contract.challenge_resolution(
        "milestone-1",
        "The sponsor disputes whether the independent evidence proves the deliverable.",
    )

    challenged = contract.get_job("milestone-1")
    assert challenged.status == "CHALLENGED"
    assert challenged.challenge_count == 1
    assert int(challenged.challenged_at) > 0

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("not approved"):
        contract.claim_payment("milestone-1")

    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("resolved decision"):
        contract.challenge_resolution(
            "milestone-1",
            "A second challenge must not be accepted while the first is unresolved.",
        )

    direct_vm.clear_mocks()
    mock_rejected(direct_vm)
    contract.resolve_challenge("milestone-1")
    assert contract.get_job("milestone-1").status == "REJECTED"


def test_unauthorized_wallet_cannot_challenge(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_approved(direct_vm)
    contract.resolve_job("milestone-1")

    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("sponsor or contractor"):
        contract.challenge_resolution(
            "milestone-1",
            "An unrelated wallet must not be able to change settlement state.",
        )


def test_submitted_job_cannot_refund_during_resolution_grace(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)

    direct_vm.warp((datetime.now(timezone.utc) + timedelta(hours=2)).isoformat())
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Resolution grace period"):
        contract.refund_expired("milestone-1")


def test_stalled_submitted_job_can_refund_after_resolution_grace(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)

    direct_vm.warp((datetime.now(timezone.utc) + timedelta(days=2)).isoformat())
    direct_vm.sender = direct_alice
    contract.refund_expired("milestone-1")

    job = contract.get_job("milestone-1")
    assert job.status == "REFUNDED"
    assert job.reward_claimed is True


def test_early_refund_is_rejected(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)

    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Wait for the deadline"):
        contract.refund_expired("milestone-1")


def test_non_sponsor_cannot_refund(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)

    direct_vm.warp((datetime.now(timezone.utc) + timedelta(days=2)).isoformat())
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("Only the sponsor"):
        contract.refund_expired("milestone-1")


def test_contract_balance_failure_blocks_payment(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_approved(direct_vm)
    contract.resolve_job("milestone-1")

    direct_vm.deal(contract.address, 0)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("balance is insufficient"):
        contract.claim_payment("milestone-1")

    job = contract.get_job("milestone-1")
    assert job.reward_claimed is False
    assert job.status == "APPROVED"


def test_double_claim_is_rejected(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)
    mock_approved(direct_vm)
    contract.resolve_job("milestone-1")

    direct_vm.sender = direct_bob
    contract.claim_payment("milestone-1")
    assert contract.get_job("milestone-1").status == "PAID"

    with direct_vm.expect_revert("not approved"):
        contract.claim_payment("milestone-1")
