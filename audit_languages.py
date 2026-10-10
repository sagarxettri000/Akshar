"""Audit English/Nepali language consistency in lessons."""

import json
from pathlib import Path

lessons_data = Path(__file__).parent / "data" / "lessons.json"
lessons = json.loads(lessons_data.read_text(encoding="utf-8"))

# Count by language
lang_counts = {}
for lesson in lessons["lessons"]:
    lang = lesson["language"]
    lang_counts[lang] = lang_counts.get(lang, 0) + 1

print("Language distribution:")
for lang, count in sorted(lang_counts.items()):
    print(f"  {lang}: {count}")

# Check for lessons missing language or with empty language
print()
print("Lessons with missing/empty language:")
for lesson in lessons["lessons"]:
    lang = lesson.get("language", "")
    if not lang or lang.strip() == "":
        print(f"  id={lesson['id']}, keys: {list(lesson.keys())}")

# Check track distribution per language
print()
print("Lessons per track and language:")
tracks = {}
for lesson in lessons["lessons"]:
    track = lesson["track"]
    lang = lesson["language"]
    if track not in tracks:
        tracks[track] = {}
    tracks[track][lang] = tracks[track].get(lang, 0) + 1

for track, langs in sorted(tracks.items()):
    print(f"  {track}: {langs}")

# Check subject distribution per language
print()
print("Lessons per subject and language:")
subjects = {}
for lesson in lessons["lessons"]:
    subject = lesson["subject"]
    lang = lesson["language"]
    if subject not in subjects:
        subjects[subject] = {}
    subjects[subject][lang] = subjects[subject].get(lang, 0) + 1

for subject, langs in sorted(subjects.items()):
    print(f"  {subject}: {langs}")

# Check for any Nepali content mojibake or encoding issues
print()
print("Checking Nepali content encoding...")
for lesson in lessons["lessons"]:
    if lesson["language"] == "ne":
        content = lesson["content"]
        # Check if we can encode/decode round-trip
        try:
            encoded = content.encode("utf-8")
            decoded = encoded.decode("utf-8")
            if content != decoded:
                print(f"  ENCODE/DECODE MISMATCH for id={lesson['id']}")
        except Exception as e:
            print(f"  ENCODING ERROR for id={lesson['id']}: {e}")

# Verify all lessons have the required fields with non-empty values
print()
print("Verifying required fields...")
REQUIRED = ("id", "track", "subject", "topic", "title", "language", "content")
missing_or_empty = []
for i, lesson in enumerate(lessons["lessons"]):
    for field in REQUIRED:
        value = lesson.get(field, "")
        if not isinstance(value, str) or not value.strip():
            missing_or_empty.append((lesson["id"], field, value))

if missing_or_empty:
    print(f"  Found {len(missing_or_empty)} lessons with missing/empty fields:")
    for mid, field, value in missing_or_empty[:20]:
        print(f"    id={mid}, field={field}, value={value!r}")
else:
    print("  All lessons have all required fields with non-empty values")

# Check for duplicate IDs
print()
ids = [lesson["id"] for lesson in lessons["lessons"]]
if len(ids) != len(set(ids)):
    print(f"  DUPLICATE IDs found! Total: {len(ids)}, Unique: {len(set(ids))}")
else:
    print(f"  All {len(ids)} lesson IDs are unique")

# Check language codes are valid
print()
valid_languages = {"en", "ne"}
invalid_langs = set()
for lesson in lessons["lessons"]:
    if lesson["language"] not in valid_languages:
        invalid_langs.add(lesson["language"])

if invalid_langs:
    print(f"  Invalid language codes found: {invalid_langs}")
else:
    print("  All language codes are valid (en or ne)")