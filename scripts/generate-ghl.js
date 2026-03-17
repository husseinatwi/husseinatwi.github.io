/**
 * Generates a GHL (GoHighLevel) custom code snippet from the Vite build output.
 *
 * The built single-file HTML is transformed into a snippet you can paste
 * directly into GHL's Custom Code (Header/Body) or a Custom JS/HTML element.
 */

import { readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const distHtml = readFileSync(resolve(__dirname, "../dist/index.html"), "utf-8");

// Extract the <style> and <script> content from the built HTML
const styleMatch = distHtml.match(/<style[^>]*>([\s\S]*?)<\/style>/);
const scriptMatch = distHtml.match(/<script[^>]*>([\s\S]*?)<\/script>/);

const styles = styleMatch ? styleMatch[1] : "";
const script = scriptMatch ? scriptMatch[1] : "";

// Build the GHL-ready snippet
const ghlSnippet = `<!-- Arab Coach Funnel - GHL Custom Code -->
<!-- Paste this entire block into GHL Custom Code (Body) or a Custom HTML element -->
<div id="arab-coach-funnel-root"></div>
<style>
${styles}
</style>
<script>
${script}
</script>
`;

const outputPath = resolve(__dirname, "../dist/ghl-custom-code.html");
writeFileSync(outputPath, ghlSnippet, "utf-8");

console.log(`✅ GHL custom code generated: dist/ghl-custom-code.html`);
console.log(`   Size: ${(Buffer.byteLength(ghlSnippet) / 1024).toFixed(1)} KB`);
console.log(`\nTo use in GHL:`);
console.log(`  1. Open your GHL funnel/website builder`);
console.log(`  2. Add a "Custom Code" or "Custom JS/HTML" element`);
console.log(`  3. Paste the contents of dist/ghl-custom-code.html`);
console.log(`  4. Save and preview`);
