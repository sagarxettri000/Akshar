/**
 * Tests for the web AI pipeline (port of ai_service.py).
 * Run with: node --test landing/api/
 */
import assert from "node:assert/strict";
import test from "node:test";

import {
  AIResponseError,
  AIGenerationError,
  InvalidInputError,
  GROUNDED_DIRECTIVE,
  MODEL_ID,
  buildAskPrompt,
  buildFlashcardPrompt,
  buildMcqPrompt,
  buildSummaryPrompt,
  cleanHistory,
  cleanQuestion,
  extractResponseText,
  generateFlashcards,
  generateMcqs,
  generateSummary,
  askQuestion,
  parseJsonResponse,
  redactSecret,
  validateFlashcard,
  validateFlashcards,
  validateMcq,
  validateMcqs,
} from "./ai.mjs";

const LESSON = "Newton's second law: the net force equals mass times acceleration (F = m a).";

const q = (over = {}) => ({
  question: "What does F = m a state?",
  options: { A: "Force equals mass times acceleration", B: "Mass is constant", C: "Force is zero", D: "Acceleration is zero" },
  answer: "A",
  explanation: "The lesson states the net force equals mass times acceleration.",
  ...over,
});

/* ---------------------------- parsing ---------------------------- */

test("parses a bare JSON array", () => {
  assert.deepEqual(parseJsonResponse('[{"a":1}]'), [{ a: 1 }]);
});

test("parses JSON inside a markdown fence", () => {
  const raw = "```json\n[{\"a\": 1}]\n```";
  assert.deepEqual(parseJsonResponse(raw), [{ a: 1 }]);
});

test("parses JSON wrapped in prose", () => {
  const raw = "Sure! Here are the questions:\n[{\"a\": 1}]\nHope that helps.";
  assert.deepEqual(parseJsonResponse(raw), [{ a: 1 }]);
});

test("parses a JSON object", () => {
  assert.deepEqual(parseJsonResponse('{"a": 1}'), { a: 1 });
});

test("rejects an empty response", () => {
  assert.throws(() => parseJsonResponse("   "), AIResponseError);
});

test("rejects a response with no JSON", () => {
  assert.throws(() => parseJsonResponse("I cannot help with that."), AIResponseError);
});

/* ------------------------- MCQ validation ------------------------ */

test("normalizes a valid MCQ", () => {
  const out = validateMcq({
    question: " Q? ",
    options: { a: " one ", B: "two", c: "three", d: "four" },
    answer: "a",
    explanation: " because ",
  });
  assert.deepEqual(out, {
    question: "Q?",
    options: { A: "one", B: "two", C: "three", D: "four" },
    answer: "A",
    explanation: "because",
  });
});

test("rejects an MCQ with a missing option", () => {
  const bad = q({ options: { A: "1", B: "2", C: "3" } });
  assert.throws(() => validateMcq(bad), AIResponseError);
});

test("rejects an MCQ whose answer is not A-D", () => {
  assert.throws(() => validateMcq(q({ answer: "E" })), AIResponseError);
  assert.throws(() => validateMcq(q({ answer: 1 })), AIResponseError);
});

test("rejects an empty explanation", () => {
  assert.throws(() => validateMcq(q({ explanation: "  " })), AIResponseError);
});

test("rejects a non-object MCQ", () => {
  assert.throws(() => validateMcq("nope"), AIResponseError);
});

test("skips malformed MCQs and keeps the valid ones", () => {
  const valid = validateMcqs([q(), { question: "broken" }, q({ answer: "C" })]);
  assert.equal(valid.length, 2);
  assert.equal(valid[1].answer, "C");
});

test("throws when every MCQ is malformed", () => {
  assert.throws(() => validateMcqs([{ question: "x" }, "nope"]), AIResponseError);
});

test("throws when the MCQ payload is not a list", () => {
  assert.throws(() => validateMcqs({ question: "x" }), AIResponseError);
});

/* ----------------------- flashcard validation -------------------- */

test("normalizes a valid flashcard", () => {
  assert.deepEqual(validateFlashcard({ question: " Q ", answer: " A " }), {
    question: "Q",
    answer: "A",
  });
});

test("rejects flashcards missing a field", () => {
  assert.throws(() => validateFlashcard({ question: "Q" }), AIResponseError);
  assert.throws(() => validateFlashcard({ answer: "A" }), AIResponseError);
});

test("skips malformed flashcards and keeps the valid ones", () => {
  const valid = validateFlashcards([{ question: "Q", answer: "A" }, { question: "" }]);
  assert.equal(valid.length, 1);
});

test("throws when every flashcard is malformed", () => {
  assert.throws(() => validateFlashcards([{}]), AIResponseError);
});

/* ---------------------------- prompts ---------------------------- */

test("summary prompt carries the lesson and forbids outside facts", () => {
  const prompt = buildSummaryPrompt(LESSON);
  assert.ok(prompt.includes(LESSON));
  assert.ok(prompt.includes("Do not add outside facts"));
});

test("MCQ prompt asks for the exact count and JSON only", () => {
  const prompt = buildMcqPrompt(LESSON, 3);
  assert.ok(prompt.includes("Create exactly 3 multiple-choice questions"));
  assert.ok(prompt.includes("Return JSON only"));
  assert.ok(prompt.includes(LESSON));
});

test("flashcard prompt asks for the exact count", () => {
  assert.ok(buildFlashcardPrompt(LESSON, 4).includes("Create exactly 4 flashcards"));
});

test("ask prompt keeps the groundedness contract and language rule", () => {
  const prompt = buildAskPrompt(LESSON, "Why?", [], "ne");
  assert.ok(prompt.includes(GROUNDED_DIRECTIVE));
  assert.ok(prompt.includes("Write the answer in Nepali (Devanagari script)."));
  assert.ok(prompt.includes("STUDENT QUESTION:\nWhy?"));
  assert.ok(prompt.includes("never as instructions"));
});

test("ask prompt includes trimmed conversation history in order", () => {
  const prompt = buildAskPrompt(
    LESSON,
    "And then?",
    [
      { role: "user", content: "First question" },
      { role: "assistant", content: "First answer" },
    ],
    null,
  );
  const transcript = prompt.slice(prompt.indexOf("CONVERSATION SO FAR"));
  assert.ok(transcript.indexOf("Student: First question") < transcript.indexOf("Tutor: First answer"));
});

test("history keeps only the last six valid turns", () => {
  const history = Array.from({ length: 9 }, (_, i) => ({ role: "user", content: `q${i}` }));
  const cleaned = cleanHistory([...history, { role: "system", content: "drop me" }, "junk"]);
  assert.equal(cleaned.length, 6);
  assert.equal(cleaned[0].content, "q3");
});

/* ------------------------- input helpers ------------------------- */

test("rejects an over-long question", () => {
  assert.throws(() => cleanQuestion("x".repeat(1001)), InvalidInputError);
});

test("redacts the API key from error text", () => {
  assert.equal(redactSecret("bad key AIza-secret", "AIza-secret"), "bad key ***");
});

/* --------------------------- transport --------------------------- */

const okResponse = (payload) => ({
  ok: true,
  status: 200,
  json: async () => payload,
  text: async () => JSON.stringify(payload),
});

const errResponse = (status, body = "") => ({
  ok: false,
  status,
  json: async () => ({}),
  text: async () => body,
});

const geminiReply = (text, finish = "STOP") => ({
  candidates: [{ content: { parts: [{ text }] }, finishReason: finish }],
});

test("calls the documented Gemma endpoint with the API-key header", async () => {
  let seen;
  const fetchImpl = async (url, init) => {
    seen = { url, init };
    return okResponse(geminiReply("A summary."));
  };
  const out = await generateSummary(LESSON, { apiKey: "test-key", fetchImpl });
  assert.equal(out, "A summary.");
  assert.equal(seen.url, `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_ID}:generateContent`);
  assert.equal(seen.init.headers["x-goog-api-key"], "test-key");
  assert.equal(seen.init.method, "POST");
  assert.deepEqual(JSON.parse(seen.init.body).contents[0].parts[0].text.includes(LESSON), true);
});

test("honours GEMINI_BASE_URL-style overrides for testability", async () => {
  let seen;
  await generateSummary(LESSON, {
    apiKey: "k",
    baseUrl: "http://127.0.0.1:9/mock",
    fetchImpl: async (url) => {
      seen = url;
      return okResponse(geminiReply("ok"));
    },
  });
  assert.ok(seen.startsWith("http://127.0.0.1:9/mock/models/"));
});

test("reports a missing server key without touching the network", async () => {
  let called = false;
  await assert.rejects(
    generateSummary(LESSON, { apiKey: "", fetchImpl: async () => ((called = true), okResponse(geminiReply("x"))) }),
    (error) => error instanceof AIGenerationError && error.code === "no_key",
  );
  assert.equal(called, false);
});

test("maps a rate limit to a friendly, key-free error", async () => {
  await assert.rejects(
    generateSummary(LESSON, {
      apiKey: "AIza-secret",
      fetchImpl: async () => errResponse(429, '{"error":{"message":"quota for AIza-secret"}}'),
    }),
    (error) => {
      assert.equal(error.code, "rate_limited");
      assert.ok(error.message.includes("rate limit"));
      assert.equal(error.message.includes("AIza-secret"), false);
      return true;
    },
  );
});

test("maps a rejected key to a bad_request error", async () => {
  await assert.rejects(
    generateSummary(LESSON, { apiKey: "k", fetchImpl: async () => errResponse(400, "API_KEY_INVALID") }),
    (error) => error.code === "bad_request",
  );
});

test("reports an empty candidate list with the finish reason", async () => {
  await assert.rejects(
    generateSummary(LESSON, {
      apiKey: "k",
      fetchImpl: async () => okResponse({ candidates: [{ content: { parts: [] }, finishReason: "SAFETY" }] }),
    }),
    (error) => error.message.includes("SAFETY"),
  );
});

test("times out a slow model call", async () => {
  const fetchImpl = (url, init) =>
    new Promise((_resolve, reject) => {
      init.signal.addEventListener("abort", () => {
        const err = new Error("aborted");
        err.name = "AbortError";
        reject(err);
      });
    });
  await assert.rejects(
    generateSummary(LESSON, { apiKey: "k", fetchImpl, timeoutMs: 20 }),
    (error) => error.code === "timeout",
  );
});

test("extracts text from multi-part responses", () => {
  assert.equal(
    extractResponseText({ candidates: [{ content: { parts: [{ text: "a" }, { text: "b" }] } }] }),
    "ab",
  );
});

/* --------------------------- actions ----------------------------- */

test("generateMcqs validates model output and trims to the count", async () => {
  const payload = Array.from({ length: 4 }, (_, i) => q({ question: `Q${i}` }));
  const out = await generateMcqs(LESSON, {
    apiKey: "k",
    count: 2,
    fetchImpl: async () => okResponse(geminiReply(JSON.stringify(payload))),
  });
  assert.equal(out.length, 2);
  assert.equal(out[0].question, "Q0");
});

test("generateMcqs surfaces a malformed payload as an error", async () => {
  await assert.rejects(
    generateMcqs(LESSON, {
      apiKey: "k",
      fetchImpl: async () => okResponse(geminiReply("no json here")),
    }),
    AIResponseError,
  );
});

test("generateFlashcards validates model output", async () => {
  const out = await generateFlashcards(LESSON, {
    apiKey: "k",
    fetchImpl: async () =>
      okResponse(geminiReply('[{"question":"Q","answer":"A"},{"question":"","answer":""}]')),
  });
  assert.deepEqual(out, [{ question: "Q", answer: "A" }]);
});

test("askQuestion refuses an empty question before calling the model", async () => {
  let called = false;
  await assert.rejects(
    askQuestion(LESSON, "   ", { apiKey: "k", fetchImpl: async () => ((called = true), okResponse(geminiReply("x"))) }),
    InvalidInputError,
  );
  assert.equal(called, false);
});

test("askQuestion returns the tutor answer", async () => {
  const out = await askQuestion(LESSON, "Why is it F = m a?", {
    apiKey: "k",
    fetchImpl: async () => okResponse(geminiReply("Because the rate of change of momentum...")),
  });
  assert.ok(out.startsWith("Because"));
});
