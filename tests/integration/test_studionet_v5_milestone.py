"""Live V5 verification: ordered two-stage project settlement."""

import hashlib
import time
from pathlib import Path
import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

def _field(value,name):
    return value.get(name) if isinstance(value,dict) else getattr(value,name)

@pytest.mark.integration
def test_proofjudge_v5_composable_project(default_account, accounts):
    assert len(accounts) >= 2
    factory = get_contract_factory(contract_file_path="proof_judge_v5.py")
    local_source = Path("contracts/proof_judge_v5.py").read_text()
    assert factory.contract_code.replace("\r\n","\n").strip() == local_source.replace("\r\n","\n").strip()
    print("PROOFJUDGE_V5_DEPLOY_INPUT_MATCH=true", flush=True)
    print("PROOFJUDGE_V5_DEPLOY_SOURCE_SHA256=" + hashlib.sha256(local_source.encode()).hexdigest(), flush=True)
    contract = factory.deploy(account=default_account, consensus_max_rotations=2)
    print(f"PROOFJUDGE_V5_CONTRACT_ADDRESS={contract.address}", flush=True)

    sponsor = contract.connect(account=default_account)
    contractor_account = accounts[1]
    contractor = contract.connect(account=contractor_account)
    reward = 1_000_000_000_000
    now = int(time.time())
    project = "proofjudge-v5-composable-project"
    stage1 = "proofjudge-v5-protocol"
    stage2 = "proofjudge-v5-sdk"

    a = sponsor.create_milestone(args=[project,stage1,"",str(contractor_account.address),
        "The public evidence must show ProofJudge V5 adds ordered multi-milestone chains, project progress, and participant settlement statistics.",
        "Approve only when both sources directly describe V5 composable milestones and the dependency rule that later stages wait for PAID.",
        now+3600]).transact(value=reward,wait_interval=10000,wait_retries=40)
    assert tx_execution_succeeded(a)
    b = sponsor.create_milestone(args=[project,stage2,stage1,str(contractor_account.address),
        "The public evidence must show a reusable TypeScript SDK for project reads, participant stats, settlement auditing, and write-request builders.",
        "Approve only when both sources directly describe the reusable V5 SDK integration surface for dApps or agents.",
        now+7200]).transact(value=reward,wait_interval=10000,wait_retries=40)
    assert tx_execution_succeeded(b)

    assert int(contract.get_project_job_count(args=[project]).call()) == 2
    assert bool(contract.is_milestone_unlocked(args=[stage2]).call()) is False
    print("PROOFJUDGE_V5_STAGE2_LOCKED_BEFORE_STAGE1_PAID=true", flush=True)

    primary="https://proofjudge-genlayer-frontend.vercel.app/milestone-v5.txt"
    support="https://raw.githubusercontent.com/maho0638/proofjudge-genlayer/main/docs/MILESTONE_V5.md"
    s1=contractor.submit_evidence(args=[stage1,primary,support]).transact(wait_interval=10000,wait_retries=40); assert tx_execution_succeeded(s1)
    r1=sponsor.resolve_job(args=[stage1]).transact(consensus_max_rotations=3,wait_interval=10000,wait_retries=50); assert tx_execution_succeeded(r1)
    j1=contract.get_job(args=[stage1]).call(); assert str(_field(j1,"status"))=="APPROVED"
    c1=contractor.claim_payment(args=[stage1]).transact(wait_interval=10000,wait_retries=40); assert tx_execution_succeeded(c1)
    assert bool(contract.is_milestone_unlocked(args=[stage2]).call()) is True
    print("PROOFJUDGE_V5_STAGE2_UNLOCKED_AFTER_STAGE1_PAID=true", flush=True)

    s2=contractor.submit_evidence(args=[stage2,primary,support]).transact(wait_interval=10000,wait_retries=40); assert tx_execution_succeeded(s2)
    r2=sponsor.resolve_job(args=[stage2]).transact(consensus_max_rotations=3,wait_interval=10000,wait_retries=50); assert tx_execution_succeeded(r2)
    j2=contract.get_job(args=[stage2]).call(); assert str(_field(j2,"status"))=="APPROVED"
    c2=contractor.claim_payment(args=[stage2]).transact(wait_interval=10000,wait_retries=40); assert tx_execution_succeeded(c2)

    p=contract.get_project_progress(args=[project]).call()
    assert int(_field(p,"total_milestones"))==2 and int(_field(p,"paid_milestones"))==2
    stats=contract.get_participant_stats(args=[str(contractor_account.address)]).call()
    assert int(_field(stats,"paid_jobs"))==2 and int(_field(stats,"total_earned"))==reward*2
    print("PROOFJUDGE_V5_COMPOSABLE_PROJECT_VERIFIED=true", flush=True)
