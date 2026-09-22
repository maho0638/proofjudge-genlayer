"""Live Studionet deployment and verification test for SourceVerifier."""

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name)


@pytest.mark.integration
def test_source_verifier_live_studionet():
    factory = get_contract_factory("SourceVerifier")
    contract = factory.deploy(consensus_max_rotations=2)

    print(f"SOURCE_VERIFIER_CONTRACT_ADDRESS={contract.address}", flush=True)

    verification_id = "iana-example-domain-v1"
    tx = contract.verify_claim(
        args=[
            verification_id,
            "example.com is intended for use in documentation examples.",
            "https://example.com",
            "https://www.iana.org/help/example-domains",
        ]
    ).transact(
        wait_interval=10000,
        wait_retries=40,
    )

    assert tx_execution_succeeded(tx)
    print(f"SOURCE_VERIFIER_VERIFY_RECEIPT={tx}", flush=True)

    result = contract.get_verification(args=[verification_id]).call()

    verdict = str(_field(result, "verdict"))
    confidence = int(_field(result, "confidence"))
    sources_agree = int(_field(result, "sources_agree"))
    rationale = str(_field(result, "rationale"))

    print(f"SOURCE_VERIFIER_VERDICT={verdict}", flush=True)
    print(f"SOURCE_VERIFIER_CONFIDENCE={confidence}", flush=True)
    print(f"SOURCE_VERIFIER_SOURCES_AGREE={sources_agree}", flush=True)
    print(f"SOURCE_VERIFIER_RATIONALE={rationale}", flush=True)

    assert verdict == "supported"
    assert confidence >= 70
    assert sources_agree == 2
    assert rationale
