/**
 * Akshar web app.
 *
 * Reads lesson content from ./data/lessons.json and sends only a lesson id to
 * /api/gemma — the model key never reaches the browser, and neither does the
 * prompt. Everything the model returns is untrusted text: it is inserted with
 * textContent, never as HTML.
 */

const STATE_KEY = "akshar:study";
const PROGRESS_KEY = "akshar:progress";
const LANGUAGE_LABELS = { en: "English", ne: "Nepali" };

let lessons = [];
let selection = { track: null, subject: null, topic: null, language: null };
let lesson = null;
let aiReady = false;

const $ = (id) => document.getElementById(id);
const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

/* ------------------------------------------------------------------ *
 * Small storage helpers (private browsing must not break the app)
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

export function progressState() {
  return readStore(PROGRESS_KEY) ?? { lessons: {}, attempts: 0, best: null };
}

function saveProgress(state) {
  writeStore(PROGRESS_KEY, state);
  renderProgress();
}

function renderProgress() {
  const state = progressState();
  $("stat-lessons").textContent = String(Object.keys(state.lessons ?? {}).length);
  $("stat-attempts").textContent = String(state.attempts ?? 0);
  $("stat-best").textContent = state.best
    ? `${state.best.score} / ${state.best.total}`
    : "—";
}

function markLessonOpened(id) {
  const state = progressState();
  state.lessons = state.lessons ?? {};
  if (!state.lessons[id]) {
    state.lessons[id] = true;
    saveProgress(state);
  }
}

function recordAttempt(score, total) {
  const state = progressState();
  state.attempts = (state.attempts ?? 0) + 1;
  const best = state.best;
  if (!best || score / total > best.score / best.total) {
    state.best = { score, total };
  }
  saveProgress(state);
}

/* ------------------------------------------------------------------ *
 * Selection resolution — the same contract as content.resolve_study_path
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

/* ------------------------------------------------------------------ *
 * Rendering the study selection and the lesson
 * ------------------------------------------------------------------ */

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
  const blocks = text.split(/\n\s*\n/).map((block) => block.trim()).filter(Boolean);
  for (const block of blocks) {
    const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
    if (lines.every((line) => /^[-•*]\s+/.test(line))) {
      const list = document.createElement("ul");
      for (const line of lines) list.append(el("li", null, line.replace(/^[-•*]\s+/, "")));
      box.append(list);
    } else {
      box.append(el("p", null, lines.join(" ")));
    }
  }
}

function renderLesson() {
  const title = $("lesson-title");
  const chips = $("lesson-chips");
  const path = $("path");
  title.textContent = "";
  chips.textContent = "";
  path.textContent = "";

  if (!lesson) {
    title.textContent = "No lesson matches this selection";
    $("lesson-content").textContent = "";
    return;
  }

  title.textContent = lesson.title;
  title.setAttribute("lang", lesson.language === "ne" ? "ne" : "en");

  const languageChip = el("span", "chip chip--brand", LANGUAGE_LABELS[lesson.language] ?? lesson.language);
  chips.append(languageChip);
  chips.append(el("span", "chip", lesson.subject));
  chips.append(el("span", "chip", lesson.track));

  const parts = [selection.track, selection.subject, selection.topic, LANGUAGE_LABELS[selection.language] ?? ""];
  parts.filter(Boolean).forEach((value, index) => {
    if (index) path.append(el("span", "path__sep", "/"));
    path.append(el("span", null, value));
  });

  $("source-label").textContent = `Source · ${LANGUAGE_LABELS[lesson.language] ?? lesson.language}`;
  renderLessonContent(lesson.content, lesson.language);
  markLessonOpened(lesson.id);
}

function applySelection(wanted, { persist = true } = {}) {
  const resolved = resolveSelection(lessons, wanted);
  selection = {
    track: resolved.track,
    subject: resolved.subject,
    topic: resolved.topic,
    language: resolved.language,
  };
  lesson = resolved.lesson;

  fillSelect("f-track", uniqueValues(lessons, "track"), selection.track);
  fillSelect(
    "f-subject",
    uniqueValues(lessons.filter((l) => l.track === selection.track), "subject"),
    selection.subject,
  );
  fillSelect(
    "f-topic",
    uniqueValues(
      lessons.filter((l) => l.track === selection.track && l.subject === selection.subject),
      "topic",
    ),
    selection.topic,
  );
  fillSelect(
    "f-language",
    uniqueValues(
      lessons.filter(
        (l) =>
          l.track === selection.track &&
          l.subject === selection.subject &&
          l.topic === selection.topic,
      ),
      "language",
    ),
    selection.language,
    (value) => LANGUAGE_LABELS[value] ?? value,
  );

  renderLesson();
  resetStudyHelp();
  if (persist) writeStore(STATE_KEY, selection);
}

/* ------------------------------------------------------------------ *
 * Tabs
 * ------------------------------------------------------------------ */

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

/* ------------------------------------------------------------------ *
 * Server calls
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
  } catch {
    aiReady = false;
  }
  chip.dataset.state = aiReady ? "on" : "off";
  text.textContent = aiReady ? "Gemma 4 ready" : "AI off — notes only";
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

/* ------------------------------------------------------------------ *
 * State messages and study-help reset
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

function resetStudyHelp() {
  summaryCache = null;
  askHistory = [];
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
  $("ask-thread").textContent = "";
  $("ask-empty").hidden = false;
  $("ask-clear").hidden = true;
  $("quiz").hidden = true;
  $("quiz").textContent = "";
  $("practice-empty").hidden = false;
  $("flashcards-list").hidden = true;
  $("flashcards-list").textContent = "";
  $("flashcards-empty").hidden = false;
}

/* ------------------------------------------------------------------ *
 * Explain
 * ------------------------------------------------------------------ */

let summaryCache = null;
let inflight = null;

function runWithButton(button, stateId, task) {
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

function wireExplain() {
  $("summary-run").addEventListener("click", () => {
    if (summaryCache) {
      $("summary-result").hidden = false;
      $("summary-result").textContent = "";
      const disclosure = el("strong", "disclosure", "AI-generated summary · Gemma 4");
      const body = el("p", null, summaryCache);
      $("summary-result").append(disclosure, body);
      return;
    }
    runWithButton($("summary-run"), "summary-state", async (signal) => {
      setState("summary-state", "loading", "Gemma 4 is writing a summary of these notes…");
      try {
        const summary = await callApi("summary", {}, signal);
        summaryCache = summary;
        setState("summary-state", null, "");
        $("summary-empty").hidden = true;
        $("summary-result").hidden = false;
        $("summary-result").textContent = "";
        $("summary-result").append(
          el("strong", "disclosure", "AI-generated summary · Gemma 4"),
          el("p", null, summary),
        );
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

/* ------------------------------------------------------------------ *
 * Ask Gemma 4
 * ------------------------------------------------------------------ */

let askHistory = [];

function renderThread() {
  const thread = $("ask-thread");
  thread.textContent = "";
  for (const turn of askHistory) {
    const wrap = el("div", "turn");
    wrap.append(
      el("span", "turn__role", turn.role === "user" ? "You" : "Gemma 4 · AI-generated"),
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

    runWithButton($("ask-submit"), "ask-state", async (signal) => {
      setState("ask-state", "loading", "Gemma 4 is reading the notes to answer…");
      try {
        const answer = await callApi(
          "ask",
          {
            question,
            history: previous,
            language: $("ask-language").value || null,
          },
          signal,
        );
        askHistory.push({ role: "assistant", content: answer });
        setState("ask-state", null, "");
        renderThread();
        const turns = $("ask-thread").querySelectorAll(".turn");
        if (turns.length) turns[turns.length - 1].scrollIntoView({ block: "nearest" });
      } catch (error) {
        if (error?.name === "AbortError") return;
        setState("ask-state", "error", `${error.message} Ask again to retry.`);
      }
    });
  });

  $("ask-clear").addEventListener("click", () => {
    askHistory = [];
    renderThread();
    setState("ask-state", null, "");
  });
}

/* ------------------------------------------------------------------ *
 * Practise
 * ------------------------------------------------------------------ */

let practiceQuestions = null;

function renderQuizGraded(answers) {
  const form = $("quiz");
  let score = 0;
  form.textContent = "";

  practiceQuestions.forEach((question, index) => {
    const chosen = answers.get(index);
    const correct = chosen === question.answer;
    if (correct) score += 1;

    const fieldset = el("fieldset", "question");
    fieldset.append(el("legend", null, `Q${index + 1}. ${question.question}`));
    for (const key of ["A", "B", "C", "D"]) {
      const row = el("label", "option");
      const input = document.createElement("input");
      input.type = "radio";
      input.name = `q${index}`;
      input.value = key;
      input.checked = chosen === key;
      input.disabled = true;
      if (key === question.answer) row.classList.add("option--correct");
      else if (chosen === key) row.classList.add("option--wrong");
      row.append(input, el("span", null, `${key}. ${question.options[key]}`));
      if (key === question.answer) row.append(el("span", "option__mark", "correct"));
      else if (chosen === key) row.append(el("span", "option__mark", "your answer"));
      fieldset.append(row);
    }
    form.append(fieldset);
  });

  const total = practiceQuestions.length;
  const percent = Math.round((score / total) * 100);
  const summary = el("div", "score");
  summary.append(
    el("span", "score__value", `${score} / ${total} (${percent}%)`),
    el("span", "score__label", "correct on this attempt · AI-generated, not official exam questions"),
  );

  const state = progressState();
  if (state.best) {
    summary.append(
      el("span", "score__label", `Best in this browser: ${state.best.score} / ${state.best.total}`),
    );
  }

  const review = el("div", "review");
  review.append(el("h3", null, "Check every answer against the notes"));
  practiceQuestions.forEach((question, index) => {
    const chosen = answers.get(index);
    wrapReview(review, index, question, chosen);
  });

  const again = el("button", "button", "Try these again");
  again.type = "button";
  again.addEventListener("click", () => renderQuizForm());

  form.append(summary, review, again);
  recordAttempt(score, total);
}

function wrapReview(review, index, question, chosen) {
  const item = el("div");
  const verdict = chosen === question.answer ? "correct" : "not correct";
  item.append(el("p", null, `Q${index + 1} — ${verdict}.`));
  item.append(el("p", null, `Correct answer: ${question.answer}. ${question.options[question.answer]}`));
  item.append(el("p", null, `Why: ${question.explanation}`));
  review.append(item);
}

function renderQuizForm() {
  const form = $("quiz");
  form.textContent = "";
  form.hidden = false;
  setState("practice-state", null, "");

  practiceQuestions.forEach((question, index) => {
    const fieldset = el("fieldset", "question");
    fieldset.append(el("legend", null, `Q${index + 1}. ${question.question}`));
    for (const key of ["A", "B", "C", "D"]) {
      const row = el("label", "option");
      const input = document.createElement("input");
      input.type = "radio";
      input.name = `q${index}`;
      input.value = key;
      row.append(input, el("span", null, `${key}. ${question.options[key]}`));
      fieldset.append(row);
    }
    form.append(fieldset);
  });

  const submit = el("button", "button button--primary", "Mark my answers");
  submit.type = "submit";
  form.append(submit);

  // Assigned rather than added: re-rendering the quiz replaces the handler, and
  // an invalid submit must not consume it.
  form.onsubmit = (event) => {
    event.preventDefault();
    const answers = new Map();
    practiceQuestions.forEach((_question, index) => {
      const picked = form.querySelector(`input[name="q${index}"]:checked`);
      if (picked) answers.set(index, picked.value);
    });
    if (answers.size < practiceQuestions.length) {
      const missing = practiceQuestions.findIndex((_q, index) => !answers.has(index));
      setState(
        "practice-state",
        "error",
        `Answer every question before marking — Q${missing + 1} is still blank.`,
      );
      form.querySelector(`input[name="q${missing}"]`)?.focus();
      return;
    }
    form.onsubmit = null;
    renderQuizGraded(answers);
  };
}

function wirePractice() {
  $("practice-run").addEventListener("click", () => {
    runWithButton($("practice-run"), "practice-state", async (signal) => {
      setState("practice-state", "loading", "Gemma 4 is writing questions from these notes…");
      try {
        const questions = await callApi(
          "mcqs",
          { count: Number($("practice-count").value) },
          signal,
        );
        practiceQuestions = questions;
        $("practice-empty").hidden = true;
        setState("practice-state", null, "");
        renderQuizForm();
      } catch (error) {
        if (error?.name === "AbortError") return;
        $("quiz").hidden = true;
        setState("practice-state", "error", `${error.message} Try again in a moment.`);
      }
    });
  });
}

/* ------------------------------------------------------------------ *
 * Flashcards
 * ------------------------------------------------------------------ */

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
    runWithButton($("flashcards-run"), "flashcards-state", async (signal) => {
      setState("flashcards-state", "loading", "Gemma 4 is writing flashcards from these notes…");
      try {
        const cards = await callApi(
          "flashcards",
          { count: Number($("flashcards-count").value) },
          signal,
        );
        $("flashcards-empty").hidden = true;
        setState("flashcards-state", null, "");
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
 * Filters, progress, bootstrap
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
    "f-track": "track",
    "f-subject": "subject",
    "f-topic": "topic",
    "f-language": "language",
  };
  for (const [id, key] of Object.entries(map)) {
    $(id).addEventListener("change", (event) => {
      applySelection({ ...selection, [key]: event.target.value });
    });
  }
}

function wireProgress() {
  $("progress-reset").addEventListener("click", () => {
    saveProgress({ lessons: {}, attempts: 0, best: null });
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
  renderProgress();
  selectTab("explain");

  try {
    const response = await fetch("./data/lessons.json", { cache: "no-cache" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const parsed = await response.json();
    lessons = Array.isArray(parsed) ? parsed : (parsed.lessons ?? []);
    if (!lessons.length) throw new Error("No lessons are available yet.");
    applySelection(readStore(STATE_KEY) ?? {}, { persist: false });
  } catch (error) {
    $("load-error").hidden = false;
    $("load-error-text").textContent = `${error.message} Reload the page to try again.`;
    $("study").hidden = true;
    return;
  }

  await probeAiStatus();
  syncAiStates();
}

if (typeof document !== "undefined" && document.getElementById("study")) {
  init();
}
