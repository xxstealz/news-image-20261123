// The Daily Globe — Monday 23 November 2026.
//
// This program is the entrypoint: it takes the front page this
// repository ships (entry.png, drawn by draw_entry.py from the day's
// verified news) and places a copy at /output/entry.png, where the
// gate reads it. Nothing else is written; the judge sees exactly
// the bytes of that file.
//
// Node 22, standard library only. Outside the grader's container,
// MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
console.log("entry.png written to", join(outDir, "entry.png"));
