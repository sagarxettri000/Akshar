"""Audit bilingual behavior of Nepluro lessons."""
import json
import sys
from pathlib import Path
from content import load_lessons, filter_lessons, search_lessons, _normalize_text, lesson_label

# Redirect output to file to avoid UnicodeEncodeError in print
with open("bilingual_audit.txt", "w", encoding="utf-8") as out:
    def msg(text):
        out.write(text + "\n")

    msg("=== Language Distribution ===")
    data = Path(__file__).parent / "data" / "lessons.json"
    lessons = json.loads(data.read_text(encoding="utf-8"))["lessons"]

    lang_counts = {}
    for l in lessons:
        lang = l["language"]
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    for lang, count in sorted(lang_counts.items()):
        msg(f"  {lang}: {count}")

    msg("\n=== All Lessons Summary ===")
    REQUIRED = ("id", "track", "subject", "topic", "title", "language", "content")
    for i, l in enumerate(lessons):
        missing = [f for f in REQUIRED if f not in l or not l[f]]
        extra = [f for f in l if f not in REQUIRED]
        lid = l.get("id", "unknown")
        msg(f"Lesson {i}: {lid}")
        msg(f"  lang={l['language']} | track={l['track']} | sub={l['subject']} | topic={l['topic']} | title={l['title']}")
        if missing:
            msg(f"  MISSING: {missing}")
        if extra:
            msg(f"  EXTRA: {extra}")

    msg("\n=== _normalize_text Tests ===")
    test_cases = [
        ("  Photosynthesis  ", "photosynthesis"),
        ("HELLO   WORLD", "hello world"),
        ("नमस्ते  दुनिया", "नमस्ते दुनिया"),
        ("", ""),
    ]
    for raw, expected in test_cases:
        result = _normalize_text(raw)
        status = "OK" if result == expected else "FAIL"
        msg(f"  {status}: _normalize_text({raw!r}) = {result!r} (expected {expected!r})")

    msg("\n=== lesson_label Tests ===")
    for code, expected in [("en", "English"), ("ne", "नेपाली (Nepali)"), ("xx", "xx")]:
        result = lesson_label(code)
        status = "OK" if result == expected else "FAIL"
        msg(f"  {status}: lesson_label({code!r}) = {result!r} (expected {expected!r})")

    msg("\n=== filter_lessons language filter ===")
    en_lessons = [l for l in lessons if l["language"] == "en"]
    ne_lessons = [l for l in lessons if l["language"] == "ne"]
    msg(f"English lessons: {len(en_lessons)}")
    msg(f"Nepali lessons: {len(ne_lessons)}")

    # Filter by language
    filtered_ne = filter_lessons(lessons, language="ne")
    msg(f"filter_lessons(language='ne'): {len(filtered_ne)} lessons")
    for l in filtered_ne:
        lid = l.get("id", "unknown")
        msg(f"  {lid}: {l['subject']} - {l['topic']}")

    filtered_en = filter_lessons(lessons, language="en")
    msg(f"filter_lessons(language='en'): {len(filtered_en)} lessons")
    for l in filtered_en:
        lid = l.get("id", "unknown")
        msg(f"  {lid}: {l['subject']} - {l['topic']}")

    # Filter combined
    filtered_both = filter_lessons(lessons, track="NEB Grade 11", language="ne")
    msg(f"filter_lessons(track='NEB Grade 11', language='ne'): {len(filtered_both)} lessons")
    for l in filtered_both:
        lid = l.get("id", "unknown")
        msg(f"  {lid}: {l['subject']} - {l['topic']}")

    msg("\n=== search_lessons tests ===")
    # Search in English lessons
    results = search_lessons(en_lessons, "photosynthesis")
    msg(f"search_lessons(English lessons, 'photosynthesis'): {len(results)} results")
    for r in results:
        lid = r.get("id", "unknown")
        msg(f"  {lid}: {r['topic']}")

    results = search_lessons(en_lessons, "  photosynthesis  ")
    msg(f"search_lessons(English lessons, '  whitespace  '): {len(results)} results")

    results = search_lessons(en_lessons, "Photosynthesis")
    msg(f"search_lessons(English lessons, 'Photosynthesis' case-match): {len(results)} results")

    # Search in Nepali lessons
    msg("\n=== Nepali content samples ===")
    for l in ne_lessons[:2]:
        content = l["content"][:100] if l["content"] else ""
        lid = l.get("id", "unknown")
        msg(f"  {lid}: {content!r}")

    msg("\n=== search_lessons with Nepali query ===")
    # Try searching with Nepali content terms
    results = search_lessons(ne_lessons, "फलां")
    msg(f"search_lessons(Nepali lessons, 'फलां'): {len(results)} results")
    for r in results:
        lid = r.get("id", "unknown")
        msg(f"  {lid}: {r['topic']}")

    msg("\n=== Empty search test ===")
    results = search_lessons(lessons, "")
    msg(f"search_lessons(lessons, ''): {len(results)} results (should be 0)")

    results = search_lessons(lessons, "   ")
    msg(f"search_lessons(lessons, '   '): {len(results)} results (should be 0)")

    msg("\n=== ALL TESTS COMPLETE ===")

# Run the main logic outside the with block for pytest compatibility
msg = print  # restore print