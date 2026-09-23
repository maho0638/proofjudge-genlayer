"""Live Studionet end-to-end test: escrow -> evidence -> consensus -> contractor claim."""

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name)


@pytest.mark.integration
def test_proofjudge_live_escrow_flow(default_account, accounts):
    assert len(accounts) >= 2

    factory = get_contract_factory("ProofJudge")
    contract = factory.deploy(
        account=default_account,
        consensus_max_rotations=2,
    )

    print(f"PROOFJUDGE_CONTRACT_ADDRESS={contract.address}", flush=True)

    sponsor = contract.connect(account=default_account)
    contractor_account = accounts[1]
    contractor = contract.connect(account=contractor_account)

    job_id = "example-domain-milestone-v2"
    reward = 1_000_000_000_000

    create_tx = sponsor.create_job(
        args=[
            job_id,
            str(contractor_account.address),
            "The primary deliverable must clearly identify itself as Example Domain and the supporting source must corroborate that example domains are reserved for documentation.",
            "Approve only when the primary page directly satisfies the requirement and an independent authoritative source corroborates the claim.",
            4000000000,
        ]
    ).transact(
        value=reward,
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(create_tx)
    print(f"PROOFJUDGE_CREATE_TX={create_tx.get('hash', '')}", flush=True)

    submit_tx = contractor.submit_evidence(
        args=[
            job_id,
            "https://example.com",
            "https://www.iana.org/help/example-domains",
        ]
    ).transact(
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(submit_tx)
    print(f"PROOFJUDGE_SUBMIT_TX={submit_tx.get('hash', '')}", flush=True)

    resolve_tx = sponsor.resolve_job(args=[job_id]).transact(
        consensus_max_rotations=3,
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(resolve_tx)
    print(f"PROOFJUDGE_RESOLVE_TX={resolve_tx.get('hash', '')}", flush=True)

    result = contract.get_job(args=[job_id]).call()
    print(f"PROOFJUDGE_STATUS={_field(result, 'status')}", flush=True)
    print(f"PROOFJUDGE_CONFIDENCE={_field(result, 'confidence')}", flush=True)
    print(f"PROOFJUDGE_REASON_CODE={_field(result, 'reason_code')}", flush=True)
    print(f"PROOFJUDGE_RATIONALE={_field(result, 'rationale')}", flush=True)

    assert str(_field(result, "status")) == "APPROVED"
    assert int(_field(result, "confidence")) >= 70
    assert str(_field(result, "reason_code")) in {
        "DIRECT_EVIDENCE",
        "REQUIREMENT_FIT",
        "SOURCE_AUTHORITY",
        "CROSS_CHECK",
    }

    claim_tx = contractor.claim_payment(args=[job_id]).transact(
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(claim_tx)
    print(f"PROOFJUDGE_CLAIM_TX={claim_tx.get('hash', '')}", flush=True)

    paid = contract.get_job(args=[job_id]).call()
    assert str(_field(paid, "status")) == "PAID"
    assert bool(_field(paid, "reward_claimed")) is True
    print("PROOFJUDGE_REWARD_CLAIMED=true", flush=True)
