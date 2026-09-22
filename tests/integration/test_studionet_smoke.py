"""End-to-end smoke test against the deployed ProofJudge Studionet contract."""

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

DEPLOYED_ADDRESS = "0x52D23490C660d184b14087007E6B56126ed0B069"


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name)


@pytest.mark.integration
def test_resolve_on_deployed_studionet_contract():
    factory = get_contract_factory("ProofJudge")
    contract = factory.build_contract(DEPLOYED_ADDRESS)

    print(f"PROOFJUDGE_CONTRACT_ADDRESS={contract.address}", flush=True)

    review_id = "studionet-smoke-v1"
    submit = contract.submit_review(
        args=[
            review_id,
            "The evidence page must identify itself as Example Domain.",
            "https://example.com",
        ]
    )
    assert tx_execution_succeeded(submit)
    print(f"PROOFJUDGE_SUBMIT_RECEIPT={submit}", flush=True)

    pending = contract.get_review(args=[review_id])
    assert _field(pending, "status") == "pending"

    resolve = contract.resolve_review(args=[review_id])
    assert tx_execution_succeeded(resolve)
    print(f"PROOFJUDGE_RESOLVE_RECEIPT={resolve}", flush=True)

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
