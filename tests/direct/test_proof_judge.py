import json


def test_submit_review(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice

    contract.submit_review(
        "task-1",
        "The page must contain a working product demo and setup instructions.",
        "https://example.com/demo",
    )

    review = contract.get_review("task-1")
    assert review.id == "task-1"
    assert review.status == "pending"
    assert review.confidence == 0
    assert review.summary == ""


def test_duplicate_review_fails(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice

    contract.submit_review("task-1", "Publish docs", "https://example.com/docs")

    with direct_vm.expect_revert("Review already exists"):
        contract.submit_review("task-1", "Different task", "https://example.com/other")


def test_resolve_approved(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice

    contract.submit_review(
        "task-2",
        "The evidence must show a public technical article about GenLayer.",
        "https://example.com/article",
    )

    direct_vm.mock_web(
        r".*example\.com/article.*",
        {
            "status": 200,
            "body": "Technical article: Building a GenLayer Intelligent Contract. Includes code and deployment steps.",
        },
    )
    direct_vm.mock_llm(
        r"(?s).*evaluating public evidence for a task-completion claim.*",
        json.dumps(
            {
                "approved": True,
                "confidence": 96,
                "summary": "Evidence contains a public GenLayer technical article with code and deployment steps.",
            }
        ),
    )

    contract.resolve_review("task-2")
    review = contract.get_review("task-2")

    assert review.status == "approved"
    assert review.confidence == 96
    assert "GenLayer" in review.summary


def test_resolve_rejected(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice

    contract.submit_review(
        "task-3",
        "The evidence must contain a working product demo.",
        "https://example.com/empty",
    )

    direct_vm.mock_web(
        r".*example\.com/empty.*",
        {"status": 200, "body": "Coming soon. No demo is available."},
    )
    direct_vm.mock_llm(
        r"(?s).*evaluating public evidence for a task-completion claim.*",
        json.dumps(
            {
                "approved": False,
                "confidence": 99,
                "summary": "The page explicitly says the demo is not available.",
            }
        ),
    )

    contract.resolve_review("task-3")
    review = contract.get_review("task-3")

    assert review.status == "rejected"
    assert review.confidence == 99


def test_cannot_resolve_twice(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/proof_judge.py")
    direct_vm.sender = direct_alice

    contract.submit_review("task-4", "Publish evidence", "https://example.com/evidence")

    direct_vm.mock_web(
        r".*example\.com/evidence.*",
        {"status": 200, "body": "Evidence is public."},
    )
    direct_vm.mock_llm(
        r"(?s).*evaluating public evidence for a task-completion claim.*",
        json.dumps(
            {
                "approved": True,
                "confidence": 90,
                "summary": "Public evidence is present.",
            }
        ),
    )

    contract.resolve_review("task-4")

    with direct_vm.expect_revert("Review already resolved"):
        contract.resolve_review("task-4")
