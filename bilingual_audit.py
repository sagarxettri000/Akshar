"""Bilingual audit for Nepluro."""
from pathlib import Path
import json
from content import _normalize_text, lesson_label, filter_lessons, search_lessons

data = Path("data/lessons.json")
lessons = json.loads(data.read_text(encoding="utf-8"))["lessons"]

results = []

def a(s):
    results.append(s)

a("_normalize_text tests:")
a(_normalize_text("  Photosynthesis  "))
a(_normalize_text("HELLO   WORLD"))
a(_normalize_text("\u0928\u092e\u0938\u094d\u0924\u0947\u0926\u0941\u0928\u093f\u092f\u093e"))
a(_normalize_text(""))

a("")
a(lesson_label("en"))
a(lesson_label("ne"))
a(lesson_label("xx"))

a("")
en_l = [l for l in lessons if l["language"] == "en"]
ne_l = [l for l in lessons if l["language"] == "ne"]
a("English count: " + str(len(en_l)))
a("Nepali count: " + str(len(ne_l)))

fn = filter_lessons(lessons, language="ne")
a("filter language=ne: " + str(len(fn)))
fn = filter_lessons(lessons, language="en")
a("filter language=en: " + str(len(fn)))

a("")
r = search_lessons(en_l, "photosynthesis")
a("English search photosynthesis: " + str(len(r)))
r = search_lessons(en_l, "  photosynthesis  ")
a("English search whitespace: " + str(len(r)))
r = search_lessons(en_l, "Photosynthesis")
a("search case match: " + str(len(r)))

# Try Nepali search - use a common Nepali word
r = search_lessons(ne_l, "\u092e\u0930\u093e\u0932")  # "फलां" in Devanagari
a("Nepali search: " + str(len(r)))

a("")
r = search_lessons(lessons, "")
a("empty search: " + str(len(r)))

a("")
r = search_lessons(lessons, "   ")
a("whitespace search: " + str(len(r)))

# Write results to file
out = Path("audit_results.txt")
out.write_text("\n".join(results), encoding="utf-8")
print("Results written to audit_results.txt")