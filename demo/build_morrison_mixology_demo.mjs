import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const workspaceRoot = path.resolve(scriptDir, "..");
const templatePath = path.join(scriptDir, "morrison_mixology_demo.template.html");
const outputPath = path.join(scriptDir, "morrison_mixology_demo.html");
const tempDir = path.join(workspaceRoot, ".tmp", "morrison_mixology_demo");

fs.mkdirSync(tempDir, { recursive: true });

const sources = {
  storage: "D:/NDC/Assets/Resources/Art/Scene/Backgrounds/EPI01/SC001_bg_RosaStorageRoom.png",
  bar: "D:/NDC/Assets/Resources/Art/Scene/Backgrounds/EPI01/SC010_bg_BarLobby.png",
  bottle: "D:/NDC/Assets/Resources/Art/Scene/EVIDENCE/EPI03/helen_home/SC3008_item_3307_big.png",
  morrisonSluggish: "D:/NDC/Assets/Resources/Art/avg_clip/EPI01/static/morrison_sluggish.png",
  morrisonSharp: "D:/NDC/Assets/Resources/Art/avg_clip/EPI01/static/morrison_sharp.png",
  morrisonClear: "D:/NDC/Assets/Resources/Art/avg_clip/EPI01/static/morrison_drunk_clear_eyes.png",
  paper: "D:/NDC/Assets/Resources/Art/UI/Caseboard/paper.png",
  drink: "D:/NDC/Assets/Resources/Art/Scene/EVIDENCE/EPI01/BarLobby/SC9004_envir_morrison_whiskey_glass.png"
};

for (const source of Object.values(sources)) {
  if (!fs.existsSync(source)) throw new Error(`Missing source asset: ${source}`);
}

const compressedStorage = path.join(tempDir, "storage.jpg");
const compressedBar = path.join(tempDir, "bar.jpg");

function compressBackground(source, output) {
  execFileSync("ffmpeg", [
    "-hide_banner", "-loglevel", "error", "-y",
    "-i", source,
    "-vf", "scale=1920:-2",
    "-q:v", "3",
    "-map_metadata", "-1",
    output
  ], { stdio: "inherit" });
}

compressBackground(sources.storage, compressedStorage);
compressBackground(sources.bar, compressedBar);

function asDataUri(filePath, mime) {
  return `data:${mime};base64,${fs.readFileSync(filePath).toString("base64")}`;
}

const replacements = new Map([
  ["__ASSET_STORAGE__", asDataUri(compressedStorage, "image/jpeg")],
  ["__ASSET_BAR__", asDataUri(compressedBar, "image/jpeg")],
  ["__ASSET_BOTTLE__", asDataUri(sources.bottle, "image/png")],
  ["__ASSET_MORRISON_SLUGGISH__", asDataUri(sources.morrisonSluggish, "image/png")],
  ["__ASSET_MORRISON_SHARP__", asDataUri(sources.morrisonSharp, "image/png")],
  ["__ASSET_MORRISON_CLEAR__", asDataUri(sources.morrisonClear, "image/png")],
  ["__ASSET_PAPER__", asDataUri(sources.paper, "image/png")],
  ["__ASSET_DRINK__", asDataUri(sources.drink, "image/png")]
]);

let html = fs.readFileSync(templatePath, "utf8");
for (const [token, value] of replacements) html = html.replaceAll(token, value);

const unresolved = html.match(/__ASSET_[A-Z_]+__/g);
if (unresolved) throw new Error(`Unresolved asset tokens: ${[...new Set(unresolved)].join(", ")}`);

fs.writeFileSync(outputPath, html, "utf8");

const megabytes = fs.statSync(outputPath).size / (1024 * 1024);
console.log(`Built ${outputPath}`);
console.log(`Self-contained file size: ${megabytes.toFixed(2)} MB`);
