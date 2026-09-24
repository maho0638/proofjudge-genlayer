"""Live Studionet verification: real release payout + rejected evidence + sponsor refund."""

import hashlib
import time
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name)


@pytest.mark.integration
def test_proofjudge_live_economic_outcomes(default_account, accounts):
    assert len(accounts) >= 2

    factory = get_contract_factory(contract_file_path="contracts/proof_judge.py")
    local_source = Path("contracts/proof_judge.py").read_text()
    assert factory.contract_code.replace("\r\n", "\n").strip() == local_source.replace("\r\n", "\n").strip()
    source_sha256 = hashlib.sha256(local_source.encode("utf-8")).hexdigest()
    print("PROOFJUDGE_DEPLOY_INPUT_MATCH=true", flush=True)
    print(f"PROOFJUDGE_DEPLOY_SOURCE_SHA256={source_sha256}", flush=True)

    contract = factory.deploy(
        account=default_account,
        consensus_max_rotations=2,
    )

    print(f"PROOFJUDGE_CONTRACT_ADDRESS={contract.address}", flush=True)

    sponsor = contract.connect(account=default_account)
    contractor_account = accounts[1]
    contractor = contract.connect(account=contractor_account)
    reward = 1_000_000_000_000

    # ------------------------------------------------------------------
    # Outcome A: a real ProofJudge production release is approved and paid.
    # ------------------------------------------------------------------
    paid_job_id = "proofjudge-production-milestone-v4"
    paid_deadline = int(time.time()) + 3600

    create_paid_tx = sponsor.create_job(
        args=[
            paid_job_id,
            str(contractor_account.address),
            (
                "The production deliverable must clearly identify itself as ProofJudge, "
                "describe a milestone escrow using native GEN, and explain that live "
                "public evidence is judged by GenLayer validator consensus before payout. "
                "The independent repository source must corroborate the same product."
            ),
            (
                "Approve only when the live production page directly demonstrates the "
                "ProofJudge milestone-settlement product and the independent public "
                "repository corroborates GEN escrow, live evidence, validator consensus, "
                "and contractor payout. Reject if either source is missing or materially "
                "contradicts the claimed release."
            ),
            paid_deadline,
        ]
    ).transact(
        value=reward,
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(create_paid_tx)
    print(f"PROOFJUDGE_PAID_CREATE_TX={create_paid_tx.get('hash', '')}", flush=True)

    submit_paid_tx = contractor.submit_evidence(
        args=[
            paid_job_id,
            "https://proofjudge-genlayer-frontend.vercel.app",
            "https://raw.githubusercontent.com/maho0638/proofjudge-genlayer/main/README.md",
        ]
    ).transact(
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(submit_paid_tx)
    print(f"PROOFJUDGE_PAID_SUBMIT_TX={submit_paid_tx.get('hash', '')}", flush=True)

    resolve_paid_tx = sponsor.resolve_job(args=[paid_job_id]).transact(
        consensus_max_rotations=3,
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(resolve_paid_tx)
    print(f"PROOFJUDGE_PAID_RESOLVE_TX={resolve_paid_tx.get('hash', '')}", flush=True)

    approved = contract.get_job(args=[paid_job_id]).call()
    print(f"PROOFJUDGE_PAID_STATUS={_field(approved, 'status')}", flush=True)
    print(f"PROOFJUDGE_PAID_CONFIDENCE={_field(approved, 'confidence')}", flush=True)
    print(f"PROOFJUDGE_PAID_REASON_CODE={_field(approved, 'reason_code')}", flush=True)
    print(f"PROOFJUDGE_PAID_RATIONALE={_field(approved, 'rationale')}", flush=True)

    assert str(_field(approved, "status")) == "APPROVED"
    assert int(_field(approved, "confidence")) >= 70
    assert str(_field(approved, "reason_code")) in {
        "DIRECT_EVIDENCE",
        "REQUIREMENT_FIT",
        "SOURCE_AUTHORITY",
        "CROSS_CHECK",
    }
    assert str(_field(approved, "policy_version")) == "PJ_V4_SNAPSHOT_CHALLENGE"
    assert str(_field(approved, "evidence_basis")) in {
        "PRIMARY_DIRECT",
        "RUBRIC_MATCH",
        "AUTHORITATIVE_PRIMARY",
        "INDEPENDENT_CORROBORATION",
    }
    assert len(str(_field(approved, "primary_snapshot"))) > 0
    assert len(str(_field(approved, "support_snapshot"))) > 0
    assert int(_field(approved, "created_at")) > 0
    assert int(_field(approved, "submitted_at")) > 0
    assert int(_field(approved, "resolved_at")) > 0

    claim_paid_tx = contractor.claim_payment(args=[paid_job_id]).transact(
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(claim_paid_tx)
    print(f"PROOFJUDGE_PAID_CLAIM_TX={claim_paid_tx.get('hash', '')}", flush=True)

    paid = contract.get_job(args=[paid_job_id]).call()
    assert str(_field(paid, "status")) == "PAID"
    assert bool(_field(paid, "reward_claimed")) is True
    assert int(_field(paid, "settled_at")) > 0
    print("PROOFJUDGE_PAID_REWARD_CLAIMED=true", flush=True)

    # ------------------------------------------------------------------
    # Outcome B: irrelevant evidence is rejected, then sponsor gets refund.
    # ------------------------------------------------------------------
    refund_job_id = "irrelevant-evidence-refund-v1"
    refund_deadline = int(time.time()) + 90

    create_refund_tx = sponsor.create_job(
        args=[
            refund_job_id,
            str(contractor_account.address),
            (
                "The primary evidence and independent support must both explicitly prove "
                "a completed ProofJudge production milestone and describe its GenLayer "
                "escrow settlement lifecycle."
            ),
            (
                "Reject when the submitted pages are generic, unrelated, ambiguous, or "
                "fail to mention ProofJudge and its GenLayer milestone escrow."
            ),
            refund_deadline,
        ]
    ).transact(
        value=reward,
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(create_refund_tx)
    print(f"PROOFJUDGE_REFUND_CREATE_TX={create_refund_tx.get('hash', '')}", flush=True)

    submit_bad_tx = contractor.submit_evidence(
        args=[
            refund_job_id,
            "https://example.com",
            "https://www.iana.org/help/example-domains",
        ]
    ).transact(
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(submit_bad_tx)
    print(f"PROOFJUDGE_REFUND_SUBMIT_TX={submit_bad_tx.get('hash', '')}", flush=True)

    resolve_bad_tx = sponsor.resolve_job(args=[refund_job_id]).transact(
        consensus_max_rotations=3,
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(resolve_bad_tx)
    print(f"PROOFJUDGE_REFUND_RESOLVE_TX={resolve_bad_tx.get('hash', '')}", flush=True)

    rejected = contract.get_job(args=[refund_job_id]).call()
    print(f"PROOFJUDGE_REFUND_DECISION={_field(rejected, 'status')}", flush=True)
    print(f"PROOFJUDGE_REFUND_CONFIDENCE={_field(rejected, 'confidence')}", flush=True)
    print(f"PROOFJUDGE_REFUND_REASON_CODE={_field(rejected, 'reason_code')}", flush=True)

    assert str(_field(rejected, "status")) == "REJECTED"
    assert str(_field(rejected, "reason_code")) in {
        "EVIDENCE_GAP",
        "SOURCE_UNAVAILABLE",
    }

    sleep_for = max(0, refund_deadline - int(time.time()) + 12)
    if sleep_for:
        print(f"PROOFJUDGE_WAITING_FOR_REFUND_SECONDS={sleep_for}", flush=True)
        time.sleep(sleep_for)

    refund_tx = sponsor.refund_expired(args=[refund_job_id]).transact(
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(refund_tx)
    print(f"PROOFJUDGE_REFUND_TX={refund_tx.get('hash', '')}", flush=True)

    refunded = contract.get_job(args=[refund_job_id]).call()
    assert str(_field(refunded, "status")) == "REFUNDED"
    assert bool(_field(refunded, "reward_claimed")) is True
    assert int(_field(refunded, "settled_at")) > 0
    print("PROOFJUDGE_REFUNDED=true", flush=True)

    assert int(contract.get_job_count().call()) == 2
    assert str(contract.get_job_id(args=[0]).call()) == paid_job_id
    assert str(contract.get_job_id(args=[1]).call()) == refund_job_id
