import test from "node:test";
import assert from "node:assert/strict";
import {PROOFJUDGE_V5_POLICY,auditSettlement,createMilestoneRequest} from "../dist/index.js";

test("coherent paid receipt passes",()=>{assert.equal(auditSettlement({status:"PAID",confidence:96,reason_code:"CROSS_CHECK",evidence_basis:"INDEPENDENT_CORROBORATION",primary_snapshot:"a",support_snapshot:"b",reward_claimed:true,policy_version:PROOFJUDGE_V5_POLICY}).ok,true);});
test("low confidence actionable approval fails",()=>{assert.equal(auditSettlement({status:"APPROVED",confidence:55,reason_code:"REQUIREMENT_FIT",evidence_basis:"RUBRIC_MATCH",primary_snapshot:"a",support_snapshot:"b",reward_claimed:false,policy_version:PROOFJUDGE_V5_POLICY}).checks.actionableApproval,false);});
test("milestone request preserves dependency and reward",()=>{const r=createMilestoneRequest({address:"0x1111111111111111111111111111111111111111",projectId:"p",jobId:"b",prerequisiteJobId:"a",contractor:"0x2222222222222222222222222222222222222222",requirement:"requirement long enough for testing",rubric:"rubric long enough for testing",deadline:123n,reward:9n}); assert.equal(r.args[2],"a"); assert.equal(r.value,9n);});
