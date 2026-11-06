// Writes review-model/block-vectors.json: one vector per block, from its name and its ? text, made by the local encoder csearch uses
// (Xenova/bge-base-en-v1.5, open weights, nothing sent anywhere). Run: node review-model/embed.mjs   (after python3 review-model/blocks.py)
import { readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
const { pipeline } = await import(join(homedir(), ".local/share/csearch/node_modules/@huggingface/transformers/dist/transformers.node.mjs"));
const blocks = JSON.parse(readFileSync("review-model/blocks.json", "utf8"));
const embed = await pipeline("feature-extraction", "Xenova/bge-base-en-v1.5", { dtype: "q8" });
const out = {};
for (const b of blocks) out[b.id] = Array.from((await embed(`${b.display}: ${b.description}`, { pooling: "cls", normalize: true })).data).map((x) => +x.toFixed(5));
writeFileSync("review-model/block-vectors.json", JSON.stringify(out));
console.log(`wrote review-model/block-vectors.json: ${Object.keys(out).length} blocks`);
