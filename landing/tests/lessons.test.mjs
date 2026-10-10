/**
 * Lesson data contract.
 *
 * `landing/data/lessons.json` is the one lesson file the app serves, so these checks
 * are the only thing standing between a malformed record and a student.
 *
 * Run with: node --test landing/tests/lessons.test.mjs
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const LESSONS_PATH = new URL("../data/lessons.json", import.meta.url);
const REQUIRED_FIELDS = ["id", "track", "subject", "topic", "title", "language", "content"];
const VALID_LANGUAGES = ["en", "ne"];
const EXPECTED_TRACKS = ["NEB Grade 11", "NEB Grade 12", "CEE", "IOE"];

const file = JSON.parse(readFileSync(LESSONS_PATH, "utf8"));
const lessons = file.lessons;

test("the file is an object with a non-empty lessons list", () => {
  assert.equal(typeof file, "object");
  assert.ok(Array.isArray(lessons), "lessons must be an array");
  assert.ok(lessons.length > 0, "lessons must not be empty");
  assert.deepEqual(Object.keys(file).sort(), ["lessons", "note", "version"]);
});

test("every lesson carries exactly the seven required fields", () => {
  lessons.forEach((lesson, index) => {
    assert.equal(typeof lesson, "object", `lesson ${index} must be an object`);
    assert.deepEqual(
      Object.keys(lesson).sort(),
      [...REQUIRED_FIELDS].sort(),
      `lesson ${index} (${lesson.id ?? "?"}) has the wrong fields`,
    );
  });
});

test("ids are unique, non-empty strings", () => {
  const seen = new Set();
  for (const lesson of lessons) {
    assert.equal(typeof lesson.id, "string");
    assert.ok(lesson.id.trim().length > 0, "id must not be blank");
    assert.ok(!seen.has(lesson.id), `duplicate id: ${lesson.id}`);
    seen.add(lesson.id);
  }
  assert.equal(seen.size, lessons.length);
});

test("every required field is a non-empty string", () => {
  for (const lesson of lessons) {
    for (const field of REQUIRED_FIELDS) {
      assert.equal(typeof lesson[field], "string", `${lesson.id}.${field} must be a string`);
      assert.ok(
        lesson[field].trim().length > 0,
        `${lesson.id}.${field} must not be blank`,
      );
    }
  }
});

test("languages are the codes the app supports", () => {
  for (const lesson of lessons) {
    assert.ok(
      VALID_LANGUAGES.includes(lesson.language),
      `${lesson.id}: language '${lesson.language}' is not one of ${VALID_LANGUAGES.join(", ")}`,
    );
  }
});

test("the served lessons cover every track and both languages", () => {
  const tracks = new Set(lessons.map((lesson) => lesson.track));
  const languages = new Set(lessons.map((lesson) => lesson.language));
  for (const track of EXPECTED_TRACKS) {
    assert.ok(tracks.has(track), `no lesson covers the ${track} track`);
  }
  for (const language of VALID_LANGUAGES) {
    assert.ok(languages.has(language), `no lesson is written in ${language}`);
  }
});

test("Nepal-focused chapter topics are available in English and Nepali", () => {
  const topics = [
    "Climate and Monsoon in Nepal",
    "Rivers and Water Resources of Nepal",
    "Biodiversity and Conservation in Nepal",
    "Constitution and Fundamental Rights of Nepal",
  ];

  for (const topic of topics) {
    const variants = lessons.filter((lesson) => lesson.topic === topic);
    assert.deepEqual(
      new Set(variants.map((lesson) => lesson.language)),
      new Set(VALID_LANGUAGES),
      `${topic} must have English and Nepali lesson content`,
    );
  }
});
