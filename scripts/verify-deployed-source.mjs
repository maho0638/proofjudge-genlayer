import fs from "node:fs";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const address = process.env.CONTRACT_ADDRESS;
if (!address) throw new Error("CONTRACT_ADDRESS is required");

const client = createClient({ chain: studionet });
const deployed = await client.getContractCode({ address });
const local = fs.readFileSync("contracts/proof_judge.py", "utf8");

const normalize = (value) => String(value).replace(/\r\n/g, "\n").trim();

if (normalize(deployed) !== normalize(local)) {
  console.error("DEPLOYED_SOURCE_MATCH=false");
  process.exit(1);
}

console.log("DEPLOYED_SOURCE_MATCH=true");
console.log("DEPLOYED_CONTRACT_ADDRESS=" + address);
