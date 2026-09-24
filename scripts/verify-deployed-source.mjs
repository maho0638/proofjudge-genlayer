import fs from "node:fs";
import { createHash } from "node:crypto";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const address = process.env.CONTRACT_ADDRESS;
if (!address) throw new Error("CONTRACT_ADDRESS is required");

const client = createClient({ chain: studionet });
const deployed = await client.getContractCode(address);
const local = fs.readFileSync("contracts/proof_judge.py", "utf8");

const normalize = (value) => String(value).replace(/\r\n/g, "\n").trim();
const deployedSource = normalize(deployed);
const repositorySource = normalize(local);
const sha256 = (value) => createHash("sha256").update(value, "utf8").digest("hex");

const deployedHash = sha256(deployedSource);
const repositoryHash = sha256(repositorySource);

console.log("DEPLOYED_CONTRACT_ADDRESS=" + address);
console.log("DEPLOYED_SOURCE_SHA256=" + deployedHash);
console.log("REPOSITORY_SOURCE_SHA256=" + repositoryHash);

if (deployedSource !== repositorySource) {
  console.error("DEPLOYED_SOURCE_MATCH=false");
  process.exit(1);
}

console.log("DEPLOYED_SOURCE_MATCH=true");
