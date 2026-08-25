import { cp, mkdir, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const destination = resolve(root, "dist");

await rm(destination, { recursive: true, force: true });
await mkdir(destination, { recursive: true });

for (const entry of ["index.html", "styles.css", "src"]) {
  await cp(resolve(root, entry), resolve(destination, entry), { recursive: true });
}

await writeFile(resolve(destination, ".nojekyll"), "", "utf8");
console.log("Built Phase 2 static site in dist/");
