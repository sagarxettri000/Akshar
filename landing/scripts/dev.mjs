#!/usr/bin/env node
/**
 * Local dev server for the Vercel app — no dependencies, no Vercel account.
 *
 *   node landing/scripts/dev.mjs                  # static + /api/gemma (real key from env)
 *   node landing/scripts/dev.mjs --mock=ok        # + a fake Gemma upstream, no key needed
 *   node landing/scripts/dev.mjs --mock=fail      # + upstream that always fails (error states)
 *   node landing/scripts/dev.mjs --mock=empty     # + upstream that returns nothing usable
 *
 * The mock upstream speaks the same HTTP shape as the Gemini API, so the real
 * handler, the real prompt building, and the real validation all run.
 */
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("../", import.meta.url));

function parseArgs(argv) {
  const parsed = {};
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith("--")) continue;
    const [key, inline] = arg.slice(2).split("=");
    if (inline !== undefined) {
      parsed[key] = inline;
    } else if (argv[i + 1] && !argv[i + 1].startsWith("--")) {
      parsed[key] = argv[i + 1];
      i += 1;
    } else {
      parsed[key] = "true";
    }
  }
  return parsed;
}

const args = parseArgs(process.argv.slice(2));

const port = Number(args.port ?? 3000);
const mockMode = args.mock ?? null;

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
};

/* ----------------------------- mock upstream ---------------------------- */

const mcq = (n) => ({
  question: `Mock question ${n} about the lesson?`,
  options: { A: `Option A${n}`, B: `Option B${n}`, C: `Option C${n}`, D: `Option D${n}` },
  answer: "B",
  explanation: `Mock explanation ${n}: the notes say so.`,
});

function mockReply(prompt) {
  if (mockMode === "fail") {
    return { status: 500, body: { error: { message: "mock upstream failure" } } };
  }
  if (mockMode === "empty") {
    return {
      status: 200,
      body: { candidates: [{ content: { parts: [] }, finishReason: "SAFETY" }] },
    };
  }
  let text;
  if (prompt.includes("multiple-choice questions")) {
    // Deliberately include one malformed item: the validator must drop it.
    text = "```json\n" + JSON.stringify([mcq(1), { question: "broken" }, mcq(2)]) + "\n```";
  } else if (prompt.includes("flashcards")) {
    text = JSON.stringify([
      { question: "Mock prompt 1?", answer: "Mock answer 1." },
      { question: "", answer: "" },
      { question: "Mock prompt 2?", answer: "Mock answer 2." },
    ]);
  } else if (prompt.includes("Summarize the lesson")) {
    text = "Mock summary: this lesson states the relationship the notes describe.";
  } else {
    text = "Mock tutor answer: the notes cover this in the paragraph above.";
  }
  return {
    status: 200,
    body: { candidates: [{ content: { parts: [{ text }] }, finishReason: "STOP" }] },
  };
}

async function startMock() {
  const server = createServer(async (req, res) => {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    if (!req.headers["x-goog-api-key"]) {
      res.writeHead(400, { "content-type": "application/json" });
      return res.end(JSON.stringify({ error: { message: "missing x-goog-api-key" } }));
    }
    let prompt = "";
    try {
      prompt = JSON.parse(Buffer.concat(chunks).toString("utf8"))?.contents?.[0]?.parts?.[0]?.text ?? "";
    } catch {
      /* an unparsable prompt is fine for the mock */
    }
    const reply = mockReply(prompt);
    res.writeHead(reply.status, { "content-type": "application/json" });
    res.end(JSON.stringify(reply.body));
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  return server.address().port;
}

let mockPort = null;
if (mockMode) {
  mockPort = await startMock();
  process.env.GEMINI_BASE_URL = `http://127.0.0.1:${mockPort}/v1beta`;
  process.env.GOOGLE_API_KEY = process.env.GOOGLE_API_KEY || "mock-key-not-a-real-secret";
}

const { default: handler } = await import("../api/gemma.mjs");

/* ------------------------------- host ---------------------------------- */

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);
  if (url.pathname === "/api/gemma") {
    try {
      return await handler(req, res);
    } catch (error) {
      res.writeHead(500, { "content-type": "application/json" });
      return res.end(JSON.stringify({ ok: false, error: String(error?.message ?? error) }));
    }
  }

  const requested = url.pathname === "/" ? "/index.html" : url.pathname;
  const filePath = normalize(join(ROOT, requested));
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403);
    return res.end("Forbidden");
  }
  try {
    const body = await readFile(filePath);
    res.writeHead(200, {
      "content-type": TYPES[extname(filePath)] ?? "application/octet-stream",
      "cache-control": "no-store",
    });
    return res.end(body);
  } catch {
    res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    return res.end("Not found");
  }
});

server.listen(port, "127.0.0.1", () => {
  const mode = mockMode
    ? `mock upstream (${mockMode}) on 127.0.0.1:${mockPort}`
    : "real Gemma 4 API";
  const ai = (process.env.GOOGLE_API_KEY || "").trim() ? "AI on" : "AI off (no GOOGLE_API_KEY)";
  console.log(`Akshar web app → http://127.0.0.1:${port}`);
  console.log(`  ${ai} · ${mode}`);
});
