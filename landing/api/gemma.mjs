/**
 * POST /api/gemma — the only place the Gemma 4 API key is used.
 *
 * The browser never sees the key and never sends lesson text: it sends a
 * lesson id plus the action, and the server reads the lesson from its own
 * copy of the content. Output is validated before it reaches the client.
 *
 * Runtime: Vercel Node function (web-standard handler). Env:
 *   GOOGLE_API_KEY  — required for AI features (never exposed to the browser)
 *   GEMINI_BASE_URL — optional override, used by local tests only
 */
import { readFileSync } from "node:fs";
import {
  AIGenerationError,
  AIServiceError,
  AIResponseError,
  InvalidInputError,
  DEFAULT_MCQ_COUNT,
  DEFAULT_FLASHCARD_COUNT,
  askQuestion,
  generateFlashcards,
  generateMcqs,
  generateSummary,
} from "./ai.mjs";

const ACTIONS = new Set(["summary", "mcqs", "flashcards", "ask"]);
const MAX_BODY_BYTES = 64 * 1024;
const MAX_COUNT = 10;
const RATE_LIMIT = { windowMs: 60_000, max: 20 };
const hits = new Map();

let lessonCache = null;

/** Load the server-side lesson copy once per instance. */
function lessons() {
  if (lessonCache) return lessonCache;
  const path = new URL("../data/lessons.json", import.meta.url);
  const parsed = JSON.parse(readFileSync(path, "utf8"));
  lessonCache = Array.isArray(parsed) ? parsed : (parsed.lessons ?? []);
  return lessonCache;
}

function findLesson(id) {
  if (typeof id !== "string" || !id.trim()) {
    throw new InvalidInputError("lessonId must be a non-empty string.");
  }
  const lesson = lessons().find((item) => item.id === id.trim());
  if (!lesson) throw new InvalidInputError("Unknown lessonId.");
  return lesson;
}

function statusFor(error) {
  switch (error?.code) {
    case "invalid_input":
      return 400;
    case "no_key":
      return 503;
    case "rate_limited":
      return 429;
    case "timeout":
      return 504;
    case "bad_response":
    case "empty_response":
    case "bad_upstream":
    case "upstream_error":
    case "network":
      return 502;
    default:
      return 500;
  }
}

function json(res, status, payload) {
  res.statusCode = status;
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.setHeader("cache-control", "no-store");
  res.end(JSON.stringify(payload));
}

function sameOrigin(req) {
  const origin = req.headers.origin;
  if (!origin) return true; // curl, server-to-server, and dev tooling
  try {
    const host = new URL(origin).host;
    const expected = req.headers.host;
    if (host === expected) return true;
    return /^(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/.test(host);
  } catch {
    return false;
  }
}

function withinRateLimit(req) {
  const ip =
    (req.headers["x-forwarded-for"] || "").split(",")[0].trim() ||
    req.socket?.remoteAddress ||
    "unknown";
  const now = Date.now();
  const recent = (hits.get(ip) ?? []).filter((t) => now - t < RATE_LIMIT.windowMs);
  if (recent.length >= RATE_LIMIT.max) {
    hits.set(ip, recent);
    return false;
  }
  recent.push(now);
  hits.set(ip, recent);
  if (hits.size > 500) {
    for (const [key, times] of hits) {
      if (!times.some((t) => now - t < RATE_LIMIT.windowMs)) hits.delete(key);
    }
  }
  return true;
}

async function readBody(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw new InvalidInputError("Request body is too large.");
    chunks.push(chunk);
  }
  if (!chunks.length) return {};
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    throw new InvalidInputError("Request body must be JSON.");
  }
}

function cleanCount(value, fallback) {
  if (value === undefined || value === null) return fallback;
  if (!Number.isInteger(value) || value < 1 || value > MAX_COUNT) {
    throw new InvalidInputError(`count must be an integer between 1 and ${MAX_COUNT}.`);
  }
  return value;
}

export default async function handler(req, res) {
  // Status probe: tells the page whether AI features are configured, without
  // touching the model or spending quota.
  if (req.method === "GET" || req.method === "HEAD") {
    const configured = Boolean(
      (process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY || "").trim(),
    );
    return json(res, 200, { ok: true, aiAvailable: configured });
  }
  if (req.method !== "POST") {
    res.setHeader("allow", "GET, POST");
    return json(res, 405, { ok: false, error: "Use POST." });
  }
  if (!sameOrigin(req)) {
    return json(res, 403, { ok: false, error: "Cross-origin request refused." });
  }
  if (!withinRateLimit(req)) {
    return json(res, 429, {
      ok: false,
      code: "rate_limited",
      error: "Too many requests from this connection. Wait a minute and try again.",
    });
  }

  let body;
  try {
    body = await readBody(req);
  } catch (error) {
    return json(res, statusFor(error), { ok: false, code: error.code, error: error.message });
  }

  const action = body.action;
  if (!ACTIONS.has(action)) {
    return json(res, 400, {
      ok: false,
      code: "invalid_input",
      error: "action must be one of: summary, mcqs, flashcards, ask.",
    });
  }

  const apiKey = process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY || "";
  if (!apiKey.trim()) {
    return json(res, 503, {
      ok: false,
      code: "no_key",
      error:
        "AI features are off: no GOOGLE_API_KEY is configured on the server. " +
        "Reading the study notes still works.",
    });
  }

  try {
    const lesson = findLesson(body.lessonId);
    const base = { apiKey };
    let data;

    switch (action) {
      case "summary":
        data = await generateSummary(lesson.content, base);
        break;
      case "mcqs":
        data = await generateMcqs(lesson.content, {
          ...base,
          count: cleanCount(body.count, DEFAULT_MCQ_COUNT),
        });
        break;
      case "flashcards":
        data = await generateFlashcards(lesson.content, {
          ...base,
          count: cleanCount(body.count, DEFAULT_FLASHCARD_COUNT),
        });
        break;
      case "ask":
        data = await askQuestion(lesson.content, body.question, {
          ...base,
          history: body.history,
          language: body.language ?? null,
        });
        break;
    }

    return json(res, 200, {
      ok: true,
      action,
      lessonId: lesson.id,
      data,
    });
  } catch (error) {
    if (error instanceof InvalidInputError) {
      return json(res, 400, { ok: false, code: error.code, error: error.message });
    }
    if (error instanceof AIResponseError || error instanceof AIGenerationError || error instanceof AIServiceError) {
      // Messages are already key-free; never surface internals to the client.
      return json(res, statusFor(error), {
        ok: false,
        code: error.code,
        error: error.message,
      });
    }
    console.error("gemma handler failed:", error?.message ?? error);
    return json(res, 500, { ok: false, error: "The request could not be completed." });
  }
}
