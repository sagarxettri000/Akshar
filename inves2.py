"""Investigate Nepali search functionality."""
from pathlib import Path
import json
from content import _normalize_text, search_lessons, filter_lessons

data = Path("data/lessons.json")
lessons = json.loads(data.read_text(encoding="utf-8"))["lessons"]

ne_lessons = [l for l in lessons if l["language"] == "ne"]
en_lessons = [l for l in lessons if l["language"] == "en"]

# Write investigation results
with open("inves2_output.txt", "w", encoding="utf-8") as f:
    write = f.write

    a = "=== Nepali Content Normalization Investigation ===\n"
    write(a)

    # Get first Nepali lesson content
    a_content = ne_lessons[0]["content"]
    a_norm = _normalize_text(a_content)
    write("=== First Nepali lesson content ===\n")
    write("Original length: %d\n" % len(a_content))
    write("Normalized length: %d\n" % len(a_norm))
    write("First 200 chars original: %s\n" % repr(a_content[:200]))
    write("First 200 chars normalized: %s\n" % repr(a_norm[:200]))

    # Test various search terms
    test_terms = [
        ("किन्र्त", "kinematics-like"),
        ("गति", "motion"),
        ("भौतिक", "physics"),
        ("वेग", "velocity"),
        ("गुरुत्व", "gravity"),
        ("फलां", "generic Nepali"),
    ]

    a("\n=== Search term tests ===\n")
    for term, label in test_terms:
        norm_term = _normalize_text(term)
        a("Term: %s (label: %s)" % (repr(term), label))
        a("  Normalized: %s" % repr(norm_term))
        # Check if term appears in normalized content
        a("  In content: %s" % ("YES" if norm_term in a_norm else "NO"))
        # Search using search_lessons
        r = search_lessons(ne_lessons, term)
        a("  search_lessons results: %d" % len(r))
        a("")

    a("=== filter_lessons tests ===\n")
    a("  filter language=en: %d" % len(filter_lessons(lessons, language="en")))
    a("  filter language=ne: %d" % len(filter_lessons(lessons, language="ne")))

    a("\n=== English lesson search ===\n")
    a("  search 'photosynthesis': %d" % len(search_lessons(en_lessons, "photosynthesis")))
    a("  search 'Photosynthesis': %d" % len(search_lessons(en_lessons, "Photosynthesis")))
    a("  search '  photosynthesis  ': %d" % len(search_lessons(en_lessons, "  photosynthesis  ")))

    a("\n=== All investigation complete ===\n")