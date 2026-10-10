/**
 * Tests for the study-selection contract in app.js.
 * Mirrors tests/test_content.py::resolve_study_path coverage.
 * Run with: node --test landing/app.test.mjs
 */
import assert from "node:assert/strict";
import test from "node:test";

import {
  availableGoals,
  examGoalOf,
  gradeOf,
  gradeOptions,
  resolveGoalPath,
  resolveSelection,
  trackFor,
  uniqueValues,
} from "../app.js";

const lesson = (track, subject, topic, language, id = `${track}-${subject}-${topic}-${language}`) => ({
  id,
  track,
  subject,
  topic,
  language,
  title: `${topic} (${language})`,
  content: "notes",
});

const LESSONS = [
  lesson("NEB Grade 11", "Physics", "Optics", "en"),
  lesson("NEB Grade 11", "Physics", "Optics", "ne"),
  lesson("NEB Grade 11", "Physics", "Waves", "en"),
  lesson("NEB Grade 11", "Chemistry", "Acids", "en"),
  lesson("CEE", "Biology", "Cells", "en"),
];

test("uniqueValues keeps first-seen order without duplicates", () => {
  assert.deepEqual(uniqueValues(LESSONS, "track"), ["NEB Grade 11", "CEE"]);
  assert.deepEqual(uniqueValues(LESSONS, "subject"), ["Physics", "Chemistry", "Biology"]);
});

test("an empty wanted selection picks the first available path", () => {
  const out = resolveSelection(LESSONS, {});
  assert.equal(out.track, "NEB Grade 11");
  assert.equal(out.subject, "Physics");
  assert.equal(out.topic, "Optics");
  assert.equal(out.language, "en");
  assert.equal(out.lesson.id, "NEB Grade 11-Physics-Optics-en");
});

test("a stale topic is repaired when its subject changes", () => {
  // Topic "Optics" does not exist under Chemistry: it must fall back.
  const out = resolveSelection(LESSONS, {
    track: "NEB Grade 11",
    subject: "Chemistry",
    topic: "Optics",
    language: "en",
  });
  assert.equal(out.subject, "Chemistry");
  assert.equal(out.topic, "Acids");
  assert.equal(out.lesson.subject, "Chemistry");
});

test("a stale subject is repaired when the track changes", () => {
  const out = resolveSelection(LESSONS, {
    track: "CEE",
    subject: "Physics",
    topic: "Optics",
    language: "ne",
  });
  assert.equal(out.subject, "Biology");
  assert.equal(out.topic, "Cells");
  assert.equal(out.language, "en"); // CEE has no Nepali variant
  assert.equal(out.lesson.track, "CEE");
});

test("a stale language falls back within the same topic", () => {
  const out = resolveSelection(LESSONS, {
    track: "NEB Grade 11",
    subject: "Physics",
    topic: "Waves",
    language: "ne", // Waves only exists in English
  });
  assert.equal(out.topic, "Waves");
  assert.equal(out.language, "en");
  assert.equal(out.lesson.title, "Waves (en)");
});

test("exact selections are preserved and variants are returned", () => {
  const out = resolveSelection(LESSONS, {
    track: "NEB Grade 11",
    subject: "Physics",
    topic: "Optics",
    language: "ne",
  });
  assert.equal(out.language, "ne");
  assert.equal(out.variants.length, 2);
  assert.equal(out.lesson.language, "ne");
});

test("an empty lesson list resolves to no lesson instead of throwing", () => {
  const out = resolveSelection([], {});
  assert.equal(out.lesson, null);
  assert.deepEqual(out.variants, []);
  assert.equal(out.track, null);
});


/* ------------------- exam goals and grades (same as content.py) ------------------- */

test("examGoalOf and gradeOf read the track", () => {
  assert.equal(examGoalOf("NEB Grade 11"), "NEB");
  assert.equal(examGoalOf("neb grade 12"), "NEB");
  assert.equal(examGoalOf("CEE"), "CEE");
  assert.equal(examGoalOf("Other board"), "Other board");
  assert.equal(gradeOf("NEB Grade 11"), "11");
  assert.equal(gradeOf("CEE"), null);
});

test("availableGoals lists the data in a stable order", () => {
  assert.deepEqual(availableGoals(LESSONS), ["NEB", "CEE"]);
});

test("gradeOptions only exist for graded goals", () => {
  assert.deepEqual(gradeOptions(LESSONS, "NEB"), ["Grade 11"]);
  assert.deepEqual(gradeOptions(LESSONS, "CEE"), []);
});

test("trackFor matches the goal and optional grade", () => {
  assert.equal(trackFor(LESSONS, "NEB", "Grade 11"), "NEB Grade 11");
  assert.equal(trackFor(LESSONS, "CEE", null), "CEE");
  assert.equal(trackFor(LESSONS, "Unknown", null), null);
});

test("resolveGoalPath picks a real lesson by default", () => {
  const out = resolveGoalPath(LESSONS, {});
  assert.equal(out.goal, "NEB");
  assert.equal(out.grade, "Grade 11");
  assert.equal(out.track, "NEB Grade 11");
  assert.ok(out.lesson);
});

test("resolveGoalPath repairs a stale grade, subject and chapter", () => {
  const out = resolveGoalPath(LESSONS, {
    goal: "NEB",
    grade: "Grade 11",
    subject: "Chemistry",
    topic: "Optics",
    language: "ne",
  });
  assert.equal(out.track, "NEB Grade 11");
  assert.equal(out.subject, "Chemistry");
  assert.equal(out.topic, "Acids");
  assert.equal(out.language, "en");
});

test("resolveGoalPath ignores a grade for a goal that has none", () => {
  const out = resolveGoalPath(LESSONS, { goal: "CEE", grade: "Grade 11", language: "ne" });
  assert.equal(out.goal, "CEE");
  assert.equal(out.grade, null);
  assert.equal(out.track, "CEE");
  assert.equal(out.lesson.track, "CEE");
});

test("resolveGoalPath falls back when the goal is unknown", () => {
  const out = resolveGoalPath(LESSONS, { goal: "Unknown" });
  assert.equal(out.goal, "NEB");
  assert.ok(out.lesson);
});

test("resolveGoalPath survives an empty lesson list", () => {
  const out = resolveGoalPath([], {});
  assert.equal(out.goal, null);
  assert.equal(out.grade, null);
  assert.equal(out.lesson, null);
});
