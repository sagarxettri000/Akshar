/**
 * Akshar web app.
 *
 * Reads lesson content from ./data/lessons.json and sends only a lesson id to
 * /api/gemma — the model key never reaches the browser, and neither does the
 * prompt. Everything the model returns is untrusted text: it is inserted with
 * textContent, never as HTML.
 *
 * Layout of this file:
 *   1. storage and progress
 *   2. study-path selection (exported: covered by landing/tests/app.test.mjs)
 *   3. dashboard, lesson and view helpers (exported: landing/tests/dashboard.test.mjs)
 *   4. rendering
 *   5. the four Gemma 4 flows
 *   6. wiring and bootstrap
 */

const STATE_KEY = "akshar:study";
const PROGRESS_KEY = "akshar:progress";
const UI_KEY = "akshar:ui";
const LANGUAGE_LABELS = { en: "English", ne: "Nepali" };

let lessons = [];
let selection = { goal: null, grade: null, track: null, subject: null, topic: null, language: null };
let lesson = null;
let aiReady = false;
let aiMock = false;

const $ = (id) => document.getElementById(id);
const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

/* ------------------------------------------------------------------ *
 * 1. Storage and progress (private browsing must not break the app)
 * ------------------------------------------------------------------ */

function readStore(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function writeStore(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable — progress is simply not persisted */
  }
}

function emptyProgress() {
  return { lessons: {}, recent: [], attempts: 0, best: null, last: null, bookmarks: [] };
}

export function progressState() {
  const stored = readStore(PROGRESS_KEY);
  if (!stored || typeof stored !== "object") return emptyProgress();
  return {
    ...emptyProgress(),
    ...stored,
    lessons: stored.lessons && typeof stored.lessons === "object" ? stored.lessons : {},
    recent: Array.isArray(stored.recent) ? stored.recent.filter((id) => typeof id === "string") : [],
    bookmarks: Array.isArray(stored.bookmarks) ? stored.bookmarks : [],
  };
}

function saveProgress(state) {
  writeStore(PROGRESS_KEY, state);
  renderProgress();
  renderDashboard();
}

function markLessonOpened(id) {
  const state = progressState();
  state.lessons[id] = true;
  state.last = id;
  // Newest first, deduplicated: this is what the dashboard's "recently studied"
  // row shows, so it has to be the real order the reader opened chapters in.
  state.recent = [id, ...state.recent.filter((value) => value !== id)].slice(0, 5);
  saveProgress(state);
}

function recordAttempt(correct, total) {
  const state = progressState();
  state.attempts += 1;
  const best = state.best;
  if (!best || correct / total > best.score / best.total) {
    state.best = { score: correct, total };
  }
  saveProgress(state);
}

function toggleBookmark(id) {
  const state = progressState();
  const has = state.bookmarks.includes(id);
  state.bookmarks = has ? state.bookmarks.filter((value) => value !== id) : [id, ...state.bookmarks];
  saveProgress(state);
  return !has;
}

function uiState() {
  const stored = readStore(UI_KEY);
  return { textSize: stored?.textSize ?? "base" };
}

/* ------------------------------------------------------------------ *
 * 2. Selection resolution — the study-path contract
 *    (covered by landing/tests/app.test.mjs)
 * ------------------------------------------------------------------ */

export function uniqueValues(items, field) {
  const seen = [];
  for (const item of items) {
    const value = item[field];
    if (value && !seen.includes(value)) seen.push(value);
  }
  return seen;
}

export function resolveSelection(items, wanted = {}) {
  const pick = (options, value) => (options.includes(value) ? value : options[0] ?? null);
  const track = pick(uniqueValues(items, "track"), wanted.track);
  const subjects = uniqueValues(items.filter((l) => l.track === track), "subject");
  const subject = pick(subjects, wanted.subject);
  const topics = uniqueValues(
    items.filter((l) => l.track === track && l.subject === subject),
    "topic",
  );
  const topic = pick(topics, wanted.topic);
  const variants = items.filter(
    (l) => l.track === track && l.subject === subject && l.topic === topic,
  );
  const language = pick(uniqueValues(variants, "language"), wanted.language);
  const lesson = variants.find((l) => l.language === language) ?? variants[0] ?? null;
  return { track, subject, topic, language, variants, lesson };
}

export const EXAM_GOALS = ["NEB", "CEE", "IOE"];
const GRADE_PATTERN = /grade\s+(\d+)/i;

export function examGoalOf(track) {
  const normalized = String(track ?? "").trim().toUpperCase();
  return EXAM_GOALS.find((goal) => normalized.startsWith(goal)) ?? String(track ?? "").trim();
}

export function gradeOf(track) {
  const match = GRADE_PATTERN.exec(String(track ?? ""));
  return match ? match[1] : null;
}

export function availableGoals(items) {
  const known = EXAM_GOALS.filter((goal) => items.some((l) => examGoalOf(l.track) === goal));
  const extras = [];
  for (const item of items) {
    const goal = examGoalOf(item.track);
    if (!EXAM_GOALS.includes(goal) && !extras.includes(goal)) extras.push(goal);
  }
  return [...known, ...extras];
}

export function gradeOptions(items, goal) {
  const options = [];
  for (const item of items) {
    if (goal != null && examGoalOf(item.track) !== goal) continue;
    const grade = gradeOf(item.track);
    const label = grade ? `Grade ${grade}` : null;
    if (label && !options.includes(label)) options.push(label);
  }
  return options;
}

export function trackFor(items, goal, grade) {
  const wanted = grade ? gradeOf(grade) : null;
  for (const item of items) {
    if (goal != null && examGoalOf(item.track) !== goal) continue;
    if (wanted !== null && gradeOf(item.track) !== wanted) continue;
    return item.track;
  }
  return null;
}

/** Coerce an exam-goal/grade/subject/chapter/language choice into a lesson. */
export function resolveGoalPath(items, wanted = {}) {
  const goals = availableGoals(items);
  const goal = goals.includes(wanted.goal) ? wanted.goal : (goals[0] ?? null);
  const grades = gradeOptions(items, goal);
  const grade = grades.length
    ? (grades.includes(wanted.grade) ? wanted.grade : grades[0])
    : null;
  const track = trackFor(items, goal, grade);
  if (track === null) {
    const empty = resolveSelection(items, {});
    return { ...empty, goal, grade };
  }
  const resolved = resolveSelection(items, {
    track,
    subject: wanted.subject,
    topic: wanted.topic,
    language: wanted.language,
  });
  return { ...resolved, goal, grade };
}

/* ------------------------------------------------------------------ *
 * 3. Dashboard, lesson and view helpers
 *    (covered by landing/tests/dashboard.test.mjs)
 * ------------------------------------------------------------------ */

/**
 * How far down the page the reader is, 0–100.
 *
 * This is the reader's actual scroll position, not an estimate of how much of
 * the lesson has been "learned": it is 0 when the page is at the top and 100
 * only once the last of the content has been scrolled to. A page with nothing
 * to scroll has nothing to indicate, so `readingBar` hides the bar instead of
 * claiming the lesson is finished.
 */
export function readingProgress({ scrollY, viewportHeight, docHeight } = {}) {
  const viewport = Number(viewportHeight);
  const doc = Number(docHeight);
  if (!Number.isFinite(viewport) || !Number.isFinite(doc) || viewport <= 0 || doc <= 0) return 0;
  const range = doc - viewport;
  if (range <= 8) return 100;
  // Floored, so the bar never claims the reader reached the end of a page
  // they have not scrolled to the bottom of.
  return clamp(Math.floor(((Number(scrollY) || 0) / range) * 100), 0, 100);
}

/** Whether a reading-progress bar is meaningful for a page of this height. */
export function readingBar({ viewportHeight, docHeight } = {}) {
  const viewport = Number(viewportHeight);
  const doc = Number(docHeight);
  if (!Number.isFinite(viewport) || !Number.isFinite(doc)) return true;
  return doc - viewport > 8;
}

/* ------------------------------------------------------------------ *
 * Lesson text → blocks
 *
 * Lesson bodies are plain text written to one light convention: a blank
 * line separates blocks; "- " starts a bullet; "1. " starts a step; a
 * short standalone line is a section title; "Example:", "Summary:" and
 * friends open a labelled block; and a block of short "=" / "->" / "|"
 * lines is a formula or a diagram. Parsing that once here keeps the
 * renderer and the tests working from the same rules.
 * ------------------------------------------------------------------ */

const LABEL_KINDS = {
  example: ["example", "worked example", "sample"],
  note: ["note", "key point", "key idea", "remember", "definition"],
  misconception: ["misconception", "common misconception", "correction"],
  summary: ["summary", "in short", "key takeaway", "takeaway"],
  exercise: ["self-check exercise", "self-check", "exercise", "try it yourself"],
  answer: ["answer"],
};

const isBulletLine = (line) => /^[-•*]\s+/.test(line);
const isNumberedLine = (line) => /^\d+[.)]\s+/.test(line);
/** A line that is laid out in columns: part of a table or a diagram. */
const isNotationLine = (line) => line.includes("|") || /\s{3,}/.test(line);
/** Words that are maths rather than prose when they sit inside a line. */
const MATH_WORDS = new Set(["lim", "sin", "cos", "tan", "log", "ln", "exp"]);

/**
 * A line that is notation rather than prose: an equation, or one step of one.
 * A sentence that merely contains "=" is prose, so a line that ends as a
 * sentence, runs long, or is mostly words never counts.
 */
function isFormulaLine(line) {
  const text = String(line).trim();
  if (!text || text.length > 90) return false;
  if (/[.?!।:]$/.test(text)) return false;
  if (text.split(/\s+/).length > 14) return false;

  const hasEquals = text.includes("=");
  if (!hasEquals && !/->|→∞|≥|≤|\blim\b/.test(text)) return false;

  if (hasEquals) {
    const left = text.slice(0, text.indexOf("=")).trim();
    const leftWords = left ? left.split(/\s+/).length : 0;
    if (leftWords > 4) {
      const prose = (text.match(/[A-Za-z]{3,}|[\u0900-\u097F]{2,}/g) || []).filter(
        (word) => !MATH_WORDS.has(word),
      );
      if (prose.length > 2) return false;
    }
  }
  return true;
}

function labelKind(label) {
  // "Worked Example 1:" and "Example 2:" are the same kind of block.
  const key = label
    .toLowerCase()
    .replace(/\s+/g, " ")
    .replace(/\s*\b\d+$/, "")
    .trim();
  for (const [kind, names] of Object.entries(LABEL_KINDS)) {
    if (names.includes(key)) return kind;
  }
  return null;
}

const cleanMarker = (line) => line.replace(/^[-•*]\s+/, "").replace(/^\d+[.)]\s+/, "");

/**
 * A section title: short, unpunctuated, and starting a thought rather than
 * continuing one (so a wrapped sentence is never mistaken for a title).
 */
function isHeadingLine(line) {
  return (
    line.length <= 60 &&
    line.split(/\s+/).length <= 8 &&
    !/[,.:;?!।]$/.test(line) &&
    !/[=|]/.test(line) &&
    !/\s{2,}/.test(line) &&
    /^[A-Z0-9\u0900-\u097F(]/.test(line) &&
    !isBulletLine(line) &&
    !isNumberedLine(line)
  );
}

function classifyLine(line) {
  const pair = line.match(/^([^:]{2,40}):\s+(\S.*)$/);
  if (pair) {
    const kind = labelKind(pair[1]);
    // "Example:", "Summary:", "Misconception:" and friends are labelled blocks.
    if (kind) return { type: "labelled", kind, label: pair[1], text: pair[2] };
    // "Evaluate: lim …" stays notation; "वेग: विस्थापनको …" is a term and its
    // meaning, which is how the bilingual notes introduce vocabulary. A longer
    // lead-in is prose that happens to contain a colon.
    if (isFormulaLine(pair[2])) return { type: "formula", text: line };
    if (pair[1].length <= 30 && pair[1].split(/\s+/).length <= 3) {
      return { type: "definition", term: pair[1], text: pair[2] };
    }
  }
  if (isHeadingLine(line)) return { type: "heading", text: line };
  if (isFormulaLine(line)) return { type: "formula", text: line };
  return { type: "paragraph", text: line };
}

/** One run of non-list lines, with no blank line inside it. */
function classifyRun(lines) {
  if (!lines.length) return [];
  if (lines.length === 1) return [classifyLine(lines[0])];

  if (lines.length >= 2 && lines.every((line) => isFormulaLine(line) || line.includes("|"))) {
    return [{ type: "diagram", lines }];
  }

  // A section title written on the line above its prose still gets to be a
  // title — that is how the notes are laid out.
  const out = [];
  let rest = lines;
  while (rest.length > 1 && isHeadingLine(rest[0])) {
    out.push({ type: "heading", text: rest[0] });
    rest = rest.slice(1);
  }

  // One equation inside a sentence of prose stays an equation, and the prose
  // around it stays prose.
  const equations = rest.filter(isFormulaLine).length;
  if (rest.length > 1 && equations === 1) {
    const at = rest.findIndex(isFormulaLine);
    const before = rest.slice(0, at).join(" ");
    const after = rest.slice(at + 1).join(" ");
    if (before) out.push({ type: "paragraph", text: before });
    out.push({ type: "formula", text: rest[at] });
    if (after) out.push({ type: "paragraph", text: after });
    return out;
  }

  out.push({ type: "paragraph", text: rest.join(" ") });
  return out;
}

/** Structure for one lesson body: headings, prose, lists, formulas, examples. */
export function classifyLessonBlocks(text) {
  const out = [];
  let run = [];
  let list = null;
  let diagram = [];

  const flushRun = () => {
    if (run.length) {
      out.push(...classifyRun(run));
      run = [];
    }
  };
  const flushDiagram = () => {
    if (diagram.length) {
      out.push({ type: "diagram", lines: diagram });
      diagram = [];
    }
  };
  const flushList = () => {
    if (list) {
      out.push(
        list.type === "steps" ? { ...list, formulas: list.items.every(isFormulaLine) } : list,
      );
      list = null;
    }
  };

  for (const raw of String(text ?? "").split("\n")) {
    const line = raw.trim();
    if (!line) {
      flushRun();
      flushList();
      continue;
    }
    // Table rows are written one line per blank-line-separated block, so they
    // are collected across blanks and emitted as a single diagram.
    if (isNotationLine(line)) {
      flushRun();
      flushList();
      diagram.push(line);
      continue;
    }
    flushDiagram();
    if (isBulletLine(line) || isNumberedLine(line)) {
      const type = isBulletLine(line) ? "bullets" : "steps";
      flushRun();
      if (list && list.type === type) list.items.push(cleanMarker(line));
      else {
        flushList();
        list = { type, items: [cleanMarker(line)] };
      }
      continue;
    }
    flushList();
    run.push(line);
  }
  flushRun();
  flushList();
  flushDiagram();
  return out;
}

/**
 * "2 min 14 s" / "48 s" — for the time a student actually spent on a set, which
 * the results screen states as what it is: time in this tab, not exam time.
 */
export function formatDuration(ms) {
  const seconds = Math.round(Math.max(0, Number(ms) || 0) / 1000);
  if (seconds < 60) return `${seconds} s`;
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return rest ? `${minutes} min ${rest} s` : `${minutes} min`;
}

export function formatGenerationDuration(ms) {
  return Number(ms) >= 1000 ? formatDuration(ms) : "under 1 s";
}

/** The chapters either side of the current one, in lesson-file order. */
export function chapterNeighbours(items, current) {
  if (!current) return { prev: null, next: null };
  const siblings = items.filter(
    (l) => l.track === current.track && l.subject === current.subject,
  );
  const topics = uniqueValues(siblings, "topic");
  const index = topics.indexOf(current.topic);
  const pick = (topic) => {
    if (!topic) return null;
    const variants = siblings.filter((l) => l.topic === topic);
    return variants.find((l) => l.language === current.language) ?? variants[0] ?? null;
  };
  return {
    prev: index > 0 ? pick(topics[index - 1]) : null,
    next: index >= 0 && index < topics.length - 1 ? pick(topics[index + 1]) : null,
  };
}

/** Correct / incorrect / unanswered counts and accuracy for one attempt. */
export function quizSummary(questions = [], answers = {}) {
  const get = (index) => (answers instanceof Map ? answers.get(index) : answers[index]);
  let correct = 0;
  let incorrect = 0;
  let unanswered = 0;
  questions.forEach((question, index) => {
    const chosen = get(index);
    if (!chosen) unanswered += 1;
    else if (chosen === question.answer) correct += 1;
    else incorrect += 1;
  });
  const total = questions.length;
  const answered = correct + incorrect;
  return {
    total,
    correct,
    incorrect,
    unanswered,
    answered,
    accuracy: answered ? Math.round((correct / answered) * 100) : 0,
    percent: total ? Math.round((correct / total) * 100) : 0,
  };
}

/**
 * Prompt suggestions for the assistant, derived from the lesson on screen.
 * They are questions to ask, never answers, and never claims about the notes.
 */
export function suggestedQuestions(lesson) {
  if (!lesson?.topic) return [];
  const topic = lesson.topic;
  const questions = [
    `Summarise ${topic} in a few sentences.`,
    `Explain the hardest part of ${topic} step by step.`,
    `Give one worked example from these notes.`,
    `What should I revise first in ${topic}?`,
  ];
  return [...new Set(questions)].slice(0, 4);
}

/** Everything the dashboard shows, from the lesson file and saved activity. */
export function dashboardModel(items = [], progress = {}) {
  const state = { ...emptyProgress(), ...(progress ?? {}) };
  const byId = (id) => items.find((l) => l.id === id) ?? null;
  const openedIds = Object.keys(state.lessons ?? {});
  const continueLesson =
    byId(state.last) ?? openedIds.map(byId).find(Boolean) ?? items[0] ?? null;
  const best = state.best ?? null;
  const attempts = state.attempts ?? 0;
  return {
    continueLesson,
    opened: openedIds.length,
    recent: (state.recent ?? []).map(byId).filter(Boolean),
    attempts,
    best,
    pathways: availableGoals(items).map((goal) => {
      const goalItems = items.filter((l) => examGoalOf(l.track) === goal);
      return {
        goal,
        chapters: uniqueValues(goalItems, "topic").length,
        subjects: uniqueValues(goalItems, "subject").length,
        languages: uniqueValues(goalItems, "language").length,
      };
    }),
    bookmarks: (state.bookmarks ?? []).map(byId).filter(Boolean),
    practice: {
      attempts,
      best,
      lesson: continueLesson,
      state: attempts === 0 ? "none" : best && best.score === best.total ? "perfect" : "recommend",
    },
  };
}

export const TEXT_SIZES = ["small", "base", "large"];
export const TEXT_SIZE_LABELS = { small: "Small", base: "Normal", large: "Large" };

export function nextTextSize(current, step) {
  const index = TEXT_SIZES.indexOf(current);
  const from = index < 0 ? 1 : index;
  return TEXT_SIZES[clamp(from + step, 0, TEXT_SIZES.length - 1)];
}

/* ------------------------------------------------------------------ *
 * 4. Rendering: messages, tabs, views, dashboard, the lesson, tools
 * ------------------------------------------------------------------ */

function setState(id, kind, message) {
  const node = $(id);
  if (!node) return;
  node.textContent = "";
  if (!message) {
    node.hidden = true;
    return;
  }
  node.hidden = false;
  node.dataset.kind = kind;
  node.append(el("span", null, message));
}

function toast(message) {
  const node = $("toast");
  if (!node) return;
  node.textContent = message;
  node.hidden = false;
  node.classList.add("toast--visible");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => {
    node.classList.remove("toast--visible");
    toast.timer = setTimeout(() => {
      node.hidden = true;
    }, 250);
  }, 2400);
}

/* ------------------------------- views ---------------------------- */

const VIEWS = ["home", "study", "sources"];

function showView(name, { focus = false } = {}) {
  const target = VIEWS.includes(name) ? name : "home";
  for (const panel of document.querySelectorAll("[data-view-panel]")) {
    panel.hidden = panel.dataset.viewPanel !== target;
  }
  for (const link of document.querySelectorAll("a[data-view]")) {
    if (link.dataset.view === target) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  if (location.hash !== `#${target}`) history.replaceState(null, "", `#${target}`);
  if (target === "study") updateReadingProgress();
  if (focus) {
    // Focus the view without letting the browser scroll it back into view: the
    // new view belongs at the top of the page, filters included.
    $("main").focus({ preventScroll: true });
  }
  window.scrollTo({ top: 0, behavior: "auto" });
}

function wireViews() {
  for (const link of document.querySelectorAll("a[data-view]")) {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      showView(link.dataset.view, { focus: true });
    });
  }
  window.addEventListener("hashchange", () => showView(location.hash.replace("#", "")));
}

/* --------------------------- text size ---------------------------- */

function applyTextSize(name) {
  const size = TEXT_SIZES.includes(name) ? name : "base";
  document.documentElement.dataset.textSize = size;
  $("text-size-value").textContent = TEXT_SIZE_LABELS[size];
  $("text-smaller").disabled = size === TEXT_SIZES[0];
  $("text-larger").disabled = size === TEXT_SIZES[TEXT_SIZES.length - 1];
  writeStore(UI_KEY, { textSize: size });
}

/* ------------------------------ tabs ------------------------------ */

const TABS = ["explain", "ask", "practise", "flashcards"];

function selectTab(name) {
  for (const key of TABS) {
    const tab = $(`tab-${key}`);
    const panel = $(`panel-${key}`);
    const active = key === name;
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
    panel.hidden = !active;
  }
}

function wireTabs() {
  TABS.forEach((key, index) => {
    const tab = $(`tab-${key}`);
    tab.addEventListener("click", () => selectTab(key));
    tab.addEventListener("keydown", (event) => {
      const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
      if (!step) return;
      event.preventDefault();
      const next = TABS[(index + step + TABS.length) % TABS.length];
      selectTab(next);
      $(`tab-${next}`).focus();
    });
  });
}

/* --------------------------- rendering ---------------------------- */

function fillSelect(id, options, selected, labelFor = (v) => v) {
  const select = $(id);
  select.textContent = "";
  if (!options.length) {
    const option = el("option", null, "—");
    option.disabled = true;
    option.selected = true;
    select.append(option);
    select.disabled = true;
    return;
  }
  select.disabled = false;
  for (const value of options) {
    const option = el("option", null, labelFor(value));
    option.value = value;
    if (value === selected) option.selected = true;
    select.append(option);
  }
}

function renderLessonContent(text, language) {
  const box = $("lesson-content");
  box.textContent = "";
  box.setAttribute("lang", language === "ne" ? "ne" : "en");

  const blocks = classifyLessonBlocks(text);
  for (let index = 0; index < blocks.length; index += 1) {
    const block = blocks[index];
    // The chapter title is already the heading above the notes, so a first
    // section title that repeats it is dropped rather than shown twice.
    if (
      index === 0 &&
      block.type === "heading" &&
      lesson &&
      block.text.toLowerCase() === lesson.title.toLowerCase()
    ) {
      continue;
    }
    if (block.type === "heading") {
      box.append(el("h3", "prose__heading", block.text));
    } else if (block.type === "bullets" || block.type === "steps") {
      const list = document.createElement(block.type === "steps" ? "ol" : "ul");
      if (block.type === "steps" && block.formulas) list.className = "prose__list--formula";
      for (const item of block.items) list.append(el("li", null, item));
      box.append(list);
    } else if (block.type === "formula") {
      box.append(el("p", "prose__formula", block.text));
    } else if (block.type === "diagram") {
      const pre = document.createElement("pre");
      pre.className = "prose__diagram";
      pre.textContent = block.lines.join("\n");
      box.append(pre);
    } else if (block.type === "definition") {
      const row = el("p", "prose__definition");
      row.append(el("span", "prose__term", `${block.term}: `), el("span", null, block.text));
      box.append(row);
    } else if (block.type === "labelled") {
      const wrap = el("div", `prose__block prose__block--${block.kind}`);
      // The label is part of the notes, so it stays readable text, not decoration.
      wrap.append(el("p", "prose__block-label", `${block.label}:`));
      wrap.append(el("p", "prose__block-body", block.text));
      box.append(wrap);
    } else {
      box.append(el("p", null, block.text));
    }
  }
}

function renderProgress() {
  const state = progressState();
  $("stat-lessons").textContent = String(Object.keys(state.lessons ?? {}).length);
  $("stat-attempts").textContent = String(state.attempts ?? 0);
  $("stat-best").textContent = state.best ? `${state.best.score} / ${state.best.total}` : "—";
}

function renderDashboard() {
  if (!lessons.length) return;
  const model = dashboardModel(lessons, progressState());
  const current = model.continueLesson;

  const resume = $("resume");
  if (current) {
    // With no saved activity there is nothing to continue, so the card offers a
    // starting point and says so rather than presenting a claim about progress.
    const opened = model.opened > 0;
    resume.textContent = opened ? `Continue: ${current.topic}` : `Start: ${current.topic}`;
    $("resume-hint").textContent = opened
      ? `${model.opened} chapter${model.opened === 1 ? "" : "s"} opened in this browser · ${model.attempts} practice attempt${model.attempts === 1 ? "" : "s"} recorded.`
      : "Starting from the first chapter in the lesson file — you can change it on Study.";
    $("continue-meta").textContent = opened
      ? `${current.track} · ${current.subject} · ${
          LANGUAGE_LABELS[current.language] ?? current.language
        }`
      : "Nothing studied yet in this browser.";
    $("continue-body").textContent = opened
      ? current.title
      : `${lessons.length} chapters across ${model.pathways.map((path) => path.goal).join(", ")} are ready — pick one and your place is kept here.`;
    // The hero already offers the one primary "start this chapter" action, so
    // before anything is studied this card points at the choosers instead of
    // repeating it.
    $("continue-action").textContent = opened ? `Continue ${current.topic}` : "Choose a chapter";
    $("continue-action").dataset.mode = opened ? "open" : "choose";

    // Recently studied: the chapters actually opened, newest first, minus the
    // one the button above already offers.
    const others = model.recent.filter((item) => item.id !== current.id);
    const recent = $("recent");
    recent.hidden = others.length === 0;
    const recentList = $("recent-list");
    recentList.textContent = "";
    for (const item of others.slice(0, 4)) {
      const button = el("button", "recent__item", item.topic);
      button.type = "button";
      button.title = `${item.subject} · ${item.track}`;
      button.addEventListener("click", () => openLesson(item));
      recentList.append(button);
    }
  } else {
    $("resume-hint").textContent = "";
    $("continue-meta").textContent = "Nothing studied yet in this browser.";
    $("continue-body").textContent = "Pick an exam goal and a chapter and your place is kept here.";
    $("continue-action").textContent = "Choose a chapter";
  }

  const pathways = $("pathways");
  pathways.textContent = "";
  for (const path of model.pathways) {
    const item = el("li", "pathway");
    const button = el("button", "pathway__button");
    button.type = "button";
    button.append(
      el("span", "pathway__goal", path.goal),
      el("span", "pathway__meta", `${path.chapters} chapter${path.chapters === 1 ? "" : "s"} · ${path.subjects} subject${path.subjects === 1 ? "" : "s"} · ${path.languages} language${path.languages === 1 ? "" : "s"}`),
    );
    button.addEventListener("click", () => {
      applySelection({ goal: path.goal }, { open: true });
      showView("study", { focus: true });
    });
    item.append(button);
    pathways.append(item);
  }

  const practice = model.practice;
  if (practice.state === "none") {
    $("practise-next-meta").textContent = "No practice attempts recorded yet.";
    $("practise-next-body").textContent =
      "Gemma 4 can write practice questions from the notes you are reading, then mark them and explain every answer.";
  } else {
    const { best } = practice;
    const percent = best ? Math.round((best.score / best.total) * 100) : 0;
    $("practise-next-meta").textContent = `Best so far: ${best.score} / ${best.total} (${percent}%) over ${practice.attempts} attempt${practice.attempts === 1 ? "" : "s"}.`;
    $("practise-next-body").textContent =
      practice.state === "perfect"
        ? `Every marked answer has been correct so far. Try a longer set on ${practice.lesson?.topic ?? "the same chapter"}, or open a chapter you have not practised.`
        : `Try another set on ${practice.lesson?.topic ?? "the chapter you were on"} and check the answers you missed.`;
  }

  const list = $("bookmark-list");
  list.textContent = "";
  $("bookmarks-empty").hidden = model.bookmarks.length > 0;
  for (const bookmarked of model.bookmarks) {
    const item = el("li");
    const button = el("button", "button button--quiet bookmark-open", `${bookmarked.topic}`);
    button.type = "button";
    button.addEventListener("click", () => openLesson(bookmarked, { view: "study" }));
    item.append(button, el("span", "bookmark-list__meta", `${bookmarked.track} · ${bookmarked.subject} · ${LANGUAGE_LABELS[bookmarked.language] ?? bookmarked.language}`));
    list.append(item);
  }
}

function renderLesson({ record = false } = {}) {
  const title = $("lesson-title");
  const chips = $("lesson-chips");
  const path = $("path");
  title.textContent = "";
  chips.textContent = "";
  path.textContent = "";

  if (!lesson) {
    title.textContent = "No lesson matches this selection";
    $("lesson-content").textContent = "";
    renderLessonTools();
    return;
  }

  title.textContent = lesson.title;
  title.setAttribute("lang", lesson.language === "ne" ? "ne" : "en");

  chips.append(
    el("span", "chip chip--brand", LANGUAGE_LABELS[lesson.language] ?? lesson.language),
    el("span", "chip", lesson.subject),
    el("span", "chip", lesson.track),
  );

  const parts = [
    selection.goal,
    selection.grade,
    selection.subject,
    selection.topic,
    LANGUAGE_LABELS[selection.language] ?? "",
  ];
  parts.filter(Boolean).forEach((value, index) => {
    if (index) path.append(el("span", "path__sep", "/"));
    path.append(el("span", null, value));
  });

  $("source-label").textContent = `Source · ${LANGUAGE_LABELS[lesson.language] ?? lesson.language}`;
  const sourceLinks = $("source-links");
  sourceLinks.textContent = "";
  const references = Array.isArray(lesson.references) ? lesson.references : [];
  for (const reference of references) {
    try {
      const url = new URL(reference.url);
      if (url.protocol !== "https:") continue;
      const link = el("a", null, reference.title);
      link.href = url.href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      const item = document.createElement("li");
      item.append(link);
      sourceLinks.append(item);
    } catch {
      continue;
    }
  }
  sourceLinks.hidden = sourceLinks.childElementCount === 0;
  $("source-references-label").hidden = sourceLinks.hidden;
  renderLessonContent(lesson.content, lesson.language);
  renderLessonTools();
  // Only chapters the reader actually navigated to are recorded as opened — the
  // render that fills the screen on load is not study activity.
  if (record) markLessonOpened(lesson.id);
}

/** Bookmark state, chapter neighbours, assistant context and the reading bar. */
function renderLessonTools() {
  const bookmarked = Boolean(lesson) && progressState().bookmarks.includes(lesson.id);
  const button = $("lesson-bookmark");
  button.setAttribute("aria-pressed", String(bookmarked));
  button.textContent = bookmarked ? "Bookmarked" : "Bookmark";

  const { prev, next } = chapterNeighbours(lessons, lesson);
  const prevButton = $("prev-lesson");
  const nextButton = $("next-lesson");
  prevButton.disabled = !prev;
  nextButton.disabled = !next;
  prevButton.textContent = prev ? `← ${prev.topic}` : "← Previous chapter";
  nextButton.textContent = next ? `${next.topic} →` : "Next chapter →";

  $("assistant-lesson").textContent = lesson ? `${lesson.title} (${lesson.track} · ${lesson.subject})` : "no lesson selected";
  const suggestions = $("suggestions");
  suggestions.textContent = "";
  for (const question of suggestedQuestions(lesson)) {
    const chip = el("button", "suggestion", question);
    chip.type = "button";
    chip.addEventListener("click", () => {
      $("ask-input").value = question;
      $("ask-input").focus();
    });
    suggestions.append(chip);
  }

  const bar = $("reading-progress");
  bar.setAttribute("aria-valuenow", "0");
  $("reading-fill").style.width = "0%";
  requestAnimationFrame(updateReadingProgress);
}

function openLesson(target, { view = "study", tab = null } = {}) {
  applySelection({
    goal: examGoalOf(target.track),
    grade: gradeOf(target.track) ? `Grade ${gradeOf(target.track)}` : null,
    subject: target.subject,
    topic: target.topic,
    language: target.language,
  }, { open: true });
  showView(view);
  if (tab) selectTab(tab);
}

function applySelection(wanted, { persist = true, open = false } = {}) {
  const resolved = resolveGoalPath(lessons, wanted);
  selection = {
    goal: resolved.goal,
    grade: resolved.grade,
    track: resolved.track,
    subject: resolved.subject,
    topic: resolved.topic,
    language: resolved.language,
  };
  lesson = resolved.lesson;

  fillSelect("f-goal", availableGoals(lessons), selection.goal);

  // The grade step only exists for graded goals (NEB); CEE and IOE are single tracks.
  const grades = gradeOptions(lessons, selection.goal);
  const gradeField = $("field-grade");
  if (grades.length) {
    gradeField.hidden = false;
    fillSelect("f-grade", grades, selection.grade);
  } else {
    gradeField.hidden = true;
    $("f-grade").disabled = true;
    $("f-grade").textContent = "";
  }

  const inTrack = lessons.filter((l) => l.track === selection.track);
  fillSelect("f-subject", uniqueValues(inTrack, "subject"), selection.subject);
  fillSelect(
    "f-chapter",
    uniqueValues(inTrack.filter((l) => l.subject === selection.subject), "topic"),
    selection.topic,
  );
  fillSelect(
    "f-language",
    uniqueValues(
      inTrack.filter((l) => l.subject === selection.subject && l.topic === selection.topic),
      "language",
    ),
    selection.language,
    (value) => LANGUAGE_LABELS[value] ?? value,
  );

  renderLesson({ record: open });
  resetStudyHelp();
  renderDashboard();
  if (persist) writeStore(STATE_KEY, selection);
}

/* ----------------------- reading progress -------------------------- */

function updateReadingProgress() {
  const bar = $("reading-progress");
  if (!bar) return;
  const docHeight = document.documentElement.scrollHeight;
  const viewportHeight = window.innerHeight;
  const percent = readingProgress({ scrollY: window.scrollY, viewportHeight, docHeight });
  bar.hidden = !readingBar({ viewportHeight, docHeight });
  bar.setAttribute("aria-valuenow", String(percent));
  $("reading-fill").style.width = `${percent}%`;
}

function wireReadingProgress() {
  let queued = false;
  const queue = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      updateReadingProgress();
    });
  };
  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", queue);
}

/* ---------------------------- lesson tools ------------------------- */

function wireLessonTools() {
  $("text-smaller").addEventListener("click", () => {
    const size = nextTextSize(uiState().textSize, -1);
    applyTextSize(size);
    toast(`Text size: ${TEXT_SIZE_LABELS[size].toLowerCase()}`);
  });
  $("text-larger").addEventListener("click", () => {
    const size = nextTextSize(uiState().textSize, 1);
    applyTextSize(size);
    toast(`Text size: ${TEXT_SIZE_LABELS[size].toLowerCase()}`);
  });

  $("lesson-bookmark").addEventListener("click", () => {
    if (!lesson) return;
    const added = toggleBookmark(lesson.id);
    renderLessonTools();
    toast(added ? `Bookmarked “${lesson.topic}”.` : `Removed the bookmark for “${lesson.topic}”.`);
  });

  $("ask-about").addEventListener("click", () => {
    selectTab("ask");
    $("ask-input").focus();
  });

  $("prev-lesson").addEventListener("click", () => {
    const { prev } = chapterNeighbours(lessons, lesson);
    if (prev) openLesson(prev);
  });
  $("next-lesson").addEventListener("click", () => {
    const { next } = chapterNeighbours(lessons, lesson);
    if (next) openLesson(next);
  });
}

/* ------------------------------------------------------------------ *
 * 5. Server calls and the four Gemma 4 flows
 * ------------------------------------------------------------------ */

async function callApi(action, payload = {}, signal) {
  let response;
  try {
    response = await fetch("/api/gemma", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ action, lessonId: lesson?.id, ...payload }),
      signal,
    });
  } catch (error) {
    if (error?.name === "AbortError") throw error;
    throw Object.assign(new Error("Could not reach the server. Check your connection."), {
      code: "network",
    });
  }

  let body = null;
  try {
    body = await response.json();
  } catch {
    /* fall through to the status check below */
  }

  if (!response.ok || !body?.ok) {
    throw Object.assign(new Error(body?.error ?? `The request failed (${response.status}).`), {
      code: body?.code ?? "failed",
      status: response.status,
    });
  }
  return body.data;
}

async function probeAiStatus() {
  const chip = $("ai-status");
  const text = $("ai-status-text");
  try {
    const response = await fetch("/api/gemma", { headers: { accept: "application/json" } });
    const body = await response.json();
    aiReady = Boolean(body?.aiAvailable);
    aiMock = body?.provider === "mock";
  } catch {
    aiReady = false;
    aiMock = false;
  }
  chip.dataset.state = aiReady ? "on" : "off";
  text.textContent = aiMock ? "Local mock mode" : aiReady ? "Gemma 4 ready" : "AI off — notes only";
  $("ai-intro").textContent = aiMock
    ? "Local mock mode uses canned fixtures to exercise the study flow; these responses are not generated by Gemma 4."
    : "Every answer below is generated from the notes you have open and is labelled as AI-generated. Practice questions include a quoted lesson excerpt, but their answers are not independently verified — check them against the notes.";
  $("ai-heading").textContent = aiMock ? "Study flow · local mock" : "Study help from Gemma 4";
  $("tab-ask").textContent = aiMock ? "Ask (mock)" : "Ask Gemma 4";
  $("practice-empty").textContent = aiMock
    ? "Local mock questions are canned fixtures, not Gemma output or official exam papers."
    : "Akshar writes multiple-choice questions from the notes above. Each includes a matching excerpt for checking; answer accuracy still needs your review. These are generated questions, not official exam papers.";
  $("summary-empty").textContent = aiMock
    ? "A canned local fixture will exercise the summary panel; it is not generated by Gemma 4."
    : "Gemma 4 writes a short summary of the notes above, in the language of the notes.";
  $("ai-off").hidden = aiReady;
  for (const id of ["summary-run", "ask-submit", "practice-run", "flashcards-run"]) {
    const button = $(id);
    if (button) button.disabled = !aiReady;
  }
  if (!aiReady) {
    for (const panel of ["summary", "ask", "practice", "flashcards"]) {
      setState(`${panel}-state`, "off", "AI features are off, so this panel cannot run yet.");
    }
  }
}

let summaryCache = null;
let inflight = null;

function runWithButton(button, task) {
  const original = button.textContent;
  button.disabled = true;
  button.textContent = "Working…";
  const controller = new AbortController();
  if (inflight) inflight.abort();
  inflight = controller;
  return task(controller.signal)
    .catch((error) => {
      if (error?.name !== "AbortError") throw error;
    })
    .finally(() => {
      button.disabled = !aiReady;
      button.textContent = original;
    });
}

/** Clear every AI surface when the selected lesson changes. */
function resetStudyHelp() {
  summaryCache = null;
  askHistory = [];
  practiceQuestions = null;
  practiceAnswers = new Map();
  quizSubmitted = false;
  for (const id of ["summary-state", "ask-state", "practice-state", "flashcards-state"]) {
    setState(id, "loading", "");
  }
  if (!aiReady) {
    for (const panel of ["summary", "ask", "practice", "flashcards"]) {
      setState(`${panel}-state`, "off", "AI features are off, so this panel cannot run yet.");
    }
  }
  $("summary-result").hidden = true;
  $("summary-result").textContent = "";
  $("summary-empty").hidden = false;
  $("summary-reset").hidden = true;
  $("summary-run").textContent = "Explain this lesson";
  $("ask-thread").textContent = "";
  $("ask-empty").hidden = false;
  $("ask-clear").hidden = true;
  $("quiz").hidden = true;
  $("quiz").textContent = "";
  $("quiz-progress").hidden = true;
  $("practice-empty").hidden = false;
  $("flashcards-list").hidden = true;
  $("flashcards-list").textContent = "";
  $("flashcards-empty").hidden = false;
  $("flashcards-run").textContent = "Build flashcards";
}

/* ----------------------------- Explain ---------------------------- */

function renderSummary(text) {
  const box = $("summary-result");
  box.hidden = false;
  box.textContent = "";
  box.append(
    el("strong", "disclosure", aiMock ? "Local mock response · not Gemma 4" : "AI-generated summary · Gemma 4"),
    el("p", null, text),
  );
}

function wireExplain() {
  $("summary-run").addEventListener("click", () => {
    if (summaryCache) {
      renderSummary(summaryCache);
      return;
    }
    runWithButton($("summary-run"), async (signal) => {
      const startedAt = performance.now();
      setState("summary-state", "loading", aiMock ? "Loading a canned local summary…" : "Gemma 4 is writing a summary of these notes…");
      try {
        const summary = await callApi("summary", {}, signal);
        summaryCache = summary;
        setState("summary-state", "success", `${aiMock ? "Mock summary loaded" : "Summary generated"} in ${formatGenerationDuration(performance.now() - startedAt)}.`);
        $("summary-empty").hidden = true;
        renderSummary(summary);
        $("summary-reset").hidden = false;
        $("summary-run").textContent = "Show summary";
      } catch (error) {
        if (error?.name === "AbortError") return;
        setState("summary-state", "error", `${error.message} Press "Explain this lesson" to try again.`);
      }
    });
  });

  $("summary-reset").addEventListener("click", () => {
    summaryCache = null;
    $("summary-result").hidden = true;
    $("summary-result").textContent = "";
    $("summary-empty").hidden = false;
    $("summary-reset").hidden = true;
    $("summary-run").textContent = "Explain this lesson";
    setState("summary-state", null, "");
  });
}

/* -------------------------- Ask Gemma 4 --------------------------- */

let askHistory = [];

function renderThread() {
  const thread = $("ask-thread");
  thread.textContent = "";
  for (const turn of askHistory) {
    const wrap = el("div", `turn turn--${turn.role === "user" ? "user" : "assistant"}`);
    wrap.append(
      el("span", "turn__role", turn.role === "user" ? "You" : aiMock ? "Local mock response" : "Gemma 4 · AI-generated"),
      el("p", "turn__body", turn.content),
    );
    thread.append(wrap);
  }
  $("ask-empty").hidden = askHistory.length > 0;
  $("ask-clear").hidden = askHistory.length === 0;
}

function wireAsk() {
  $("ask-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const input = $("ask-input");
    const question = input.value.trim();
    if (!question) {
      setState("ask-state", "error", "Type a question first.");
      input.focus();
      return;
    }
    const previous = askHistory.slice();
    askHistory.push({ role: "user", content: question });
    renderThread();
    input.value = "";

    runWithButton($("ask-submit"), async (signal) => {
      const startedAt = performance.now();
      setState("ask-state", "loading", aiMock ? "Loading a canned local reply…" : "Gemma 4 is reading the notes to answer…");
      const pending = renderPendingAnswer();
      try {
        const answer = await callApi(
          "ask",
          { question, history: previous, language: $("ask-language").value || null },
          signal,
        );
        askHistory.push({ role: "assistant", content: answer });
        setState("ask-state", "success", `${aiMock ? "Mock reply loaded" : "Answered"} in ${formatGenerationDuration(performance.now() - startedAt)}.`);
        renderThread();
        const turns = $("ask-thread").querySelectorAll(".turn");
        if (turns.length) turns[turns.length - 1].scrollIntoView({ block: "nearest" });
      } catch (error) {
        if (error?.name === "AbortError") return;
        setState("ask-state", "error", `${error.message} Ask again to retry.`);
      } finally {
        pending?.remove();
      }
    });
  });

  $("ask-clear").addEventListener("click", () => {
    askHistory = [];
    renderThread();
    setState("ask-state", null, "");
  });
}

/** A placeholder answer while the model is working, marked busy for screen readers. */
function renderPendingAnswer() {
  const thread = $("ask-thread");
  if (!thread) return null;
  thread.setAttribute("aria-busy", "true");
  const bubble = el("div", "turn turn--assistant turn--pending");
  bubble.setAttribute("aria-hidden", "true");
  for (const width of ["82%", "64%"]) {
    const line = el("span", "skeleton-line");
    line.style.width = width;
    bubble.append(line);
  }
  thread.append(bubble);
  bubble.scrollIntoView({ block: "nearest" });
  // renderThread() clears the thread when the answer lands, but making the
  // busy state explicit keeps it correct if that ever changes.
  const stop = () => thread.removeAttribute("aria-busy");
  const observer = new MutationObserver(() => {
    if (!thread.contains(bubble)) {
      stop();
      observer.disconnect();
    }
  });
  observer.observe(thread, { childList: true });
  return bubble;
}

/* ---------------------------- Practise ---------------------------- */

let practiceQuestions = null;
let practiceAnswers = new Map();
let quizSubmitted = false;
let dialogConfirm = null;
let quizStartedAt = 0;

function practiceMode() {
  const checked = document.querySelector('input[name="practice-mode"]:checked');
  return checked?.value === "exam" ? "exam" : "practice";
}

function updateQuizProgress() {
  const total = practiceQuestions?.length ?? 0;
  const answered = practiceAnswers.size;
  const percent = total ? Math.round((answered / total) * 100) : 0;
  $("quiz-progress-bar").setAttribute("aria-valuenow", String(percent));
  $("quiz-progress-fill").style.width = `${percent}%`;
  $("quiz-progress-text").textContent = total
    ? `${answered} of ${total} answered · ${
        practiceMode() === "exam"
          ? "answers stay hidden until you submit"
          : "each answer is checked as you choose it"
      }`
    : "";
  for (const fieldset of document.querySelectorAll("#quiz .question")) {
    fieldset.dataset.answered = String(practiceAnswers.has(Number(fieldset.dataset.index)));
  }
}

/** In practice mode, mark the chosen answer and show why, straight away. */
function markQuestion(index) {
  const fieldset = document.querySelector(`#quiz .question[data-index="${index}"]`);
  if (!fieldset) return;
  const question = practiceQuestions[index];
  const chosen = practiceAnswers.get(index);
  const correct = chosen === question.answer;
  for (const row of fieldset.querySelectorAll(".option")) {
    const value = row.querySelector("input").value;
    row.classList.toggle("option--correct", Boolean(chosen) && value === question.answer);
    row.classList.toggle("option--wrong", Boolean(chosen) && value === chosen && !correct);
  }
  const feedback = fieldset.querySelector(".feedback");
  if (!chosen) {
    feedback.hidden = true;
    return;
  }
  feedback.hidden = false;
  feedback.dataset.kind = correct ? "correct" : "wrong";
  const verdict = correct
    ? `Correct. ${question.explanation}`
    : `Not correct — the answer is ${question.answer}. ${question.explanation}`;
  feedback.textContent = `${verdict} Lesson evidence: “${question.evidence}”`;
}

function chooseAnswer(index, value) {
  practiceAnswers.set(index, value);
  updateQuizProgress();
  if (practiceMode() === "practice" && !quizSubmitted) markQuestion(index);
}

function renderQuizForm() {
  const form = $("quiz");
  form.textContent = "";
  form.hidden = false;
  practiceAnswers = new Map();
  quizSubmitted = false;
  quizStartedAt = Date.now();
  setState("practice-state", null, "");
  $("quiz-progress").hidden = false;

  practiceQuestions.forEach((question, index) => {
    const fieldset = el("fieldset", "question");
    fieldset.dataset.index = String(index);
    fieldset.append(el("legend", null, `Q${index + 1}. ${question.question}`));
    for (const key of ["A", "B", "C", "D"]) {
      const row = el("label", "option");
      const input = document.createElement("input");
      input.type = "radio";
      input.name = `q${index}`;
      input.value = key;
      input.addEventListener("change", () => chooseAnswer(index, key));
      row.append(input, el("span", "option__text", `${key}. ${question.options[key]}`));
      fieldset.append(row);
    }
    const feedback = el("p", "feedback");
    feedback.hidden = true;
    fieldset.append(feedback);
    form.append(fieldset);
  });

  const submit = el("button", "button button--primary", "Mark my answers");
  submit.type = "submit";
  form.append(submit);

  // Assigned rather than added: re-rendering the quiz replaces the handler, and
  // an invalid submit must not consume it.
  form.onsubmit = (event) => {
    event.preventDefault();
    const missing = practiceQuestions
      .map((_question, index) => index)
      .filter((index) => !practiceAnswers.has(index));

    if (missing.length && practiceMode() === "exam") {
      dialogConfirm = () => {
        form.onsubmit = null;
        renderQuizGraded(practiceAnswers);
      };
      $("submit-dialog-text").textContent = `${missing.length} question${
        missing.length === 1 ? " is" : "s are"
      } still blank. Blank questions are marked as unanswered.`;
      const dialog = $("submit-dialog");
      if (typeof dialog.showModal === "function") dialog.showModal();
      else dialogConfirm();
      return;
    }

    if (missing.length) {
      setState(
        "practice-state",
        "error",
        `Answer every question before marking — Q${missing[0] + 1} is still blank.`,
      );
      form.querySelector(`input[name="q${missing[0]}"]`)?.focus();
      return;
    }

    form.onsubmit = null;
    renderQuizGraded(practiceAnswers);
  };

  updateQuizProgress();
  form.querySelector("input")?.focus({ preventScroll: true });
}

function wrapReview(review, index, question, chosen) {
  const item = el("div", "review__item");
  const verdict = !chosen ? "not answered" : chosen === question.answer ? "correct" : "not correct";
  item.append(el("p", "review__verdict", `Q${index + 1} — ${verdict}.`));
  item.append(
    el("p", null, `Correct answer: ${question.answer}. ${question.options[question.answer]}`),
  );
  item.append(el("p", null, `Why: ${question.explanation}`));
  item.append(el("p", null, `Lesson evidence: “${question.evidence}”`));
  if (chosen) item.append(el("p", "review__yours", `You chose ${chosen}.`));
  review.append(item);
}

function renderQuizGraded(answers) {
  const form = $("quiz");
  const summary = quizSummary(practiceQuestions, answers);
  quizSubmitted = true;
  form.textContent = "";
  $("quiz-progress").hidden = true;
  setState("practice-state", null, "");

  const card = el("div", "result-card");

  const score = el("div", "score score--hero");
  score.tabIndex = -1;
  score.append(
    el("span", "score__value", `${summary.correct} / ${summary.total}`),
    el(
      "span",
      "score__label",
      `${summary.percent}% correct · ${aiMock ? "local mock questions" : "AI-generated questions"}, not an official exam`,
    ),
  );
  card.append(score);

  const counts = el("ul", "result-counts");
  const countItem = (className, label, value) => {
    const item = el("li", `count-chip ${className}`);
    item.append(el("span", "count-chip__value", String(value)), el("span", "count-chip__label", label));
    return item;
  };
  counts.append(
    countItem("count-chip--correct", "correct", summary.correct),
    countItem("count-chip--wrong", "incorrect", summary.incorrect),
    countItem("count-chip--blank", "unanswered", summary.unanswered),
  );
  card.append(counts);

  card.append(
    el(
      "p",
      "result-facts",
      `Answered ${summary.answered} of ${summary.total} · accuracy ${summary.accuracy}% on the questions you answered.`,
    ),
  );

  if (quizStartedAt) {
    card.append(
      el(
        "p",
        "result-facts result-facts--quiet",
        `Time on this set: ${formatDuration(Date.now() - quizStartedAt)} — counted in this tab, from when the questions appeared.`,
      ),
    );
  }

  const state = progressState();
  if (state.best) {
    card.append(el("p", "result-facts", `Best in this browser: ${state.best.score} / ${state.best.total}.`));
  }

  const missed = summary.incorrect + summary.unanswered;
  card.append(
    el(
      "p",
      "result-revisit",
      missed && lesson
        ? `Revise ${lesson.topic}: ${summary.incorrect} wrong and ${summary.unanswered} blank in this set. Read the notes again, then try a fresh set.`
        : "Every answer was correct. Try a longer set or move on to the next chapter.",
    ),
  );

  const actions = el("div", "result-actions");
  const fresh = el("button", "button button--primary", "New questions");
  fresh.type = "button";
  fresh.addEventListener("click", () => $("practice-run").click());
  const again = el("button", "button", "Try these again");
  again.type = "button";
  again.addEventListener("click", () => renderQuizForm());
  const home = el("button", "button button--quiet", "Back to dashboard");
  home.type = "button";
  home.addEventListener("click", () => showView("home", { focus: true }));
  actions.append(fresh, again, home);
  card.append(actions);

  const review = el("div", "review");
  review.append(el("h3", null, "Check every answer against the notes"));
  practiceQuestions.forEach((question, index) => {
    wrapReview(review, index, question, answers instanceof Map ? answers.get(index) : answers[index]);
  });
  card.append(review);

  form.append(card);
  score.focus();
  recordAttempt(summary.correct, summary.total);
}

function wirePractice() {
  $("practice-run").addEventListener("click", () => {
    runWithButton($("practice-run"), async (signal) => {
      const startedAt = performance.now();
      setState("practice-state", "loading", aiMock ? "Loading canned local questions…" : "Gemma 4 is writing questions from these notes…");
      try {
        const questions = await callApi("mcqs", { count: Number($("practice-count").value) }, signal);
        practiceQuestions = questions;
        $("practice-empty").hidden = true;
        setState("practice-state", null, "");
        renderQuizForm();
        setState("practice-state", "success", `${aiMock ? "Mock questions loaded" : "Questions generated"} in ${formatGenerationDuration(performance.now() - startedAt)}.`);
      } catch (error) {
        if (error?.name === "AbortError") return;
        $("quiz").hidden = true;
        $("quiz-progress").hidden = true;
        setState("practice-state", "error", `${error.message} Try again in a moment.`);
      }
    });
  });

  for (const radio of document.querySelectorAll('input[name="practice-mode"]')) {
    radio.addEventListener("change", () => {
      if (practiceQuestions && !quizSubmitted) {
        for (const index of practiceAnswers.keys()) markQuestion(index);
      }
      updateQuizProgress();
    });
  }

  $("submit-dialog-cancel").addEventListener("click", () => {
    $("submit-dialog").close();
    dialogConfirm = null;
  });
  $("submit-dialog-confirm").addEventListener("click", () => {
    $("submit-dialog").close();
    const run = dialogConfirm;
    dialogConfirm = null;
    if (run) run();
  });
}

/* --------------------------- Flashcards --------------------------- */

function renderCards(cards) {
  const list = $("flashcards-list");
  list.textContent = "";
  list.hidden = false;
  cards.forEach((card, index) => {
    const details = el("details", "card");
    details.append(el("summary", null, `Card ${index + 1} · ${card.question}`));
    details.append(el("p", "card__answer", card.answer));
    list.append(details);
  });
}

function wireFlashcards() {
  $("flashcards-run").addEventListener("click", () => {
    runWithButton($("flashcards-run"), async (signal) => {
      const startedAt = performance.now();
      setState("flashcards-state", "loading", aiMock ? "Loading canned local flashcards…" : "Gemma 4 is writing flashcards from these notes…");
      try {
        const cards = await callApi(
          "flashcards",
          { count: Number($("flashcards-count").value) },
          signal,
        );
        $("flashcards-empty").hidden = true;
        setState("flashcards-state", "success", `${aiMock ? "Mock flashcards loaded" : "Flashcards generated"} in ${formatGenerationDuration(performance.now() - startedAt)}.`);
        renderCards(cards);
        $("flashcards-run").textContent = "Build a new set";
      } catch (error) {
        if (error?.name === "AbortError") return;
        $("flashcards-list").hidden = true;
        setState("flashcards-state", "error", `${error.message} Try again in a moment.`);
      }
    });
  });
}

/* ------------------------------------------------------------------ *
 * 6. Wiring and bootstrap
 * ------------------------------------------------------------------ */

function syncAiStates() {
  if (!aiReady) return;
  for (const panel of ["summary", "ask", "practice", "flashcards"]) {
    const node = $(`${panel}-state`);
    if (node && node.dataset.kind === "off") setState(`${panel}-state`, null, "");
  }
}

function wireFilters() {
  const map = {
    "f-goal": "goal",
    "f-grade": "grade",
    "f-subject": "subject",
    "f-chapter": "topic",
    "f-language": "language",
  };
  for (const [id, key] of Object.entries(map)) {
    $(id).addEventListener("change", (event) => {
      applySelection({ ...selection, [key]: event.target.value }, { open: true });
    });
  }
}

function wireProgress() {
  $("progress-reset").addEventListener("click", () => {
    saveProgress(emptyProgress());
    toast("Progress cleared in this browser.");
  });
  $("continue-action").addEventListener("click", () => {
    if ($("continue-action").dataset.mode === "choose") {
      showView("study", { focus: true });
      return;
    }
    const model = dashboardModel(lessons, progressState());
    if (model.continueLesson) openLesson(model.continueLesson);
    else showView("study", { focus: true });
  });
  $("resume").addEventListener("click", () => {
    const model = dashboardModel(lessons, progressState());
    if (model.continueLesson) openLesson(model.continueLesson);
    else showView("study", { focus: true });
  });
  $("practise-next").addEventListener("click", () => {
    const model = dashboardModel(lessons, progressState());
    if (model.continueLesson) openLesson(model.continueLesson, { tab: "practise" });
    else {
      showView("study", { focus: true });
      selectTab("practise");
    }
  });
}

async function init() {
  wireTabs();
  wireExplain();
  wireAsk();
  wirePractice();
  wireFlashcards();
  wireFilters();
  wireProgress();
  wireViews();
  wireLessonTools();
  wireReadingProgress();
  applyTextSize(uiState().textSize);
  renderProgress();
  selectTab("explain");

  try {
    const response = await fetch("./data/lessons.json", { cache: "no-cache" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const parsed = await response.json();
    lessons = Array.isArray(parsed) ? parsed : (parsed.lessons ?? []);
    if (!lessons.length) throw new Error("No lessons are available yet.");
    const saved = readStore(STATE_KEY) ?? {};
    if (!saved.goal && saved.track) {
      saved.goal = examGoalOf(saved.track);
      saved.grade = gradeOf(saved.track) ? `Grade ${gradeOf(saved.track)}` : null;
    }
    applySelection(saved, { persist: false });
  } catch (error) {
    $("load-error").hidden = false;
    $("load-error-text").textContent = `${error.message} Reload the page to try again.`;
    for (const panel of document.querySelectorAll("[data-view-panel]")) panel.hidden = true;
    return;
  }

  renderDashboard();
  showView(location.hash.replace("#", "") || "home");
  await probeAiStatus();
  syncAiStates();
  updateReadingProgress();
}

if (typeof document !== "undefined" && document.getElementById("study")) {
  init();
}
