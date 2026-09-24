import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OLD_STEWARD_ADDRESSES = {
    "0x52D23490C660d184b14087007E6B56126ed0B069".lower(),
    "0xA9BDf49634aC02Ce15a2Ad0eF0B220972561FbFc".lower(),
}

REFERENCE_FILES = [
    ROOT / "frontend" / "lib" / "genlayer.ts",
    ROOT / "README.md",
    ROOT / "PROJECT_SUBMISSION.md",
    ROOT / "docs" / "STEWARD_VERIFICATION.md",
    ROOT / "docs" / "QUALITY_BAR.md",
]


def test_frontend_and_reviewer_docs_use_one_canonical_contract_address():
    demo = json.loads((ROOT / "frontend" / "public" / "verified-demo.json").read_text())
    canonical = demo["contract"].lower()

    assert re.fullmatch(r"0x[a-f0-9]{40}", canonical)

    for path in REFERENCE_FILES:
        text = path.read_text()
        assert canonical in text.lower(), f"{path} does not reference canonical contract"
        for stale in OLD_STEWARD_ADDRESSES:
            assert stale not in text.lower(), f"{path} still references stale contract {stale}"


def test_frontend_constant_matches_machine_readable_proof():
    demo = json.loads((ROOT / "frontend" / "public" / "verified-demo.json").read_text())
    source = (ROOT / "frontend" / "lib" / "genlayer.ts").read_text()
    match = re.search(r'CONTRACT_ADDRESS\s*=\s*\n?\s*"(0x[a-fA-F0-9]{40})"', source)
    assert match, "Could not locate CONTRACT_ADDRESS in frontend client"
    assert match.group(1).lower() == demo["contract"].lower()


def test_runtime_source_mirror_matches_contract_source_exactly():
    contract_source = (ROOT / "contracts" / "proof_judge.py").read_text().replace("\r\n", "\n").strip()
    mirrored_source = (ROOT / "frontend" / "public" / "deployed-contract-source.txt").read_text().replace("\r\n", "\n").strip()
    assert mirrored_source == contract_source


def test_frontend_never_presents_cached_verdict_as_live_state():
    page = (ROOT / "frontend" / "app" / "page.tsx").read_text()
    assert "showing the pinned verified outcomes" not in page
    assert "verifiedJob ||" not in page
    assert "verifiedRefundJob ||" not in page
    assert "no cached verdict is shown" in page
