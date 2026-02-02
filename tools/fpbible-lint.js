import fs from "fs";
import path from "path";
import glob from "fast-glob";

const cfg = JSON.parse(fs.readFileSync("tools/fpbible-lint.json", "utf8"));

const files = await glob(cfg.include, { ignore: cfg.exclude });

let failed = false;

for (const file of files) {
  const txt = fs.readFileSync(file, "utf8");
  for (const phrase of cfg.banned) {
    const re = new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i");
    if (re.test(txt)) {
      failed = true;
      console.log(`FAIL: ${file} contains banned phrase: "${phrase}"`);
    }
  }
}

if (failed) process.exit(1);
console.log("PASS: No banned phrases found.");