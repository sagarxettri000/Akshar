/**
 * Deployment wiring and secret guards for the one published front end.
 *
 * Ported from the retired web-app test module: the deployment is a single Vercel
 * project, and the API key must stay server-side.
 *
 * Run with: node --test landing/tests/deploy.test.mjs
 */
import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const LANDING = fileURLToPath(new URL("..", import.meta.url));
const SECRET_PATTERNS = [
  /AIza[0-9A-Za-z_-]{30,}/,
  /sk-[0-9A-Za-z]{20,}/,
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/,
];

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry);
    if (statSync(path).isDirectory()) {
      if (["node_modules", ".vercel"].includes(entry)) continue;
      out.push(...walk(path));
    } else {
      out.push(path);
    }
  }
  return out;
}

test("vercel.json registers the one function with a long budget and security headers", () => {
  const config = JSON.parse(readFileSync(join(LANDING, "vercel.json"), "utf8"));
  assert.ok(config.functions["api/gemma.mjs"], "the function must be registered");
  assert.ok(
    config.functions["api/gemma.mjs"].maxDuration >= 30,
    "a cold Gemma 4 answer needs a long budget",
  );
  const headerKeys = new Set(config.headers.flatMap((entry) => entry.headers.map((h) => h.key)));
  for (const key of ["X-Content-Type-Options", "Referrer-Policy", "X-Frame-Options"]) {
    assert.ok(headerKeys.has(key), `missing security header ${key}`);
  }
});

test("the API reads the key from the server environment only", () => {
  const source = readFileSync(join(LANDING, "api", "gemma.mjs"), "utf8");
  assert.match(source, /process\.env\.GOOGLE_API_KEY/);
  // The handler must never hand the key back to the browser.
  assert.ok(
    !source.replace("const base = { apiKey };", "").includes("apiKey,"),
    "the key must not be returned in a response",
  );
});

test("the browser bundle never carries a key or talks to Google directly", () => {
  const source = readFileSync(join(LANDING, "app.js"), "utf8");
  assert.ok(!source.includes("x-goog-api-key"));
  assert.ok(!source.includes("generativelanguage.googleapis.com"));
});

test("no secret value is committed anywhere under landing/", () => {
  const offenders = walk(LANDING).filter((path) => {
    let text = "";
    try {
      text = readFileSync(path, "utf8");
    } catch {
      return false; // binary asset
    }
    return SECRET_PATTERNS.some((pattern) => pattern.test(text));
  });
  assert.deepEqual(offenders, [], `possible secrets committed: ${offenders.join(", ")}`);
});
