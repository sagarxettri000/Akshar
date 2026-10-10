"""Search test for bilingual Nepluro lessons."""
from pathlib import Path
import json
from content import _normalize_text, search_lessons, lesson_label, filter_lessons

data = Path("data/lessons.json")
lessons = json.loads(data.read_text(encoding="utf-8"))["lessons"]

ne_lessons = [l for l in lessons if l["language"] == "ne"]
en_lessons = [l for l in lessons if l["language"] == "en"]

# Write results to file
out_file = open("search_results.txt", "w", encoding="utf-8")

def a(s):
    out_file.write(s + "\n")

a("=== Nepali lesson search tests ===")
a("")

a("Test 1: Search English lessons for 'motion':")
r = search_lessons(en_lessons, "motion")
a("  Results: %d" % len(r))

a("")
a("Test 2: Search Nepali lessons for 'गति' (motion):")
r = search_lessons(ne_lessons, "\u0917\u0924\u093f\u0932\u093e")
a("  Results: %d" % len(r))
for result in r:
    a("  Lesson: %s - %s" % (result["id"], result["topic"]))

a("")
a("Test 3: Search Nepali lessons for shorter 'गति':")
r = search_lessons(ne_lessons, "\u0917\u0924\u093f")
a("  Results: %d" % len(r))

a("")
a("Test 4: _normalize_text on Nepali:")
a_content = ne_lessons[0]["content"]
Nepali_word = "\u0917\u0924\u093f\u0932\u093e"
normalized = _normalize_text(Nepali_word)
a("  Original: %s" % repr(Nepali_word))
a("  Normalized: %s" % repr(normalized))

a("")
a("Test 5: Search for 'भौतिक' (physics in Nepali):")
r = search_lessons(ne_lessons, "\u092d\u093e\u0924\u093f\u0915\u093e\u0928\u094d")
a("  Results: %d" % len(r))

a("")
a("Test 7: Search for 'गुरुत्व' (gravity):")
r = search_lessons(ne_lessons, "\u0915\u0931\u093f\u0928\u094d")
a("  Results: %d" % len(r))

a("")
a("Test 7: Search for 'वेग' (velocity):")
r = search_lessons(ne_lessons, "\u0935\u094d\u0926\u0940")
a("  Results: %d" % len(r))

a("")
a("Test 8: Empty search:")
r = search_lessons(lessons, "")
a("  Results: %d (should be 0)" % len(r))

a("")
a("Test 9: Whitespace search:")
r = search_lessons(lessons, "   ")
a("  Results: %d (should be 0)" % len(r))

a("")
a("Test 10: English search 'photosynthesis':")
r = search_lessons(en_lessons, "photosynthesis")
a("  Results: %d" % len(r))

a("")
a("Test 11: Search case-insensitive:")
r = search_lessons(en_lessons, "Photosynthesis")
a("  Results: %d" % len(r))

a("")
a("Test 12: Search whitespace-tolerant:")
r = search_lessons(en_lessons, "  photosynthesis  ")
a("  Results: %d" % len(r))

a("")
a("Test 13: lesson_label:")
a("  en: %s" % lesson_label("en"))
a("  ne: %s" % lesson_label("ne"))
a("  xx: %s" % lesson_label("xx"))

a("")
a("Test 14: filter_lessons language:")
a("  English count: %d" % len([l for l in lessons if l["language"] == "en"]))
a("  Nepali count: %d" % len([l for l in lessons if l["language"] == "ne"]))
a("  filter language=en: %d" % len(filter_lessons(lessons, language="en")))
a("  filter language=ne: %d" % len(filter_lessons(lessons, language="ne")))

a("=== All search tests complete ===")
out_file.close()

print("Search test results written to search_results.txt")