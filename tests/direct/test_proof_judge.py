import json


def create_demo_job(direct_vm, contract, sponsor, contractor):
    direct_vm.sender = sponsor
    direct_vm.value = 2500
    contract.create_job(
        "milestone-1",
        contractor,
        "The delivered page must clearly identify itself as Example Domain.",
        "Approve only if the primary deliverable directly satisfies the requirement and independent support corroborates it.",
        4000000000,
    )
    direct_vm.value = 0


def submit_demo_evidence(direct_vm, contract, contractor):
    direct_vm.sender = contractor
    contract.submit_evidence(
        "milestone-1",
        "https://example.com",
        "https://www.iana.org/help/example-domains",
    )


def mock_approved(direct_vm):
    direct_vm.mock_web(
        r".*example\.com.*",
        {"status": 200, "body": "Example Domain. This domain is for use in illustrative examples."},
    )
    direct_vm.mock_web(
        r".*iana\.org.*",
        {"status": 200, "body": "IANA-managed example domains are reserved for documentation examples."},
    )
    direct_vm.mock_llm(
        r"(?s).*neutral settlement judge for a milestone escrow.*",
        json.dumps(
            {
                "approved": True,
                "confidence": 97,
                "reason_code": "CROSS_CHECK",
            }
        ),
    )


def test_create_job_escrows_gen_and_indexes(
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


def test_zero_reward_is_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 0

    with direct_vm.expect_revert("greater than zero"):
        contract.create_job(
            "no-reward",
            direct_bob,
            "Requirement",
            "Rubric",
            4000000000,
        )


def test_sponsor_cannot_assign_self(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 1000

    with direct_vm.expect_revert("must be different"):
        contract.create_job(
            "self-job",
            direct_alice,
            "Requirement",
            "Rubric",
            4000000000,
        )
    direct_vm.value = 0


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


def test_consensus_approval_unlocks_claim_state(
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


def test_rejection_can_be_resubmitted_before_deadline(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/proof_judge.py")
    create_demo_job(direct_vm, contract, direct_alice, direct_bob)
    submit_demo_evidence(direct_vm, contract, direct_bob)

    direct_vm.mock_web(
        r".*",
        {"status": 200, "body": "No verifiable deliverable is present."},
    )
    direct_vm.mock_llm(
        r"(?s).*neutral settlement judge for a milestone escrow.*",
        json.dumps(
            {
                "approved": False,
                "confidence": 94,
                "reason_code": "EVIDENCE_GAP",
            }
        ),
    )

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
