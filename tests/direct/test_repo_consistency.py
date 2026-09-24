import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OLD_STEWARD_ADDRESSES = {
    "0x52D23490C660d184b14087007E6B56126ed0B069".lower(),
    "0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc".lower(),
    "0x699f62FA0f53B92D85949B1F046f6B50209707eE".lower(),
    "0x0149C49f43e6f109046c78D9146A950Dde818BDF".lower(),
}

OLD_WORKFLOW_IDS = {
    "35786696088",
    "35985412296",
    "35990646474",
    "35992879746",
}

ADDRESS_REFERENCE_FILES = [
    ROOT / "frontend" / "lib" / "genlayer.ts",
    ROOT / "README.md",
    ROOT / "PROJECT_SUBMISSION.md",
    ROOT / "docs" / "STEWARD_VERIFICATION.md",
    ROOT / "docs" / "QUALITY_BAR.md",
    ROOT / "docs" / "SECURITY.md",
    ROOT / "docs" / "PRODUCT_READINESS.md",
    ROOT / "docs" / "STEWARD_REMEDIATION.md",
]

WORKFLOW_REFERENCE_FILES = [
    ROOT / "README.md",
    ROOT / "PROJECT_SUBMISSION.md",
    ROOT / "docs" / "STEWARD_VERIFICATION.md",
    ROOT / "docs" / "QUALITY_BAR.md",
    ROOT / "docs" / "SECURITY.md",
    ROOT / "docs" / "STEWARD_REMEDIATION.md",
]


def _demo():
    return json.loads((ROOT / "frontend" / "public" / "verified-demo.json").read_text())


def test_frontend_and_reviewer_docs_use_one_canonical_contract_address():
    demo = _demo()
    canonical = demo["contract"].lower()

    assert re.fullmatch(r"0x[a-f0-9]{40}", canonical)

    for path in ADDRESS_REFERENCE_FILES:
        text = path.read_text().lower()
        assert canonical in text, f"{path} does not reference canonical contract"
        for stale in OLD_STEWARD_ADDRESSES:
            assert stale not in text, f"{path} still references stale contract {stale}"


def test_reviewer_docs_use_one_successful_canonical_workflow():
    demo = _demo()
    workflow = demo["workflow"]
    assert workflow.endswith("/35993240108")

    for path in WORKFLOW_REFERENCE_FILES:
        text = path.read_text()
        assert workflow in text, f"{path} does not reference canonical workflow"
        for stale in OLD_WORKFLOW_IDS:
            assert stale not in text, f"{path} still references stale workflow {stale}"


def test_frontend_constant_matches_machine_readable_proof():
    demo = _demo()
    source = (ROOT / "frontend" / "lib" / "genlayer.ts").read_text()
    match = re.search(r'CONTRACT_ADDRESS\s*=\s*\n?\s*"(0x[a-fA-F0-9]{40})"', source)
    assert match, "Could not locate CONTRACT_ADDRESS in frontend client"
    assert match.group(1).lower() == demo["contract"].lower()


def test_frontend_uses_machine_proof_as_its_single_reviewer_manifest():
    page = (ROOT / "frontend" / "app" / "page.tsx").read_text()
    assert 'import verifiedDemoData from "../public/verified-demo.json"' in page
    for stale in OLD_STEWARD_ADDRESSES:
        assert stale not in page.lower()


def test_runtime_source_mirror_matches_contract_source_exactly():
    contract_source = (ROOT / "contracts" / "proof_judge.py").read_text().replace("\r\n", "\n").strip()
    mirrored_source = (ROOT / "frontend" / "public" / "deployed-contract-source.txt").read_text().replace("\r\n", "\n").strip()
    assert mirrored_source == contract_source


def test_machine_proof_records_successful_post_deploy_source_attestation():
    demo = _demo()
    source = demo["source"]
    assert source["deployedSourceMatch"] is True
    assert source["deployedNormalizedSha256"] == source["repositoryNormalizedSha256"]
    assert re.fullmatch(r"[a-f0-9]{64}", source["deployedNormalizedSha256"])
    assert re.fullmatch(r"[a-f0-9]{64}", source["deployInputSha256"])


def test_canonical_transaction_proof_is_mirrored_in_reviewer_docs():
    demo = _demo()
    hashes = list(demo["paidOutcome"]["transactions"].values()) + list(
        demo["refundedOutcome"]["transactions"].values()
    )
    for path in [ROOT / "README.md", ROOT / "docs" / "STEWARD_VERIFICATION.md"]:
        text = path.read_text()
        for tx_hash in hashes:
            assert tx_hash in text, f"{path} is missing canonical tx {tx_hash}"


def test_frontend_never_presents_cached_verdict_as_live_state():
    page = (ROOT / "frontend" / "app" / "page.tsx").read_text()
    assert "showing the pinned verified outcomes" not in page
    assert "verifiedJob ||" not in page
    assert "verifiedRefundJob ||" not in page
    assert "no cached verdict is shown" in page
