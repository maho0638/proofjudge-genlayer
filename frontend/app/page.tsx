"use client";

import { FormEvent, useState } from "react";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: unknown[] }) => Promise<any>;
    };
  }
}

const contractAddress = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS as `0x${string}` | undefined;

function makeClient(account?: string) {
  return createClient({
    chain: studionet,
    ...(account ? { account: account as `0x${string}` } : {}),
  } as any);
}

async function walletAddress() {
  if (!window.ethereum) throw new Error("MetaMask is required for write actions.");
  const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
  if (!accounts?.[0]) throw new Error("No wallet account selected.");
  return accounts[0] as string;
}

export default function Home() {
  const [reviewId, setReviewId] = useState("demo-1");
  const [requirement, setRequirement] = useState("");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [lookupId, setLookupId] = useState("demo-1");
  const [result, setResult] = useState<any>(null);
  const [status, setStatus] = useState("Ready");

  async function submitReview(event: FormEvent) {
    event.preventDefault();
    if (!contractAddress) return setStatus("Set NEXT_PUBLIC_CONTRACT_ADDRESS first.");
    try {
      setStatus("Submitting review request...");
      const account = await walletAddress();
      const client: any = makeClient(account);
      const write = {
        address: contractAddress,
        functionName: "submit_review",
        args: [reviewId, requirement, evidenceUrl],
      };
      const estimate = await client.estimateTransactionFeesForWrite(write);
      const hash = await client.writeContract({
        ...write,
        fees: {
          distribution: estimate.distribution,
          feeValue: estimate.feeValue,
        },
      });
      await client.waitForTransactionReceipt({ hash, status: "ACCEPTED", retries: 24, interval: 5000 });
      setStatus(`Submitted: ${hash}`);
    } catch (error: any) {
      setStatus(error?.message || "Submit failed");
    }
  }

  async function resolveReview() {
    if (!contractAddress) return setStatus("Set NEXT_PUBLIC_CONTRACT_ADDRESS first.");
    try {
      setStatus("Resolving with GenLayer consensus...");
      const account = await walletAddress();
      const client: any = makeClient(account);
      const write = {
        address: contractAddress,
        functionName: "resolve_review",
        args: [lookupId],
      };
      const estimate = await client.estimateTransactionFeesForWrite(write);
      const hash = await client.writeContract({
        ...write,
        fees: {
          distribution: estimate.distribution,
          feeValue: estimate.feeValue,
        },
      });
      await client.waitForTransactionReceipt({ hash, status: "ACCEPTED", retries: 24, interval: 5000 });
      setStatus(`Resolved: ${hash}`);
      await loadReview();
    } catch (error: any) {
      setStatus(error?.message || "Resolve failed");
    }
  }

  async function loadReview() {
    if (!contractAddress) return setStatus("Set NEXT_PUBLIC_CONTRACT_ADDRESS first.");
    try {
      setStatus("Reading review...");
      const client: any = makeClient();
      const data = await client.readContract({
        address: contractAddress,
        functionName: "get_review",
        args: [lookupId],
      });
      setResult(data);
      setStatus("Loaded");
    } catch (error: any) {
      setStatus(error?.message || "Read failed");
    }
  }

  return (
    <main>
      <header>
        <div>
          <span className="eyebrow">GENLAYER INTELLIGENT CONTRACT</span>
          <h1>ProofJudge</h1>
          <p>Verify task evidence with live web data, LLM reasoning, and validator consensus.</p>
        </div>
        <div className="status">{status}</div>
      </header>

      <section className="grid">
        <form className="card" onSubmit={submitReview}>
          <h2>Submit evidence</h2>
          <label>Review ID<input value={reviewId} onChange={(e) => setReviewId(e.target.value)} /></label>
          <label>Requirement<textarea value={requirement} onChange={(e) => setRequirement(e.target.value)} placeholder="Example: The GitHub repository must include a working demo and setup instructions." /></label>
          <label>Public evidence URL<input value={evidenceUrl} onChange={(e) => setEvidenceUrl(e.target.value)} placeholder="https://..." /></label>
          <button type="submit">Submit on GenLayer</button>
        </form>

        <div className="card">
          <h2>Resolve & inspect</h2>
          <label>Review ID<input value={lookupId} onChange={(e) => setLookupId(e.target.value)} /></label>
          <div className="actions">
            <button onClick={resolveReview}>Resolve with consensus</button>
            <button className="secondary" onClick={loadReview}>Read result</button>
          </div>
          <pre>{result ? JSON.stringify(result, null, 2) : "No result loaded yet."}</pre>
        </div>
      </section>

      <section className="steps">
        <div><b>1</b><span>Submit a natural-language requirement and public evidence URL.</span></div>
        <div><b>2</b><span>GenLayer fetches the evidence and evaluates it with an LLM.</span></div>
        <div><b>3</b><span>Validators reach consensus and store the verdict on-chain.</span></div>
      </section>
    </main>
  );
}
