/**
 * Tests for the study-dashboard and lesson helpers in app.js.
 *
 * These cover the parts a student sees as "Continue learning", the reading
 * progress bar, chapter navigation, practice marking and the assistant
 * suggestions. Run with: node --test landing/tests/dashboard.test.mjs
 */
import assert from "node:assert/strict";
import test from "node:test";

import {
  TEXT_SIZES,
  chapterNeighbours,
  dashboardModel,
  nextTextSize,
  quizSummary,
  readingProgress,
  readingBar,
  suggestedQuestions,
} from "../app.js";

const lesson = (track, subject, topic, language = "en", title = `${topic} notes`) => ({
  id: `${track}-${subject}-${topic}-${language}`.replace(/\s+/g, "-").toLowerCase(),
  track,
  subject,
  topic,
  title,
  language,
  content: `${topic} body text.`,
});

const NEB = [
  lesson("NEB Grade 11", "Physics", "Kinematics"),
  lesson("NEB Grade 11", "Physics", "Newton's Laws of Motion"),
  lesson("NEB Grade 11", "Physics", "Newton's Laws of Motion", "ne"),
  lesson("NEB Grade 11", "Chemistry", "Atomic Structure"),
  lesson("CEE", "Physics", "Kinematics"),
  lesson("IOE", "Mathematics", "Algebra"),
];

/* ------------------------------ reading progress ------------------------------ */

test("reading progress is 0 at the top of the page", () => {
  assert.equal(readingProgress({ scrollY: 0, viewportHeight: 800, docHeight: 3000 }), 0);
});

test("reading progress is 100 only once the page is scrolled to the end", () => {
  assert.equal(readingProgress({ scrollY: 2200, viewportHeight: 800, docHeight: 3000 }), 100);
  // One pixel short of the end must not read as finished.
  assert.ok(readingProgress({ scrollY: 2190, viewportHeight: 800, docHeight: 3000 }) < 100);
});

test("reading progress grows with the scroll position", () => {
  const early = readingProgress({ scrollY: 100, viewportHeight: 800, docHeight: 3000 });
  const later = readingProgress({ scrollY: 1100, viewportHeight: 800, docHeight: 3000 });
  assert.ok(later > early, `${later} should exceed ${early}`);
  assert.equal(later, 50);
});

test("a page with nothing to scroll reports complete and hides the bar", () => {
  assert.equal(readingProgress({ scrollY: 0, viewportHeight: 800, docHeight: 640 }), 100);
  assert.equal(readingBar({ viewportHeight: 800, docHeight: 640 }), false);
  assert.equal(readingBar({ viewportHeight: 800, docHeight: 3000 }), true);
});

test("reading progress is clamped, and never returns NaN", () => {
  assert.equal(readingProgress({ scrollY: 99999, viewportHeight: 800, docHeight: 3000 }), 100);
  assert.equal(readingProgress({ scrollY: -50, viewportHeight: 800, docHeight: 3000 }), 0);
  assert.equal(readingProgress({}), 0);
  assert.equal(readingProgress(), 0);
  assert.equal(readingProgress({ scrollY: 100 }), 0);
});

/* ------------------------------ chapter neighbours --------------------------- */

test("chapters sit in lesson-file order and keep the reader's language", () => {
  const current = NEB[1];
  const { prev, next } = chapterNeighbours(NEB, current);
  assert.equal(prev.topic, "Kinematics");
  assert.equal(next, null, "the second Physics chapter is the last one in that subject");
});

test("the next chapter follows the same language when both variants exist", () => {
  const nepali = NEB[2];
  const { prev, next } = chapterNeighbours(NEB, nepali);
  assert.equal(prev.topic, "Kinematics");
  assert.equal(prev.language, "en", "falls back to the only variant that exists");
  assert.equal(next, null);
});

test("chapter neighbours never cross subject or return the current chapter", () => {
  const current = NEB[3]; // Chemistry
  const { prev, next } = chapterNeighbours(NEB, current);
  assert.equal(prev, null);
  assert.equal(next, null);
  assert.equal(chapterNeighbours(NEB, null).prev, null);
});

/* ---------------------------------- quiz ------------------------------------- */

test("quizSummary splits correct, incorrect and unanswered", () => {
  const questions = [{ answer: "A" }, { answer: "B" }, { answer: "C" }];
  const summary = quizSummary(questions, new Map([[0, "A"], [1, "D"]]));
  assert.deepEqual(summary, {
    total: 3,
    correct: 1,
    incorrect: 1,
    unanswered: 1,
    answered: 2,
    accuracy: 50,
    percent: 33,
  });
});

test("quizSummary accepts the graded answer object too", () => {
  const questions = [{ answer: "A" }, { answer: "B" }];
  assert.equal(quizSummary(questions, { 0: "A", 1: "B" }).percent, 100);
  assert.equal(quizSummary(questions, {}).accuracy, 0, "accuracy is 0 with nothing answered");
  assert.equal(quizSummary([], {}).total, 0);
});

/* ---------------------------- assistant suggestions -------------------------- */

test("suggestions are prompts built from the lesson on screen", () => {
  const questions = suggestedQuestions(NEB[1]);
  assert.ok(questions.length >= 1 && questions.length <= 4);
  assert.ok(
    questions.filter((question) => question.includes("Newton's Laws of Motion")).length >= 3,
    "most suggestions name the chapter on screen",
  );
  assert.ok(questions.every((question) => typeof question === "string" && question.trim().length > 8));
  assert.equal(new Set(questions).size, questions.length, "no duplicates");
  assert.deepEqual(suggestedQuestions(null), []);
});

/* --------------------------------- dashboard --------------------------------- */

test("the dashboard starts empty without inventing activity", () => {
  const model = dashboardModel(NEB, { lessons: {}, attempts: 0, best: null, bookmarks: [] });
  assert.equal(model.opened, 0);
  assert.equal(model.attempts, 0);
  assert.equal(model.best, null);
  assert.equal(model.practice.state, "none");
  assert.deepEqual(model.bookmarks, []);
  assert.equal(model.continueLesson.id, NEB[0].id, "falls back to the first chapter");
});

test("the dashboard continues the last chapter studied and counts real activity", () => {
  const model = dashboardModel(NEB, {
    lessons: { [NEB[0].id]: true, [NEB[3].id]: true },
    attempts: 2,
    best: { score: 2, total: 5 },
    last: NEB[3].id,
    bookmarks: [NEB[4].id],
  });
  assert.equal(model.continueLesson.id, NEB[3].id);
  assert.equal(model.opened, 2);
  assert.equal(model.attempts, 2);
  assert.equal(model.practice.state, "recommend");
  assert.equal(model.practice.lesson.id, NEB[3].id);
  assert.deepEqual(model.bookmarks.map((item) => item.id), [NEB[4].id]);
});

test("a perfect best score is reported as perfect, and unknown ids are dropped", () => {
  const model = dashboardModel(NEB, {
    lessons: {},
    attempts: 1,
    best: { score: 5, total: 5 },
    last: "lesson-that-was-removed",
    bookmarks: ["also-gone"],
  });
  assert.equal(model.practice.state, "perfect");
  assert.equal(model.continueLesson.id, NEB[0].id);
  assert.deepEqual(model.bookmarks, []);
});

test("pathways count chapters, subjects and languages from the lesson file", () => {
  const model = dashboardModel(NEB, {});
  const neb = model.pathways.find((path) => path.goal === "NEB");
  const cee = model.pathways.find((path) => path.goal === "CEE");
  assert.equal(neb.chapters, 3, "Kinematics + Newton's Laws + Atomic Structure");
  assert.equal(neb.subjects, 2);
  assert.equal(neb.languages, 2);
  assert.equal(cee.chapters, 1);
  assert.deepEqual(model.pathways.map((path) => path.goal), ["NEB", "CEE", "IOE"]);
});

/* --------------------------------- text size --------------------------------- */

test("text size steps stay inside the scale", () => {
  assert.deepEqual(TEXT_SIZES, ["small", "base", "large"]);
  assert.equal(nextTextSize("base", 1), "large");
  assert.equal(nextTextSize("base", -1), "small");
  assert.equal(nextTextSize("large", 1), "large");
  assert.equal(nextTextSize("small", -1), "small");
  assert.equal(nextTextSize("unknown", 1), "large", "unknown values fall back to base first");
});
