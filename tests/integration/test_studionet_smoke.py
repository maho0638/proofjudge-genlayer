"""Studionet deployment + end-to-end smoke test for ProofJudge."""

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name)


@pytest.mark.integration
def test_deploy_and_resolve_on_studionet():
    factory = get_contract_factory("ProofJudge")
    contract = factory.deploy(consensus_max_rotations=2)

    print(f"PROOFJUDGE_CONTRACT_ADDRESS={contract.address}", flush=True)

    review_id = "studionet-smoke"
    submit = contract.submit_review(
        args=[
            review_id,
            "The evidence page must identify itself as Example Domain.",
            "https://example.com",
        ],
        wait_interval=10000,
        wait_retries=30,
    )
    assert tx_execution_succeeded(submit)

    pending = contract.get_review(args=[review_id])
    assert _field(pending, "status") == "pending"

    resolve = contract.resolve_review(
        args=[review_id],
        wait_interval=10000,
        wait_retries=40,
    )
    assert tx_execution_succeeded(resolve)

    final = contract.get_review(args=[review_id])
    status = _field(final, "status")
    confidence = int(_field(final, "confidence"))
    summary = str(_field(final, "summary"))

    print(f"PROOFJUDGE_SMOKE_STATUS={status}", flush=True)
    print(f"PROOFJUDGE_SMOKE_CONFIDENCE={confidence}", flush=True)
    print(f"PROOFJUDGE_SMOKE_SUMMARY={summary}", flush=True)

    assert status in ("approved", "rejected")
    assert 0 <= confidence <= 100
    assert summary
