"use client";

import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: unknown[] }) => Promise<any>;
    };
  }
}

export const CONTRACT_ADDRESS =
  "0x76D61aAec5bD4625346858acCd6dAb39966c4247" as `0x${string}`;

export function readClient() {
  const config: any = { chain: studionet };
  const endpoint = process.env.NEXT_PUBLIC_GENLAYER_RPC_URL;
  if (endpoint) config.endpoint = endpoint;
  return createClient(config);
}

export async function walletClient() {
  if (!window.ethereum) {
    throw new Error("MetaMask or another EIP-1193 wallet is required.");
  }

  const accounts = await window.ethereum.request({
    method: "eth_requestAccounts",
  });

  if (!accounts?.[0]) throw new Error("No wallet account selected.");

  const config: any = {
    chain: studionet,
    account: accounts[0] as `0x${string}`,
    provider: window.ethereum,
  };

  const endpoint = process.env.NEXT_PUBLIC_GENLAYER_RPC_URL;
  if (endpoint) config.endpoint = endpoint;

  const client: any = createClient(config);
  await client.connect("studionet");
  return { client, account: accounts[0] as string };
}

export function parseGen(value: string): bigint {
  const clean = value.trim();
  if (!/^\d+(\.\d{0,18})?$/.test(clean)) {
    throw new Error("Reward must be a valid GEN amount.");
  }
  const [whole, fraction = ""] = clean.split(".");
  return BigInt(whole) * 10n ** 18n + BigInt(fraction.padEnd(18, "0"));
}

export function formatGen(value: unknown): string {
  try {
    const n = BigInt(String(value));
    const whole = n / 10n ** 18n;
    const fraction = (n % 10n ** 18n).toString().padStart(18, "0").slice(0, 8);
    return `${whole}.${fraction.replace(/0+$/, "") || "0"} GEN`;
  } catch {
    return String(value ?? "0");
  }
}

export async function sendWrite(request: {
  address: `0x${string}`;
  functionName: string;
  args: unknown[];
  value?: bigint;
}) {
  const { client } = await walletClient();

  let fees: any = undefined;
  if (typeof client.estimateTransactionFeesForWrite === "function") {
    const estimate = await client.estimateTransactionFeesForWrite({
      ...request,
      value: request.value ?? 0n,
    });

    fees = {
      distribution: estimate.distribution,
      feeValue: estimate.feeValue,
      ...(estimate.messageAllocations
        ? { messageAllocations: estimate.messageAllocations }
        : {}),
    };
  }

  const hash = await client.writeContract({
    ...request,
    value: request.value ?? 0n,
    ...(fees ? { fees } : {}),
  });

  const receipt = await client.waitForTransactionReceipt({
    hash,
    status: "FINALIZED" as any,
    retries: 48,
    interval: 5000,
  });

  const finalized = String(receipt?.statusName ?? "").toUpperCase() === "FINALIZED";
  const executed =
    String(receipt?.txExecutionResultName ?? "").toUpperCase() ===
    "FINISHED_WITH_RETURN";

  if (!finalized || !executed) {
    throw new Error(
      `Transaction did not succeed: ${receipt?.statusName ?? "unknown"} / ${receipt?.txExecutionResultName ?? "unknown"}`
    );
  }

  return hash as string;
}
