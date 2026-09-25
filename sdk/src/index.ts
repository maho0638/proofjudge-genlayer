import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

export type ContractAddress = `0x${string}`;
export const PROOFJUDGE_V5_POLICY = "PJ_V5_COMPOSABLE_MILESTONES";
export const MIN_APPROVAL_CONFIDENCE = 70;

export type ProofJudgeJob = {
  id?: string; project_id?: string; prerequisite_job_id?: string;
  milestone_index?: string | number | bigint; status?: string;
  confidence?: string | number | bigint; reason_code?: string;
  evidence_basis?: string; primary_snapshot?: string; support_snapshot?: string;
  reward_claimed?: boolean; policy_version?: string;
};
export type ProjectProgress = Record<string, string | number | bigint | undefined>;
export type ParticipantStats = Record<string, string | number | bigint | undefined>;

export function auditSettlement(job: ProofJudgeJob) {
  const status = String(job.status ?? "");
  const confidence = Number(job.confidence ?? 0);
  const resolved = ["APPROVED","REJECTED","CHALLENGED","PAID","REFUNDED"].includes(status);
  const checks = {
    v5Policy: job.policy_version === PROOFJUDGE_V5_POLICY,
    actionableApproval: status !== "APPROVED" || confidence >= MIN_APPROVAL_CONFIDENCE,
    paidWasClaimed: status !== "PAID" || job.reward_claimed === true,
    refundWasSettled: status !== "REFUNDED" || job.reward_claimed === true,
    resolvedHasReason: !resolved || Boolean(job.reason_code),
    resolvedHasEvidenceBasis: !resolved || Boolean(job.evidence_basis),
    resolvedHasSnapshots: !resolved || (Boolean(job.primary_snapshot) && Boolean(job.support_snapshot)),
  };
  return { ok: Object.values(checks).every(Boolean), checks };
}

export class ProofJudgeClient {
  readonly address: ContractAddress;
  private readonly client: any;
  constructor(options: { address: ContractAddress; endpoint?: string }) {
    this.address = options.address;
    const config: any = { chain: studionet };
    if (options.endpoint) config.endpoint = options.endpoint;
    this.client = createClient(config);
  }
  getJob(jobId: string): Promise<ProofJudgeJob> {
    return this.client.readContract({address:this.address,functionName:"get_job",args:[jobId]});
  }
  getProjectProgress(projectId: string): Promise<ProjectProgress> {
    return this.client.readContract({address:this.address,functionName:"get_project_progress",args:[projectId]});
  }
  getParticipantStats(address: string): Promise<ParticipantStats> {
    return this.client.readContract({address:this.address,functionName:"get_participant_stats",args:[address]});
  }
  async isMilestoneUnlocked(jobId: string): Promise<boolean> {
    return Boolean(await this.client.readContract({address:this.address,functionName:"is_milestone_unlocked",args:[jobId]}));
  }
  async listProject(projectId: string): Promise<ProofJudgeJob[]> {
    const raw = await this.client.readContract({address:this.address,functionName:"get_project_job_count",args:[projectId]});
    const count = Number(raw ?? 0);
    const jobs: ProofJudgeJob[] = [];
    for (let i=0;i<count;i+=1) {
      const id = await this.client.readContract({address:this.address,functionName:"get_project_job_id",args:[projectId,BigInt(i)]});
      jobs.push(await this.getJob(String(id)));
    }
    return jobs;
  }
}
export function createMilestoneRequest(p:{address:ContractAddress;projectId:string;jobId:string;prerequisiteJobId?:string;contractor:string;requirement:string;rubric:string;deadline:bigint;reward:bigint}) {
  return {address:p.address,functionName:"create_milestone",args:[p.projectId,p.jobId,p.prerequisiteJobId??"",p.contractor,p.requirement,p.rubric,p.deadline],value:p.reward} as const;
}
export const submitEvidenceRequest = (address:ContractAddress,jobId:string,primary:string,support:string) => ({address,functionName:"submit_evidence",args:[jobId,primary,support]} as const);
export const resolveJobRequest = (address:ContractAddress,jobId:string) => ({address,functionName:"resolve_job",args:[jobId]} as const);
export const challengeRequest = (address:ContractAddress,jobId:string,note:string) => ({address,functionName:"challenge_resolution",args:[jobId,note]} as const);
export const resolveChallengeRequest = (address:ContractAddress,jobId:string) => ({address,functionName:"resolve_challenge",args:[jobId]} as const);
export const claimRequest = (address:ContractAddress,jobId:string) => ({address,functionName:"claim_payment",args:[jobId]} as const);
export const refundRequest = (address:ContractAddress,jobId:string) => ({address,functionName:"refund_expired",args:[jobId]} as const);
