"""Investigate Nepali lesson content."""
from pathlib import Path
import json
from content import _normalize_text

data = Path("data/lessons.json")
lessons = json.loads(data.read_text(encoding="utf-8"))["lessons"]

ne_lessons = [l for l in lessons if l["language"] == "ne"]

# Write investigation results to file
out = Path("investigate_output.txt")
with out.open("w", encoding="utf-8") as fp:

    def write_line(s):
        fp.write(s + "\n")

    write_line("Nepali lesson content info:")
    for i, l in enumerate(ne_lessons[:1]):
        a = l["content"]
        a_len = len(a) if a else 0
        a_idx = 0
        write_line("  first 50 chars:")
        for ch in a or "":
            a_idx += 1
            if a_idx <= 50:
                write_line("  U+%04X = %s" % (ord(ch), repr(ch)))
        a_idx = 0
        write_line("  last 50 chars:")
        for ch in a[max(0, a_len-50):]:
            a_idx += 1
            write_line("  char from end %d: U+%04X = %s" % (a_idx, ord(ch), repr(ch)))
        write_line("  total length: %d" % a_len)

    # Test normalize on Nepali text
    write_line("")
    write_line("Test _normalize_text on Nepali content:")
    a = ne_lessons[0]["content"]
    if a:
        norm = _normalize_text(a)
        a_idx = 0
        write_line("Normalized content first 100 chars:")
        for ch in norm[:100]:
            a_idx += 1
            write_line("  U+%04X" % ord(ch))
        write_line("Normalized content repr (first 100): %s" % repr(norm[:100]))

        # Test search with normalized content
        q = _normalize_text("\u092e\u0930\u093e\u0932")  # "फलां"
        write_line("\nNormalized query 'फलां': %s" % repr(q))
        write_line("Query in normalized content: %s" % ("YES" if q in norm else "NO"))

        # Check Devanagari range content
        dev_count = sum(1 for ch in a if '\u0900' <= ch <= '\u097F')
        write_line("Devanagari chars in content: %d" % dev_count)

        # Try searching with actual content words
        a_idx = 0
        write_line("\nFirst 3 chars of content:")
        for ch in a[:3]:
            a_idx += 1
            write_line("  char %d: U+%04X" % (a_idx, ord(ch)))

    # Second lesson
    write_line("\n\nSecond Nepali lesson first 50 chars:")
    a = ne_lessons[1]["content"] if len(ne_lessons) > 1 else ""
    if a:
        a_idx = 0
        for ch in a[:50]:
            a_idx += 1
            write_line("  U+%04X" % ord(ch))

    write_line("\n\nDone.")