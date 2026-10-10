"""Final verification of all changes - results written to file."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from content import load_lessons, filter_lessons, search_lessons, _normalize_text, lesson_label

lessons = load_lessons()
results = []

results.append(f"Lessons: {len(lessons)} total")

en = sum(1 for l in lessons if l['language'] == 'en')
ne = sum(1 for l in lessons if l['language'] == 'ne')
results.append(f"English: {en}, Nepali: {ne}")
assert en == 9, f"Expected 9 English, got {en}"
assert ne == 5, f"Expected 5 Nepali, got {ne}"

# Test filters
ne_lessons = filter_lessons(lessons, language='ne')
results.append(f"Nepali filter: {len(ne_lessons)} (expected 5)")
assert len(ne_lessons) == 5, f"Expected 5 Nepali lessons filtered, got {len(ne_lessons)}"

en_lessons = filter_lessons(lessons, language='en')
results.append(f"English filter: {len(en_lessons)} (expected 9)")
assert len(en_lessons) == 9, f"Expected 9 English lessons filtered, got {len(en_lessons)}"

# Test normalize
norm = _normalize_text('  Photosynthesis  ')
results.append(f'Normalize: "{norm}" (expected "photosynthesis")')
assert norm == "photosynthesis", f"Expected 'photosynthesis', got {norm}"

# Test labels - write to file to avoid Unicode encode issues
with open("verify_results.txt", "w", encoding="utf-8") as f:
    f.write("lesson_label checks:\n")
    
    r_en = lesson_label("en")
    results.append(f"lesson_label(en): {r_en}")
    f.write(f"  en: {r_en}\n")
    assert r_en == "English", f"Expected 'English', got {r_en}"
    
    r_ne = lesson_label("ne")
    results.append(f"lesson_label(ne): {r_ne}")
    f.write(f"  ne: {r_ne}\n")
    assert r_ne == "नेपाली (Nepali)", f"Expected 'नेपाली (Nepali)', got {r_ne}"
    
    r_xx = lesson_label("xx")
    results.append(f"lesson_label(xx): {r_xx}")
    f.write(f"  xx: {r_xx}\n")
    assert r_xx == "xx", f"Expected 'xx' for unknown, got {r_xx}"

# Test search
en_lessons_only = [l for l in lessons if l["language"] == "en"]
results.append("")

results.append("Search tests:")
results.append(f"  search('photosynthesis'): {len(search_lessons(en_lessons_only, 'photosynthesis'))} (expected >= 1)")
assert len(search_lessons(en_lessons_only, "photosynthesis")) >= 1

results.append(f"  search('  whitespace  '): {len(search_lessons(en_lessons_only, '  whitespace  '))} (expected >= 1)")
assert len(search_lessons(en_lessons_only, "  whitespace  ")) >= 1

results.append(f"  search(''): {len(search_lessons(en_lessons_only, ''))} (expected 0)")
assert len(search_lessons(en_lessons_only, "")) == 0

results.append(f"  search('   '): {len(search_lessons(en_lessons_only, '   '))} (expected 0)")
assert len(search_lessons(en_lessons_only, "   ")) == 0

# Test combined filter
combined = filter_lessons(lessons, track="NEB Grade 11", language="ne")
results.append("")
results.append(f"Combined filter (NEB Grade 11 + ne): {len(combined)} lessons")
assert isinstance(combined, list)

# Test unique IDs
ids = [l["id"] for l in lessons]
results.append("")
results.append(f"Unique IDs: {len(ids)} / {len(set(ids))}")
assert len(ids) == len(set(ids)), "Duplicate lesson IDs found"

# Test all lessons have required fields
REQUIRED = ("id", "track", "subject", "topic", "title", "language", "content")
for i, l in enumerate(lessons):
    for field in REQUIRED:
        assert field in l, f"Lesson {i} missing field '{field}'"
        assert l[field], f"Lesson {i} field '{field}' is empty"
results.append("")
results.append("All lessons have required fields: OK")

# Write summary
with open("verify_results.txt", "w", encoding="utf-8") as f:
    for line in results:
        f.write(line + "\n")

print("Verification complete - results written to verify_results.txt")