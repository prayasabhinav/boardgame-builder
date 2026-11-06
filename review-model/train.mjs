// Not run since 6 November 2026: measured on five folds over the pattern-read keys it ranked r above f at AUC 0.656, and four in five of its
// flags were wrong. review-model/rules.py writes review.json from properties.json instead. Kept to compare against.
// Trains the needs-review model and writes review.json, the table the tool's flags read.
// A pair is a core mechanic and one block from another slot. Its features are the two blocks' vectors multiplied together and their
// difference, plus the partner's slot. Logistic regression with a strong L2 penalty, since labels are few. A pair a known game has is
// never flagged, whatever the model says; a pair is flagged when its probability is at least THRESHOLD.
// Run: python3 review-model/labels.py && node review-model/train.mjs
import { readFileSync, writeFileSync } from "node:fs";
const THRESHOLD = 0.5;
const vec = JSON.parse(readFileSync("review-model/block-vectors.json", "utf8"));
const slots = [...new Set(JSON.parse(readFileSync("review-model/blocks.json", "utf8")).map((b) => b.slot))];
const slotOf = Object.fromEntries(JSON.parse(readFileSync("review-model/blocks.json", "utf8")).map((b) => [b.id, b.slot]));
const { pairs, labels } = JSON.parse(readFileSync("review-model/labels.json", "utf8"));
const positives = Object.values(labels).filter((l) => l.label === 1).length;
if (positives < 10) {
  console.log(`only ${positives} pairs are labelled needs review; the model has too little to learn from, so review.json is not written. Key a sheet first (review-model/sheet.py).`);
  process.exit(0);
}
const features = (pair) => {
  const [c, b] = pair.split("+");
  return [...vec[c].map((x, i) => x * vec[b][i]), ...vec[c].map((x, i) => Math.abs(x - vec[b][i])), ...slots.map((s) => (s === slotOf[b] ? 1 : 0)), 1];
};
const train = Object.entries(labels).map(([p, l]) => [features(p), l.label]);
const w = new Array(train[0][0].length).fill(0);
const sig = (z) => 1 / (1 + Math.exp(-z));
const balance = (train.length - positives) / positives;   // the few needs-review rows weigh as much in total as the many fine ones
for (let epoch = 0; epoch < 400; epoch++) {
  const g = w.map((x) => 0.05 * x);   // L2
  for (const [x, y] of train) {
    const err = (sig(x.reduce((s, v, i) => s + v * w[i], 0)) - y) * (y === 1 ? balance : 1);
    for (let i = 0; i < w.length; i++) g[i] += (err * x[i]) / train.length;
  }
  for (let i = 0; i < w.length; i++) w[i] -= 0.5 * g[i];
}
const p = Object.fromEntries(pairs.map((q) => [q, +sig(features(q).reduce((s, v, i) => s + v * w[i], 0)).toFixed(3)]));
const flagged = pairs.filter((q) => (labels[q] ? labels[q].label === 1 : p[q] >= THRESHOLD));
writeFileSync("review.json", JSON.stringify({ made: new Date().toISOString().slice(0, 10), threshold: THRESHOLD, flagged, p }, null, 1));
console.log(`wrote review.json: ${flagged.length} of ${pairs.length} pairs flagged (${flagged.filter((q) => !labels[q]).length} predicted, ${flagged.filter((q) => labels[q]).length} labelled)`);
