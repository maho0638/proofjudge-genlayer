import json


def test_supported_claim(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/source_verifier.py")
    direct_vm.sender = direct_alice

    direct_vm.mock_web(
        r".*source-one\.example.*",
        {"status": 200, "body": "Release v2.0 was published on 10 September 2026."},
    )
    direct_vm.mock_web(
        r".*source-two\.example.*",
        {"status": 200, "body": "Changelog: version 2.0 released September 10, 2026."},
    )
    direct_vm.mock_llm(
        r"(?s).*factual claim verifier.*",
        json.dumps(
            {
                "verdict": "supported",
                "confidence": 97,
                "sources_agree": 2,
                "rationale": "Both sources independently state that v2.0 was released on 10 September 2026.",
            }
        ),
    )

    contract.verify_claim(
        "release-check",
        "Version 2.0 was released on 10 September 2026.",
        "https://source-one.example/release",
        "https://source-two.example/changelog",
    )

    result = contract.get_verification("release-check")
    assert result.verdict == "supported"
    assert result.confidence == 97
    assert result.sources_agree == 2
    assert "Both sources" in result.rationale


def test_contradicted_claim(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/source_verifier.py")
    direct_vm.sender = direct_alice

    direct_vm.mock_web(
        r".*source-one\.example.*",
        {"status": 200, "body": "The product launch date is 15 October 2026."},
    )
    direct_vm.mock_web(
        r".*source-two\.example.*",
        {"status": 200, "body": "Official launch scheduled for October 15, 2026."},
    )
    direct_vm.mock_llm(
        r"(?s).*factual claim verifier.*",
        json.dumps(
            {
                "verdict": "contradicted",
                "confidence": 96,
                "sources_agree": 2,
                "rationale": "Both sources give 15 October 2026, contradicting the claimed 1 October date.",
            }
        ),
    )

    contract.verify_claim(
        "launch-check",
        "The product launched on 1 October 2026.",
        "https://source-one.example/news",
        "https://source-two.example/official",
    )

    result = contract.get_verification("launch-check")
    assert result.verdict == "contradicted"
    assert result.sources_agree == 2


def test_rejects_same_source(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/source_verifier.py")
    direct_vm.sender = direct_alice

    with direct_vm.expect_revert("Sources must be different"):
        contract.verify_claim(
            "same-source",
            "A claim",
            "https://example.com",
            "https://example.com",
        )


def test_rejects_non_https_source(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/source_verifier.py")
    direct_vm.sender = direct_alice

    with direct_vm.expect_revert("Sources must use HTTPS"):
        contract.verify_claim(
            "bad-url",
            "A claim",
            "http://example.com",
            "https://example.org",
        )


def test_rejects_duplicate_verification_id(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/source_verifier.py")
    direct_vm.sender = direct_alice

    direct_vm.mock_web(
        r".*one\.example.*",
        {"status": 200, "body": "Evidence one."},
    )
    direct_vm.mock_web(
        r".*two\.example.*",
        {"status": 200, "body": "Evidence two."},
    )
    direct_vm.mock_llm(
        r"(?s).*factual claim verifier.*",
        json.dumps(
            {
                "verdict": "insufficient",
                "confidence": 70,
                "sources_agree": 2,
                "rationale": "The supplied evidence does not establish the claim.",
            }
        ),
    )

    contract.verify_claim(
        "duplicate",
        "A claim",
        "https://one.example/a",
        "https://two.example/b",
    )

    with direct_vm.expect_revert("Verification already exists"):
        contract.verify_claim(
            "duplicate",
            "Another claim",
            "https://one.example/a",
            "https://two.example/b",
        )
