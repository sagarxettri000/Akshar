# Security Review: Nepluro Application

## Overview
Nepluro is a local Streamlit-based educational app for learning with Gemma 4 AI. It reads from a static `lessons.json` file and calls the Google GenAI API for AI-powered features.

## Threat Model
- **Trusted inputs**: Lesson content from `data/lessons.json` (author-edited)
- **Semi-trusted inputs**: User questions via `ask_question()` API
- **Untrusted outputs**: AI-generated content (summary, MCQs, flashcards, answers)
- **No user accounts**: Session-state only, no persistent storage
- **No file uploads**: Only reads from `lessons.json`

## Severity Classification
- **High**: Credential exposure, arbitrary code execution, data exfiltration
- **Medium**: Information disclosure that aids attacks
- **Low**: Minor information disclosure, usability issues

## Findings

### 1. API Key Management ✅
**Location**: `ai_service.py:_clean_api_key()`, `get_api_key()` in `app.py`
**Status**: **Good practice**
- API keys are read from `st.secrets["GOOGLE_API_KEY"]` or environment variables
- `_redact_secret()` masks keys in error messages
- `secrets.toml.example` is gitignored; real `secrets.toml` must not be committed
- **No API keys in code, logs, or test fixtures**

**Recommendation**: Maintain current practice. No changes needed.

---

### 2. Error Message Disclosure ✅
**Location**: `app.py` practice tab, `ai_service.py:_generate_text()`, various `st.error()` calls
**Status**: **Low risk**
- Error messages are shown to users via `st.error()` / `st.warning()`
- AI service errors generic: "The Gemma 4 request failed: ..."
- Contains `{exc}` but these are AI SDK exceptions, not system exceptions
- No stack traces, file paths, or internal details exposed to end users

**Examples**:
- `st.error(f"Could not generate a summary: {exc}")` - line 93
- `st.error(f"Could not answer: {exc}")` - line 275
- `st.error(f"Could not load lesson content: {exc}")` - line 300

**Recommendation**: Current messages are acceptable. No user-exposed secrets or internal details.

---

### 3. st.markdown Rendering ✅
**Location**: `app.py` lines 98, 134, 188-195, 242
**Status**: **Low risk - trusted content only**
- All `st.markdown()` calls render content from `lessons.json` (author-edited)
- No user-generated content is rendered via markdown in the current flow
- `st.markdown(message["content"])` at line 242 renders chat history from AI, which is instructed to return plain text per the `_GROUNDED_DIRECTIVE`
- No `unsafe_allow_html=True` used anywhere

**Examples**:
- `st.markdown(f"**Q{index}. {question['question']}**")` - line 134
- `st.markdown(f"Your answer: **{student_letter}.** ...")` - line 189
- `st.markdown(summary)` - line 98 (AI summary)

**Recommendation**: Content is trusted (from `lessons.json`). No sanitization needed, but if user-generated content is ever added, sanitize before rendering.

---

### 4. Input Validation ✅
**Location**: `ai_service.py:_clean_lesson_text()`, `_clean_api_key()`, `_clean_question()`, `_clean_history()`, `_clean_answer_language()`
**Status**: **Good practice**
- All public functions validate inputs before processing
- `InvalidInputError` raised for: empty strings, wrong types, out-of-range values
- History entries with wrong role/content are dropped (not raised), preventing corrupt state

**Examples**:
- `_clean_lesson_text()`: raises if not non-empty string
- `_clean_api_key()`: raises if not non-empty string
- `_clean_question()`: raises if > MAX_QUESTION_LENGTH (1000 chars)
- `_clean_history()`: drops malformed entries silently

**Recommendation**: Current validation is thorough and appropriate. No changes needed.

---

### 5. File Path Safety ✅
**Location**: `content.py:load_lessons()`, `DEFAULT_LESSONS_PATH`
**Status**: **Good practice**
- `load_lessons()` uses a fixed path: `Path(__file__).resolve().parent / "data" / "lessons.json"`
- No user-controlled file paths
- `lessons.json` is read-only in the demo context
- Path is resolved at module load time, not per-request

**Recommendation**: Maintain current practice. No changes needed.

---

### 6. Logging ✅
**Location**: `ai_service.py:logger.warning()`, `app.py:st.error/st.warning/st.success`
**Status**: **Good practice**
- `logger.warning()` used for skipped malformed MCQs/flashcards (no user data)
- `st.error/st.warning/st.success` used for user-facing messages
- No secrets logged
- No stack traces exposed to users

**Recommendation**: Maintain current practice. No changes needed.

---

### Summary
| Category | Severity | Status |
|----------|----------|--------|
| API Key Management | N/A | ✅ Good |
| Error Message Disclosure | Low | ✅ Acceptable |
| HTML Rendering | Low | ✅ Trusted content |
| Input Validation | N/A | ✅ Good |
| File Path Safety | N/A | ✅ Good |
| Logging | N/A | ✅ Good |

**Overall Security Posture**: **Good** - The application does not handle secrets poorly, does not expose user data, and has appropriate input validation for an educational demo app.

**No high or medium severity vulnerabilities found.** All findings are low-risk recommendations for a demo educational application.
MARKDOWNSECURITY