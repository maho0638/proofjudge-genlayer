import { readFileSync } from "fs";
import path from "path";
import {
  TransactionHash,
  TransactionStatus,
  GenLayerClient,
  DecodedDeployData,
  GenLayerChain,
} from "genlayer-js/types";
import { localnet } from "genlayer-js/chains";

export default async function main(client: GenLayerClient<any>) {
  const filePath = path.resolve(process.cwd(), "contracts/proof_judge.py");
  const contractCode = new Uint8Array(readFileSync(filePath));

  await client.initializeConsensusSmartContract();

  const tx = await client.deployContract({
    code: contractCode,
    args: [],
  });

  const receipt = await client.waitForTransactionReceipt({
    hash: tx as TransactionHash,
    status: TransactionStatus.ACCEPTED,
    retries: 200,
  });

  const address =
    (client.chain as GenLayerChain).id === localnet.id
      ? receipt.data.contract_address
      : (receipt.txDataDecoded as DecodedDeployData)?.contractAddress;

  console.log(`ProofJudge deployed at: ${address}`);
}
