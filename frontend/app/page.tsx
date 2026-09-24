"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  CONTRACT_ADDRESS,
  formatGen,
  parseGen,
  readClient,
  sendWrite,
  walletClient,
} from "../lib/genlayer";

type JobView = {
  id?: string;
  sponsor?: string;
  contractor?: string;
  requirement?: string;
  rubric?: string;
  reward?: string | number | bigint;
  deadline?: string | number | bigint;
  status?: string;
  evidence_url?: string;
  support_url?: string;
  attempt_count?: string | number | bigint;
  confidence?: string | number | bigint;
  reason_code?: string;
  evidence_basis?: string;
  primary_snapshot?: string;
  support_snapshot?: string;
  rationale?: string;
  reward_claimed?: boolean;
  challenge_count?: string | number | bigint;
  challenge_note?: string;
  created_at?: string | number | bigint;
  submitted_at?: string | number | bigint;
  resolved_at?: string | number | bigint;
  challenged_at?: string | number | bigint;
  settled_at?: string | number | bigint;
  policy_version?: string;
};

type ActivityItem = {
  label: string;
  hash: string;
  jobId: string;
};

const explorerBase = "https://explorer-studio.genlayer.com";
const verifiedDemo = {
  contract: "0x699f62FA0f53B92D85949B1F046f6B50209707eE",
  jobId: "proofjudge-production-milestone-v3",
  workflow: "https://github.com/maho0638/proofjudge-genlayer/actions/runs/35985412296",
  expected: {
    id: "proofjudge-production-milestone-v3",
    status: "PAID",
    confidence: 98,
    reason_code: "CROSS_CHECK",
    evidence_basis: "INDEPENDENT_CORROBORATION",
    reward_claimed: true,
    challenge_count: 0,
    attempt_count: 1,
    evidence_url: "https://proofjudge-genlayer-frontend.vercel.app",
    support_url: "https://raw.githubusercontent.com/maho0638/proofjudge-genlayer/main/README.md",
    rationale:
      "Approved because independent support corroborates the primary evidence. Confidence 98/100.",
    policy_version: "PJ_V4_SNAPSHOT_CHALLENGE",
  } satisfies JobView,
  transactions: [
    ["Create escrow", "0xb9cdb9211b7775911b70e4af93b0408644c5d9ddafb0123d20fbcfc20dd62c9b"],
    ["Submit evidence", "0x82e871f6510cf5e8af66e778a7b879e4a19d04f01c717103862d43bd5c19eb6d"],
    ["Resolve consensus", "0x3fa02241eb60d23604ab3bde2d1eee9334794557f73af280f3ae3abdc2752bef"],
    ["Claim payment", "0x8c98e573115a3a41a28456c59aa4eef1060ab1fdc713a69db74b50bd05d18013"],
  ] as const,
  refund: {
    jobId: "irrelevant-evidence-refund-v1",
    expected: {
      id: "irrelevant-evidence-refund-v1",
      status: "REFUNDED",
      confidence: 2,
      reason_code: "EVIDENCE_GAP",
      reward_claimed: true,
      attempt_count: 1,
      evidence_url: "https://example.com",
      support_url: "https://www.iana.org/help/example-domains",
      rationale:
        "Rejected because the submitted evidence is insufficient or ambiguous. Confidence 2/100.",
      policy_version: "PJ_V4_SNAPSHOT_CHALLENGE",
    } satisfies JobView,
    transactions: [
      ["Create escrow", "0xd29492ee5f16e2d595b6792d17058c325ab0a9b4456cd7763eedfa2a01ebf637"],
      ["Submit irrelevant evidence", "0xa790bb59991bd38e6e211cebcccba62fe2ea3870d1163cb1313d47dc7eeb18d0"],
      ["Consensus rejects", "0xdab3ff727e806eda7b716290eececea0def16f2b5fd846cb1f29a89d21c86dfb"],
      ["Sponsor refund", "0x794aabd5d29b0391503a969108342b96a350e654bcea8d9ad2831810d94f05dc"],
    ] as const,
  },
};

function short(value?: string) {
  if (!value) return "—";
  if (value.length < 18) return value;
  return `${value.slice(0, 8)}…${value.slice(-6)}`;
}

function validHttps(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "https:";
  } catch {
    return false;
  }
}

function host(value: string) {
  try {
    return new URL(value).hostname.replace(/^www\./, "").toLowerCase();
  } catch {
    return "";
  }
}

function deadlineText(value?: string | number | bigint) {
  try {
    const n = Number(value ?? 0);
    if (!n) return "—";
    return new Date(n * 1000).toLocaleString();
  } catch {
    return "—";
  }
}

export default function Home() {
  const [account, setAccount] = useState("");
  const [notice, setNotice] = useState("System ready");
  const [busy, setBusy] = useState("");
  const [workspace, setWorkspace] = useState<"sponsor" | "contractor" | "settlement">("sponsor");

  const [verifiedJob, setVerifiedJob] = useState<JobView | null>(null);
  const [verifiedRefundJob, setVerifiedRefundJob] = useState<JobView | null>(null);
  const [verifiedProofState, setVerifiedProofState] = useState<"loading" | "live" | "error">("loading");
  const [sourceMatch, setSourceMatch] = useState<"loading" | "match" | "mismatch" | "error">("loading");
  const [jobs, setJobs] = useState<JobView[]>([]);
  const [marketState, setMarketState] = useState("Loading on-chain agreements…");

  const [jobId, setJobId] = useState("");
  const [contractor, setContractor] = useState("");
  const [requirement, setRequirement] = useState("");
  const [rubric, setRubric] = useState("");
  const [reward, setReward] = useState("0.001");
  const [deadline, setDeadline] = useState("");

  const [submitJobId, setSubmitJobId] = useState(verifiedDemo.jobId);
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [supportUrl, setSupportUrl] = useState("");

  const [settlementId, setSettlementId] = useState(verifiedDemo.jobId);
  const [challengeNote, setChallengeNote] = useState("");
  const [loadedJob, setLoadedJob] = useState<JobView | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);

  function recordActivity(label: string, hash: string, id: string) {
    setActivity((items) => [{ label, hash, jobId: id }, ...items].slice(0, 6));
  }

  async function connectWallet() {
    try {
      const { account: next } = await walletClient();
      setAccount(next);
      setNotice(`Wallet connected: ${short(next)}`);
    } catch (error: any) {
      setNotice(error?.message || "Wallet connection failed");
    }
  }

  async function loadVerified() {
    setVerifiedProofState("loading");
    setSourceMatch("loading");
    try {
      const client: any = readClient();
      const paid: any = await client.readContract({
        address: CONTRACT_ADDRESS,
        functionName: "get_job",
        args: [verifiedDemo.jobId],
      });
      const refunded: any = await client.readContract({
        address: CONTRACT_ADDRESS,
        functionName: "get_job",
        args: [verifiedDemo.refund.jobId],
      });
      setVerifiedJob(paid as JobView);
      setVerifiedRefundJob(refunded as JobView);
      setVerifiedProofState("live");

      try {
        const deployedSource: any = await client.getContractCode({ address: CONTRACT_ADDRESS });
        const pinnedSource = await fetch("/deployed-contract-source.txt", { cache: "no-store" }).then((response) => {
          if (!response.ok) throw new Error("Pinned source unavailable");
          return response.text();
        });
        const normalizeSource = (value: unknown) =>
          String(value ?? "").replace(/\r\n/g, "\n").trim();
        setSourceMatch(
          normalizeSource(deployedSource) === normalizeSource(pinnedSource)
            ? "match"
            : "mismatch"
        );
      } catch {
        setSourceMatch("error");
      }
    } catch {
      setVerifiedJob(null);
      setVerifiedRefundJob(null);
      setVerifiedProofState("error");
      setSourceMatch("error");
    }
  }

  async function loadMarket() {
    try {
      const client: any = readClient();
      const rawCount: any = await client.readContract({
        address: CONTRACT_ADDRESS,
        functionName: "get_job_count",
        args: [],
      });
      const count = Number(rawCount ?? 0);
      const start = Math.max(0, count - 6);
      const items: JobView[] = [];

      for (let i = count - 1; i >= start; i--) {
        const id: any = await client.readContract({
          address: CONTRACT_ADDRESS,
          functionName: "get_job_id",
          args: [BigInt(i)],
        });
        const job: any = await client.readContract({
          address: CONTRACT_ADDRESS,
          functionName: "get_job",
          args: [String(id)],
        });
        items.push(job as JobView);
      }

      setJobs(items);
      setMarketState(count ? `${count} agreement${count === 1 ? "" : "s"} indexed on-chain` : "No agreements indexed yet");
    } catch {
      setJobs([]);
      setMarketState("On-chain discovery temporarily unavailable");
    }
  }

  async function loadJob(id = settlementId) {
    if (!id.trim()) return setNotice("Enter a job ID.");
    try {
      setBusy("read");
      const data: any = await readClient().readContract({
        address: CONTRACT_ADDRESS,
        functionName: "get_job",
        args: [id.trim()],
      });
      setLoadedJob(data as JobView);
      setSettlementId(id.trim());
      setNotice(`Loaded ${id.trim()} from Studionet`);
    } catch (error: any) {
      setLoadedJob(null);
      setNotice(error?.message || "Job read failed");
    } finally {
      setBusy("");
    }
  }

  async function refreshAfterWrite(id: string) {
    await loadMarket();
    if (id) await loadJob(id);
    if (id === verifiedDemo.jobId) await loadVerified();
  }

  async function createJob(event: FormEvent) {
    event.preventDefault();
    try {
      if (!jobId.trim()) throw new Error("Job ID is required.");
      if (!/^0x[a-fA-F0-9]{40}$/.test(contractor.trim())) {
        throw new Error("Contractor must be a valid 0x wallet address.");
      }
      if (requirement.trim().length < 20) throw new Error("Write a clear acceptance requirement.");
      if (rubric.trim().length < 20) throw new Error("Write a clear judging rubric.");
      if (!deadline) throw new Error("Choose a deadline.");
      const timestamp = Math.floor(new Date(deadline).getTime() / 1000);
      if (!Number.isFinite(timestamp) || timestamp <= Math.floor(Date.now() / 1000)) {
        throw new Error("Deadline must be in the future.");
      }

      setBusy("create");
      setNotice("Creating agreement and locking native GEN…");
      const hash = await sendWrite({
        address: CONTRACT_ADDRESS,
        functionName: "create_job",
        args: [
          jobId.trim(),
          contractor.trim(),
          requirement.trim(),
          rubric.trim(),
          BigInt(timestamp),
        ],
        value: parseGen(reward),
      });
      setNotice(`Escrow created: ${short(hash)}`);
      recordActivity("Create escrow", hash, jobId.trim());
      setSettlementId(jobId.trim());
      await refreshAfterWrite(jobId.trim());
      setWorkspace("settlement");
    } catch (error: any) {
      setNotice(error?.message || "Create failed");
    } finally {
      setBusy("");
    }
  }

  async function submitEvidence(event: FormEvent) {
    event.preventDefault();
    try {
      if (!submitJobId.trim()) throw new Error("Job ID is required.");
      if (!validHttps(evidenceUrl) || !validHttps(supportUrl)) {
        throw new Error("Both evidence URLs must use HTTPS.");
      }
      if (evidenceUrl.trim() === supportUrl.trim() || host(evidenceUrl) === host(supportUrl)) {
        throw new Error("Evidence must come from two distinct hostnames.");
      }

      setBusy("submit");
      setNotice("Submitting independent evidence to the contract…");
      const hash = await sendWrite({
        address: CONTRACT_ADDRESS,
        functionName: "submit_evidence",
        args: [submitJobId.trim(), evidenceUrl.trim(), supportUrl.trim()],
      });
      setNotice(`Evidence submitted: ${short(hash)}`);
      recordActivity("Submit evidence", hash, submitJobId.trim());
      setSettlementId(submitJobId.trim());
      await refreshAfterWrite(submitJobId.trim());
      setWorkspace("settlement");
    } catch (error: any) {
      setNotice(error?.message || "Evidence submission failed");
    } finally {
      setBusy("");
    }
  }

  async function settle(action: "resolve_job" | "resolve_challenge" | "claim_payment" | "refund_expired") {
    try {
      if (!settlementId.trim()) throw new Error("Job ID is required.");
      setBusy(action);
      const label =
        action === "resolve_job"
          ? "Running validator consensus…"
          : action === "resolve_challenge"
            ? "Re-running consensus for challenged decision…"
          : action === "claim_payment"
            ? "Claiming approved escrow…"
            : "Requesting guarded refund…";
      setNotice(label);

      const hash = await sendWrite({
        address: CONTRACT_ADDRESS,
        functionName: action,
        args: [settlementId.trim()],
      });
      const activityLabel =
        action === "resolve_job"
          ? "Resolve consensus"
          : action === "resolve_challenge"
            ? "Resolve challenge"
          : action === "claim_payment"
            ? "Claim payment"
            : "Refund expired";
      setNotice(`${action.replace("_", " ")} finalized: ${short(hash)}`);
      recordActivity(activityLabel, hash, settlementId.trim());
      await refreshAfterWrite(settlementId.trim());
    } catch (error: any) {
      setNotice(error?.message || "Transaction failed");
    } finally {
      setBusy("");
    }
  }

  async function challengeResolution() {
    try {
      if (!settlementId.trim()) throw new Error("Job ID is required.");
      if (challengeNote.trim().length < 20) {
        throw new Error("Explain the challenge in at least 20 characters.");
      }
      setBusy("challenge_resolution");
      setNotice("Submitting one-time settlement challenge…");
      const hash = await sendWrite({
        address: CONTRACT_ADDRESS,
        functionName: "challenge_resolution",
        args: [settlementId.trim(), challengeNote.trim()],
      });
      setNotice(`Challenge finalized: ${short(hash)}`);
      recordActivity("Challenge decision", hash, settlementId.trim());
      await refreshAfterWrite(settlementId.trim());
    } catch (error: any) {
      setNotice(error?.message || "Challenge failed");
    } finally {
      setBusy("");
    }
  }

  useEffect(() => {
    loadVerified();
    loadMarket();
    loadJob(verifiedDemo.jobId);
  }, []);

  const canonicalJob = verifiedJob;
  const canonicalRefund = verifiedRefundJob;

  const integrityChecks = useMemo(
    () =>
      [
        ["Contract address", CONTRACT_ADDRESS.toLowerCase() === verifiedDemo.contract.toLowerCase()],
        ["Deployed source", sourceMatch === "match"],
        ["Paid job ID", canonicalJob?.id === verifiedDemo.expected.id],
        ["Paid status", canonicalJob?.status === "PAID"],
        ["Paid confidence", Number(canonicalJob?.confidence ?? -1) === 98],
        ["Paid reason", canonicalJob?.reason_code === "CROSS_CHECK"],
        ["Evidence basis", canonicalJob?.evidence_basis === "INDEPENDENT_CORROBORATION"],
        ["Evidence snapshots", Boolean(canonicalJob?.primary_snapshot) && Boolean(canonicalJob?.support_snapshot)],
        ["Paid reward", canonicalJob?.reward_claimed === true],
        ["Policy v4", canonicalJob?.policy_version === "PJ_V4_SNAPSHOT_CHALLENGE"],
        ["Independent evidence", host(String(canonicalJob?.evidence_url ?? "")) !== host(String(canonicalJob?.support_url ?? ""))],
        ["Refund job ID", canonicalRefund?.id === verifiedDemo.refund.expected.id],
        ["Rejected evidence", Number(canonicalRefund?.confidence ?? -1) === 2 && canonicalRefund?.reason_code === "EVIDENCE_GAP"],
        ["Refunded status", canonicalRefund?.status === "REFUNDED"],
        ["Refund settled", canonicalRefund?.reward_claimed === true],
      ] as const,
    [canonicalJob, canonicalRefund, sourceMatch]
  );

  const integrityPassed = integrityChecks.filter(([, passed]) => passed).length;
  const integrityComplete =
    verifiedProofState === "live" && integrityPassed === integrityChecks.length;

  const normalizedAccount = account.toLowerCase();
  const sponsorAddress = String(loadedJob?.sponsor || "").toLowerCase();
  const contractorAddress = String(loadedJob?.contractor || "").toLowerCase();
  const connectedRole =
    !normalizedAccount
      ? "Wallet not connected"
      : normalizedAccount === sponsorAddress
        ? "Sponsor"
        : normalizedAccount === contractorAddress
          ? "Assigned contractor"
          : "Observer";
  const paidCount = jobs.filter((job) => job.status === "PAID").length;
  const refundedCount = jobs.filter((job) => job.status === "REFUNDED").length;
  const pendingCount = jobs.filter((job) => !["PAID", "REFUNDED"].includes(String(job.status))).length;

  return (
    <main>
      <nav className="nav">
        <a className="brand" href="#top">
          <img className="brandLogo" src="/proofjudge-logo.png" alt="ProofJudge logo" />
          <span><b>ProofJudge</b><small>CONSENSUS MILESTONE ESCROW</small></span>
        </a>
        <div className="navLinks">
          <a href="#review">Review</a>
          <a href="#agreements">Agreements</a>
          <a href="#proof">Live proof</a>
          <a href="#workspace">Workspace</a>
          <a href="#why">Why GenLayer</a>
        </div>
        <button className="wallet" onClick={connectWallet}>
          <i />{account ? short(account) : "Connect wallet"}
        </button>
      </nav>

      <section className="hero" id="top">
        <div className="heroCopy">
          <div className="networkPill"><i /> LIVE ON STUDIONET <span>CHAIN 61999</span></div>
          <p className="kicker">ESCROW + LIVE EVIDENCE + VALIDATOR CONSENSUS</p>
          <h1>Ship the milestone.<br /><em>Prove it.</em> Get paid.</h1>
          <p className="lede">
            ProofJudge turns subjective deliverable acceptance into an on-chain settlement.
            A sponsor locks native GEN, the assigned contractor submits public evidence,
            and GenLayer decides whether the precommitted acceptance criteria were met.
          </p>
          <div className="heroActions">
            <a className="primaryCta" href="#workspace" onClick={() => setWorkspace("sponsor")}>Create an agreement</a>
            <a className="ghostCta" href="#proof">Inspect verified settlement</a>
          </div>
          <div className="microProof">
            <span>✓ Native GEN escrow</span><span>✓ Two independent evidence domains</span><span>✓ Winnerless bilateral settlement</span>
          </div>
        </div>

        <aside className="protocolCard">
          <div className="protocolHead">
            <div><img className="protocolLogo" src="/proofjudge-logo.png" alt="" aria-hidden="true" /><div><small>PROOFJUDGE PROTOCOL</small><b>Evidence-backed payout</b></div></div>
            <span className="chainBadge">61999</span>
          </div>
          <div className="protocolLive"><i /> {verifiedProofState === "live" ? "STUDIONET VERIFIED" : verifiedProofState === "error" ? "RPC CHECK DEGRADED" : "VERIFYING STUDIONET"} <b>GEN</b></div>
          <div className="protocolSteps">
            <div><span>01</span><b>Lock escrow</b><small>Sponsor commits value</small></div>
            <div><span>02</span><b>Submit proof</b><small>Contractor provides evidence</small></div>
            <div><span>03</span><b>Consensus</b><small>Validators re-check the web</small></div>
            <div><span>04</span><b>Claim payout</b><small>Only approved work unlocks GEN</small></div>
          </div>
          <div className="contractLine"><span>Contract</span><code>{short(CONTRACT_ADDRESS)}</code><a href={`${explorerBase}/address/${CONTRACT_ADDRESS}`} target="_blank">Explorer ↗</a></div>
        </aside>
      </section>

      <section className="metrics">
        <div><strong>1:1</strong><span>sponsor ↔ contractor</span></div>
        <div><strong>2 URLs</strong><span>independent evidence</span></div>
        <div><strong>3</strong><span>max evidence attempts</span></div>
        <div><strong>GEN</strong><span>native escrow & payout</span></div>
      </section>

      <section className="featureRow">
        <article><span className="featureIcon">◎</span><div><b>Escrow before work</b><p>The sponsor cannot create an agreement without locking a positive native GEN reward.</p></div></article>
        <article><span className="featureIcon">↗</span><div><b>Independent proof</b><p>The deliverable and corroborating evidence must use separate HTTPS hostnames.</p></div></article>
        <article><span className="featureIcon">✦</span><div><b>Consensus before payout</b><p>Validators independently fetch and judge the same evidence before claim becomes possible.</p></div></article>
      </section>

      <section className="reviewFastTrack" id="review">
        <div className="reviewIntro">
          <div>
            <p className="kicker">REVIEWER FAST TRACK</p>
            <h2>Audit the product in under a minute.</h2>
            <p>
              No wallet, seeded UI state or private dashboard is required. Every claim below
              links to a live contract read, finalized Studionet transaction, reproducible CI
              workflow or settlement-critical source file.
            </p>
          </div>
          <div className="reviewOutcomeStack">
            <div className="outcomeChip paid"><small>GOOD EVIDENCE</small><b>98/100 → PAID</b><span>contractor claimed GEN</span></div>
            <div className="outcomeChip refunded"><small>BAD EVIDENCE</small><b>2/100 → REFUNDED</b><span>contractor payout stayed locked</span></div>
          </div>
        </div>
        <div className="reviewLinks">
          <a href="#proof"><span>01</span><div><b>Read two live outcomes</b><small>12 contract checks · no wallet</small></div><i>↓</i></a>
          <a href={`${explorerBase}/address/${CONTRACT_ADDRESS}`} target="_blank" rel="noreferrer"><span>02</span><div><b>Inspect Studionet contract</b><small>escrow · resolve · payout · refund</small></div><i>↗</i></a>
          <a href={verifiedDemo.workflow} target="_blank" rel="noreferrer"><span>03</span><div><b>Reproduce both paths</b><small>fresh deployment in CI</small></div><i>↗</i></a>
          <a href="/verified-demo.json" target="_blank" rel="noreferrer"><span>04</span><div><b>Open machine proof</b><small>canonical IDs · results · tx hashes</small></div><i>↗</i></a>
        </div>
      </section>

      <section className="section" id="agreements">
        <div className="sectionHead">
          <div><p className="kicker">ON-CHAIN DISCOVERY</p><h2>Milestone agreements,<br />indexed by the contract.</h2></div>
          <div className="healthPill"><i /> {marketState}</div>
        </div>
        <div className="marketSummary">
          <div><small>Indexed</small><b>{jobs.length}</b></div>
          <div><small>Paid</small><b>{paidCount}</b></div>
          <div><small>Refunded</small><b>{refundedCount}</b></div>
          <div><small>Active / unresolved</small><b>{pendingCount}</b></div>
        </div>
        <div className="marketGrid">
          {jobs.length ? jobs.map((job) => (
            <button className="marketCard" key={String(job.id)} onClick={() => { setSettlementId(String(job.id)); loadJob(String(job.id)); setWorkspace("settlement"); document.getElementById("workspace")?.scrollIntoView({ behavior: "smooth" }); }}>
              <div><span className={`statusTag ${String(job.status || "").toLowerCase()}`}>{job.status || "UNKNOWN"}</span><small>{formatGen(job.reward)}</small></div>
              <b>{job.id}</b>
              <p>{job.requirement}</p>
              <footer><span>{Number(job.attempt_count ?? 0)} attempt(s)</span><span>Confidence {Number(job.confidence ?? 0)}/100</span></footer>
            </button>
          )) : <div className="emptyMarket">{marketState}</div>}
        </div>
      </section>

      <section className="section proofSection" id="proof">
        <div className="sectionHead proofTitle">
          <div>
            <p className="kicker">VERIFIED LIVE PROOF</p>
            <h2>Correct work gets paid.<br />Bad evidence does not.</h2>
            <p>
              No wallet is required to audit these two real Studionet outcomes. The same
              Intelligent Contract paid a verified ProofJudge production milestone and
              rejected irrelevant evidence before returning that escrow to the sponsor.
            </p>
          </div>
          <a className="outlineLink" href={verifiedDemo.workflow} target="_blank" rel="noreferrer">Open verification workflow ↗</a>
        </div>

        <div className={`systemStatus ${verifiedProofState === "live" ? "good" : ""}`}>
          <i />
          {verifiedProofState === "live"
            ? "Two live contract outcomes verified directly from Studionet"
            : verifiedProofState === "error"
              ? "Live RPC unavailable — no cached verdict is shown; use Explorer and CI proof while live state is unavailable"
              : "Verifying paid and refunded outcomes from Studionet…"}
        </div>

        <div className={`integrityPanel ${integrityComplete ? "pass" : verifiedProofState === "error" ? "fallback" : ""}`}>
          <div className="integrityTop">
            <div>
              <small>REVIEWER INTEGRITY GATE</small>
              <strong>
                {verifiedProofState === "live"
                  ? `${integrityPassed}/${integrityChecks.length} live checks match`
                  : verifiedProofState === "error"
                    ? "Live state unavailable — cached verdict disabled"
                    : "Checking both economic outcomes…"}
              </strong>
            </div>
            <b>{integrityComplete ? "PASS" : verifiedProofState === "error" ? "FALLBACK" : "VERIFYING"}</b>
          </div>
          <div className="integrityChecks">
            {integrityChecks.map(([label, passed]) => (
              <div key={label}>
                <i className={verifiedProofState === "live" && passed ? "ok" : ""} />
                <span>{label}</span>
                <b>{verifiedProofState === "live" ? (passed ? "MATCH" : "MISMATCH") : "—"}</b>
              </div>
            ))}
          </div>
        </div>

        <div className="proofGrid">
          <article className="settlementCard">
            <div className="cardTitle">
              <span><i /> Outcome A · production release</span>
              <a href={`${explorerBase}/address/${CONTRACT_ADDRESS}`} target="_blank" rel="noreferrer">Contract ↗</a>
            </div>
            <div className="settlementStats">
              <div><small>Job</small><b>{canonicalJob?.id || "Loading…"}</b></div>
              <div><small>Status</small><b>{canonicalJob?.status || "Loading…"}</b></div>
              <div><small>Confidence</small><b>{canonicalJob ? `${Number(canonicalJob.confidence ?? 0)}/100` : "Loading…"}</b></div>
              <div><small>Stored reason</small><b>{canonicalJob?.reason_code || "Loading…"}</b></div>
              <div><small>Reward claimed</small><b>{canonicalJob ? (canonicalJob.reward_claimed ? "Yes" : "No") : "Loading…"}</b></div>
              <div><small>Policy</small><b>{canonicalJob?.policy_version || "Loading…"}</b></div>
            </div>
            <blockquote>{canonicalJob?.rationale || "Loading the verified settlement rationale…"}</blockquote>
            <div className="evidencePair">
              <a href={String(canonicalJob?.evidence_url || verifiedDemo.expected.evidence_url)} target="_blank" rel="noreferrer">
                <small>LIVE PRODUCTION DELIVERABLE</small>
                <b>{host(String(canonicalJob?.evidence_url || verifiedDemo.expected.evidence_url))}</b><span>Open ↗</span>
              </a>
              <a href={String(canonicalJob?.support_url || verifiedDemo.expected.support_url)} target="_blank" rel="noreferrer">
                <small>INDEPENDENT REPOSITORY SUPPORT</small>
                <b>{host(String(canonicalJob?.support_url || verifiedDemo.expected.support_url))}</b><span>Open ↗</span>
              </a>
            </div>
          </article>

          <article className="txCard">
            <div className="cardTitle"><span>Paid lifecycle</span><small>4 finalized transactions</small></div>
            <div className="txList">
              {verifiedDemo.transactions.map(([label, hash], index) => (
                <a key={hash} href={`${explorerBase}/tx/${hash}`} target="_blank" rel="noreferrer">
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <div><b>{label}</b><code>{short(hash)}</code></div><i>↗</i>
                </a>
              ))}
            </div>
          </article>

          <article className="settlementCard refundCard">
            <div className="cardTitle">
              <span><i /> Outcome B · bad evidence</span>
              <small>Payout blocked → sponsor refunded</small>
            </div>
            <div className="settlementStats">
              <div><small>Job</small><b>{canonicalRefund?.id || "Loading…"}</b></div>
              <div><small>Final status</small><b>{canonicalRefund?.status || "Loading…"}</b></div>
              <div><small>Decision confidence</small><b>{canonicalRefund ? `${Number(canonicalRefund.confidence ?? 0)}/100` : "Loading…"}</b></div>
              <div><small>Stored reason</small><b>{canonicalRefund?.reason_code || "Loading…"}</b></div>
              <div><small>Escrow settled</small><b>{canonicalRefund ? (canonicalRefund.reward_claimed ? "Yes" : "No") : "Loading…"}</b></div>
              <div><small>Policy</small><b>{canonicalRefund?.policy_version || "Loading…"}</b></div>
            </div>
            <blockquote>{canonicalRefund?.rationale || "Loading the rejected-evidence rationale…"}</blockquote>
            <div className="outcomeNote">
              <b>Economic safety proved</b>
              <span>Consensus rejected irrelevant evidence at 2/100. Contractor payout never opened; after deadline the sponsor recovered the escrow.</span>
            </div>
          </article>

          <article className="txCard">
            <div className="cardTitle"><span>Reject + refund lifecycle</span><small>4 finalized transactions</small></div>
            <div className="txList">
              {verifiedDemo.refund.transactions.map(([label, hash], index) => (
                <a key={hash} href={`${explorerBase}/tx/${hash}`} target="_blank" rel="noreferrer">
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <div><b>{label}</b><code>{short(hash)}</code></div><i>↗</i>
                </a>
              ))}
            </div>
          </article>
        </div>
      </section>

      <section className="section workspaceSection" id="workspace">
        <div className="sectionHead">
          <div><p className="kicker">PROTOCOL WORKSPACE</p><h2>Run the full agreement lifecycle.</h2><p>Every write is sent directly to the Intelligent Contract and waits for GenLayer finalization before the UI reports success.</p></div>
          <div className="notice"><i /> {notice}</div>
        </div>

        <div className="workspace">
          <div className="workspaceTabs">
            <button className={workspace === "sponsor" ? "active" : ""} onClick={() => setWorkspace("sponsor")}><span>01</span><b>Create agreement</b><small>Sponsor</small></button>
            <button className={workspace === "contractor" ? "active" : ""} onClick={() => setWorkspace("contractor")}><span>02</span><b>Submit evidence</b><small>Contractor</small></button>
            <button className={workspace === "settlement" ? "active" : ""} onClick={() => setWorkspace("settlement")}><span>03</span><b>Resolve & settle</b><small>Consensus</small></button>
          </div>

          <div className="workspacePanel">
            {workspace === "sponsor" && (
              <form onSubmit={createJob}>
                <div className="panelTitle"><span>01</span><div><h3>Create a milestone escrow</h3><p>Lock GEN behind explicit acceptance criteria and one assigned contractor.</p></div></div>
                <div className="formGrid">
                  <label>Job ID<input value={jobId} onChange={(e) => setJobId(e.target.value)} placeholder="website-milestone-1" /></label>
                  <label>Contractor wallet<input value={contractor} onChange={(e) => setContractor(e.target.value)} placeholder="0x…" /></label>
                  <label>Reward (GEN)<input value={reward} onChange={(e) => setReward(e.target.value)} inputMode="decimal" /></label>
                  <label>Deadline<input type="datetime-local" value={deadline} onChange={(e) => setDeadline(e.target.value)} /></label>
                  <label className="wide">Acceptance requirement<textarea value={requirement} onChange={(e) => setRequirement(e.target.value)} placeholder="Describe exactly what must be delivered…" /></label>
                  <label className="wide">Precommitted rubric<textarea value={rubric} onChange={(e) => setRubric(e.target.value)} placeholder="Define what evidence counts, what must be direct, and what should cause rejection…" /></label>
                </div>
                <div className="formFooter"><span>GEN is escrowed when this transaction finalizes.</span><button disabled={!!busy}>{busy === "create" ? "Creating…" : "Lock GEN & create"}</button></div>
              </form>
            )}

            {workspace === "contractor" && (
              <form onSubmit={submitEvidence}>
                <div className="panelTitle"><span>02</span><div><h3>Submit independent evidence</h3><p>Only the assigned contractor can submit. Rejected work may be retried up to three times before the deadline.</p></div></div>
                <div className="formGrid">
                  <label className="wide">Job ID<input value={submitJobId} onChange={(e) => setSubmitJobId(e.target.value)} /></label>
                  <label>Primary deliverable URL<input value={evidenceUrl} onChange={(e) => setEvidenceUrl(e.target.value)} placeholder="https://your-deliverable.example/…" /></label>
                  <label>Independent support URL<input value={supportUrl} onChange={(e) => setSupportUrl(e.target.value)} placeholder="https://independent-source.example/…" /></label>
                </div>
                <div className="preflight">
                  <span className={validHttps(evidenceUrl) ? "ok" : ""}>HTTPS primary</span>
                  <span className={validHttps(supportUrl) ? "ok" : ""}>HTTPS support</span>
                  <span className={host(evidenceUrl) && host(supportUrl) && host(evidenceUrl) !== host(supportUrl) ? "ok" : ""}>Distinct domains</span>
                </div>
                <div className="formFooter"><span>Evidence is judged from the live public web.</span><button disabled={!!busy}>{busy === "submit" ? "Submitting…" : "Submit evidence"}</button></div>
              </form>
            )}

            {workspace === "settlement" && (
              <div>
                <div className="panelTitle"><span>03</span><div><h3>Judge and settle</h3><p>Resolution is permissionless. Payout and refund remain role-gated by the contract.</p></div></div>
                <div className="roleBar">
                  <span><i /> Connected role</span>
                  <b>{connectedRole}</b>
                  {account && <code>{short(account)}</code>}
                </div>
                <div className="settleControls">
                  <label>Job ID<input value={settlementId} onChange={(e) => setSettlementId(e.target.value)} /></label>
                  <button className="secondaryBtn" onClick={() => loadJob()} disabled={!!busy}>{busy === "read" ? "Reading…" : "Read state"}</button>
                  <button onClick={() => settle("resolve_job")} disabled={!!busy || loadedJob?.status !== "SUBMITTED"}>{busy === "resolve_job" ? "Resolving…" : "Resolve by consensus"}</button>
                  <button
                    className="secondaryBtn"
                    onClick={() => settle("claim_payment")}
                    disabled={
                      !!busy ||
                      loadedJob?.status !== "APPROVED" ||
                      (!!account && normalizedAccount !== contractorAddress)
                    }
                  >{busy === "claim_payment" ? "Claiming…" : "Claim payment"}</button>
                  <button
                    className="secondaryBtn"
                    onClick={() => settle("refund_expired")}
                    disabled={
                      !!busy ||
                      !["OPEN", "REJECTED"].includes(String(loadedJob?.status)) ||
                      (!!account && normalizedAccount !== sponsorAddress)
                    }
                  >{busy === "refund_expired" ? "Refunding…" : "Refund expired"}</button>
                </div>
                {loadedJob ? (
                  <div className="loadedState">
                    <div className="stateHeader"><div><small>ON-CHAIN AGREEMENT</small><h3>{loadedJob.id}</h3></div><span className={`statusTag ${String(loadedJob.status || "").toLowerCase()}`}>{loadedJob.status}</span></div>
                    <p>{loadedJob.requirement}</p>
                    <div className="stateGrid">
                      <div><small>Escrow</small><b>{formatGen(loadedJob.reward)}</b></div>
                      <div><small>Contractor</small><b>{short(loadedJob.contractor)}</b></div>
                      <div><small>Attempts</small><b>{Number(loadedJob.attempt_count ?? 0)}/3</b></div>
                      <div><small>Confidence</small><b>{Number(loadedJob.confidence ?? 0)}/100</b></div>
                      <div><small>Deadline</small><b>{deadlineText(loadedJob.deadline)}</b></div>
                      <div><small>Reward claimed</small><b>{loadedJob.reward_claimed ? "Yes" : "No"}</b></div>
                      <div><small>Policy</small><b>{loadedJob.policy_version || "Legacy"}</b></div>
                      <div><small>Created</small><b>{deadlineText(loadedJob.created_at)}</b></div>
                      <div><small>Submitted</small><b>{deadlineText(loadedJob.submitted_at)}</b></div>
                      <div><small>Resolved</small><b>{deadlineText(loadedJob.resolved_at)}</b></div>
                      <div><small>Settled</small><b>{deadlineText(loadedJob.settled_at)}</b></div>
                    </div>
                    {loadedJob.rationale && <blockquote>{loadedJob.rationale}</blockquote>}
                  </div>
                ) : <div className="statePlaceholder">Load a job to inspect its contract state.</div>}
              </div>
            )}
          </div>
        </div>

        <div className="activityPanel">
          <div className="activityHead">
            <div><small>FINALIZED WRITE ACTIVITY</small><b>Explorer-verifiable transaction trail</b></div>
            <span>{activity.length ? `${activity.length} recent` : "No writes in this session"}</span>
          </div>
          {activity.length ? (
            <div className="activityList">
              {activity.map((item) => (
                <a key={item.hash} href={`${explorerBase}/tx/${item.hash}`} target="_blank" rel="noreferrer">
                  <div><b>{item.label}</b><small>{item.jobId}</small></div>
                  <code>{short(item.hash)}</code><span>Explorer ↗</span>
                </a>
              ))}
            </div>
          ) : (
            <p className="activityEmpty">Create, submit, resolve, claim or refund from this workspace and the finalized transaction will appear here.</p>
          )}
        </div>
      </section>

      <section className="section guardrails">
        <p className="kicker">SETTLEMENT GUARDRAILS</p>
        <h2>Rules that protect both sides.</h2>
        <div className="ruleGrid">
          <article><span>01</span><b>Escrow first</b><p>No agreement exists without a positive native GEN reward already locked.</p></article>
          <article><span>02</span><b>Assigned contractor</b><p>Only the sponsor-selected wallet can submit evidence or claim an approved payment.</p></article>
          <article><span>03</span><b>Independent sources</b><p>Primary and supporting evidence must use separate HTTPS hostnames.</p></article>
          <article><span>04</span><b>Retry without gaming</b><p>Rejected evidence can be replaced before deadline, but attempts are capped at three.</p></article>
          <article><span>05</span><b>Consensus before money</b><p>Approval and confidence must survive independent validator re-execution.</p></article>
          <article><span>06</span><b>Guarded refund</b><p>Expired OPEN or REJECTED work can be refunded; unresolved submitted evidence cannot be bypassed.</p></article>
        </div>
      </section>

      <section className="section why" id="why">
        <p className="kicker">WHY GENLAYER IS CENTRAL</p>
        <h2>A normal smart contract cannot judge a deliverable.</h2>
        <div className="whyGrid">
          <article><span>01</span><b>Live web evidence</b><p>The Intelligent Contract renders the deliverable and corroborating source when judgment happens.</p></article>
          <article><span>02</span><b>Natural-language criteria</b><p>The sponsor commits to human-readable acceptance rules instead of reducing work quality to a brittle boolean oracle.</p></article>
          <article><span>03</span><b>Validator re-execution</b><p>The leader proposes approval; validators independently re-fetch and re-evaluate before state changes.</p></article>
          <article><span>04</span><b>Economic consequence</b><p>The accepted decision changes who can withdraw native GEN held by the contract.</p></article>
        </div>
      </section>

      <section className="section readiness">
        <div className="sectionHead">
          <div>
            <p className="kicker">PRODUCTION-STYLE READINESS</p>
            <h2>Not a verdict demo.<br />A complete settlement product.</h2>
          </div>
          <p>ProofJudge covers the product states a real bilateral milestone needs, including the failure path reviewers usually cannot verify in demos.</p>
        </div>
        <div className="readinessGrid">
          <article><small>SPONSOR</small><b>Precommit the deal</b><p>Assigned contractor, requirement, rubric, deadline and native GEN are committed before evidence exists.</p></article>
          <article><small>CONTRACTOR</small><b>Prove completion</b><p>Only the assigned wallet may submit two independently hosted public evidence sources.</p></article>
          <article><small>CONSENSUS</small><b>Adjudicate live evidence</b><p>Validators independently re-fetch and re-evaluate instead of trusting a frontend verdict.</p></article>
          <article><small>ECONOMICS</small><b>Settle both outcomes</b><p>Approval opens contractor claim; rejection never opens payout and expired failed work can return escrow.</p></article>
          <article><small>SAFETY</small><b>Bound retries and time</b><p>Three-attempt cap, deadline ceiling, confidence threshold and unresolved-submission refund guard reduce gaming.</p></article>
          <article><small>AUDIT</small><b>Reviewer can verify</b><p>On-chain index, timestamps, policy version, Explorer lifecycle, CI reproduction and machine-readable proof are public.</p></article>
        </div>
        <div className="sourceRail">
          <a href="https://github.com/maho0638/proofjudge-genlayer/blob/main/contracts/proof_judge.py" target="_blank" rel="noreferrer">Intelligent Contract ↗</a>
          <a href="https://github.com/maho0638/proofjudge-genlayer/blob/main/docs/STEWARD_VERIFICATION.md" target="_blank" rel="noreferrer">Steward guide ↗</a>
          <a href="https://github.com/maho0638/proofjudge-genlayer/blob/main/docs/SECURITY.md" target="_blank" rel="noreferrer">Security model ↗</a>
          <a href="https://github.com/maho0638/proofjudge-genlayer/blob/main/docs/QUALITY_BAR.md" target="_blank" rel="noreferrer">Quality mapping ↗</a>
        </div>
      </section>

      <footer className="footer">
        <div className="brand"><img className="brandLogo" src="/proofjudge-logo.png" alt="ProofJudge logo" /><span><b>ProofJudge</b><small>EVIDENCE-BASED MILESTONE SETTLEMENT</small></span></div>
        <div><span className="footerVersion">v3 · PJ_V3_MINCONF70</span><a href="/verified-demo.json" target="_blank">Proof JSON ↗</a><a href="https://github.com/maho0638/proofjudge-genlayer" target="_blank">GitHub ↗</a><a href={`${explorerBase}/address/${CONTRACT_ADDRESS}`} target="_blank">GenLayer Explorer ↗</a></div>
      </footer>
    </main>
  );
}
