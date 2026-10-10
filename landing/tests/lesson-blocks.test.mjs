/**
 * Lesson body rendering.
 *
 * The notes are plain text written to one light convention (section titles,
 * bullets, numbered steps, labels such as "Example:", equations, diagrams).
 * `classifyLessonBlocks()` is the single place that turns that text into
 * structure, and these tests hold two promises: every classification is the
 * one we intend, and no lesson loses a single word on the way to the screen.
 *
 * Run with: node --test landing/tests/lesson-blocks.test.mjs
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { classifyLessonBlocks, formatDuration } from "../app.js";

const LESSONS_PATH = new URL("../data/lessons.json", import.meta.url);
const lessons = JSON.parse(readFileSync(LESSONS_PATH, "utf8")).lessons;

const types = (text) => classifyLessonBlocks(text).map((block) => block.type);

/** List markers are the one thing rendering removes, so drop them from both sides. */
const normalize = (text) =>
  String(text)
    .split("\n")
    .map((line) => line.replace(/^\s*[-•*]\s+/, "").replace(/^\s*\d+[.)]\s+/, ""))
    .join("\n")
    .replace(/\s+/g, " ")
    .trim();

test("bullet blocks become one list with the markers removed", () => {
  const [block] = classifyLessonBlocks("- first point\n- second point\n• third point");
  assert.equal(block.type, "bullets");
  assert.deepEqual(block.items, ["first point", "second point", "third point"]);
});

test("indented Markdown bullets are not mistaken for diagrams", () => {
  const [block] = classifyLessonBlocks(
    "*    **Definition:** The rate of change of momentum.\n" +
      "*    **Formula:** $F = ma$",
  );
  assert.equal(block.type, "bullets");
  assert.deepEqual(block.items, [
    "**Definition:** The rate of change of momentum.",
    "**Formula:** $F = ma$",
  ]);
});

test("numbered formula blocks become formula steps", () => {
  const [block] = classifyLessonBlocks("1. v = u + at\n2. s = ut + (1/2)at^2\n3. v^2 = u^2 + 2as");
  assert.equal(block.type, "steps");
  assert.equal(block.formulas, true);
  assert.deepEqual(block.items, ["v = u + at", "s = ut + (1/2)at^2", "v^2 = u^2 + 2as"]);
});

test("numbered prose blocks become ordinary steps", () => {
  const [block] = classifyLessonBlocks(
    "1. Principal quantum number (n): indicates the energy level or shell.\n" +
      "2. Azimuthal quantum number (l): indicates the subshell or orbital shape.",
  );
  assert.equal(block.type, "steps");
  assert.equal(block.formulas, false);
});

test("a labelled block keeps its label and its sentence", () => {
  const [block] = classifyLessonBlocks("Misconception: Ionic bonds are always stronger than covalent bonds.");
  assert.equal(block.type, "labelled");
  assert.equal(block.kind, "misconception");
  assert.equal(block.label, "Misconception");
  assert.equal(block.text, "Ionic bonds are always stronger than covalent bonds.");

  const [worked] = classifyLessonBlocks("Worked Example: Use F = m a with m = 2 kg and a = 3 m/s^2.");
  assert.equal(worked.kind, "example");
  assert.equal(worked.label, "Worked Example");
});

test("a short standalone line is a section title, a sentence never is", () => {
  assert.deepEqual(types("Genes and Alleles"), ["heading"]);
  assert.deepEqual(types("Summary"), ["heading"]);
  assert.deepEqual(
    types("A gene is a segment of DNA that codes for a specific trait."),
    ["paragraph"],
  );
  assert.deepEqual(types("What is 2 + 2?"), ["paragraph"]);
});

test("notation lines are formulas, and tables stay diagrams", () => {
  assert.deepEqual(types("f'(x) = lim(h -> 0) [f(x + h) - f(x)] / h"), ["formula"]);
  const [diagram] = classifyLessonBlocks("T     t\nT |  TT   |  Tt  |\nt |  Tt   |  tt  |");
  assert.equal(diagram.type, "diagram");
  assert.deepEqual(diagram.lines, ["T     t", "T |  TT   |  Tt  |", "t |  Tt   |  tt  |"]);
});

test("a section title written above its prose is still a title", () => {
  assert.deepEqual(types("Bohr's Model\nNiels Bohr proposed that electrons revolve in fixed orbits."), [
    "heading",
    "paragraph",
  ]);
});

test("wrapped prose stays one paragraph when no line is a title", () => {
  const [block] = classifyLessonBlocks(
    "Electrons fill orbitals in order of increasing energy,\nwhich is known as the aufbau principle.",
  );
  assert.equal(block.type, "paragraph");
  assert.equal(
    block.text,
    "Electrons fill orbitals in order of increasing energy, which is known as the aufbau principle.",
  );
});

test("a single equation inside prose keeps both shapes", () => {
  const blocks = classifyLessonBlocks(
    "The energy of an electron in the nth orbit is:\nE_n = -13.6 / n^2 eV\nwhere n is the principal quantum number.",
  );
  assert.deepEqual(blocks.map((block) => block.type), ["paragraph", "formula", "paragraph"]);
  assert.equal(blocks[1].text, "E_n = -13.6 / n^2 eV");
});

test("empty or missing text produces no blocks", () => {
  assert.deepEqual(classifyLessonBlocks(""), []);
  assert.deepEqual(classifyLessonBlocks(null), []);
  assert.deepEqual(classifyLessonBlocks(undefined), []);
});

test("durations read the way a student would say them", () => {
  assert.equal(formatDuration(0), "0 s");
  assert.equal(formatDuration(48_000), "48 s");
  assert.equal(formatDuration(84_000), "1 min 24 s");
  assert.equal(formatDuration(120_000), "2 min");
  assert.equal(formatDuration(Number.NaN), "0 s");
  assert.equal(formatDuration(-5000), "0 s");
});

test("no lesson loses words or gains an empty block", () => {
  lessons.forEach((lesson) => {
    const blocks = classifyLessonBlocks(lesson.content);
    assert.ok(blocks.length > 0, `${lesson.id} produced no blocks`);
    const rendered = blocks
      .map((block) => {
        if (block.type === "bullets" || block.type === "steps") return block.items.join("\n");
        if (block.type === "diagram") return block.lines.join("\n");
        if (block.type === "labelled") return `${block.label}: ${block.text}`;
        if (block.type === "definition") return `${block.term}: ${block.text}`;
        return block.text;
      })
      .join("\n");
    assert.equal(
      normalize(rendered),
      normalize(lesson.content),
      `${lesson.id} does not render the notes word for word`,
    );
  });
});

test("the shipped lessons actually exercise headings, lists and labels", () => {
  const counts = { heading: 0, bullets: 0, steps: 0, labelled: 0, formula: 0, diagram: 0 };
  lessons.forEach((lesson) => {
    for (const block of classifyLessonBlocks(lesson.content)) {
      counts[block.type] = (counts[block.type] ?? 0) + 1;
    }
  });
  assert.ok(counts.heading >= 30, `expected many section titles, saw ${counts.heading}`);
  assert.ok(counts.bullets >= 10, `expected bullet lists, saw ${counts.bullets}`);
  assert.ok(counts.labelled >= 5, `expected labelled blocks, saw ${counts.labelled}`);

  // A lesson whose notes carry real structure gets the matching blocks: titles,
  // a numbered formula list and a summary.
  const motion = lessons.find((item) => item.id === "grade11-physics-motion");
  const blocks = classifyLessonBlocks(motion.content);
  assert.ok(blocks.some((block) => block.type === "heading" && block.text === "Key Concepts"));
  assert.ok(blocks.some((block) => block.type === "heading" && block.text === "Summary"));
  assert.ok(blocks.some((block) => block.type === "steps" && block.formulas === true));
  assert.ok(blocks.some((block) => block.type === "bullets"));

  const bonding = lessons.find((item) => item.id === "grade11-chemistry-chemical-bonding");
  const labelled = classifyLessonBlocks(bonding.content).filter((block) => block.type === "labelled");
  assert.ok(labelled.some((block) => block.kind === "example"), "expected worked examples");
  assert.ok(labelled.some((block) => block.kind === "misconception"), "expected misconceptions");
});
