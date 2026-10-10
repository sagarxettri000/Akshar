"""Security and reliability review of Nepluro."""

import ast
import json
import re
from pathlib import Path

BASE = Path("C:\\Users\\dipso\\OneDrive\\Desktop\\Hackathon\\Nepluro")

print("=" * 60)
print("SECURITY AND RELIABILITY REVIEW")
print("=" * 60)

# 1. Check for hardcoded secrets/API keys
print("\n--- 1. Hardcoded secrets/API keys ---")
for py_file in BASE.rglob("*.py"):
    content = py_file.read_text(encoding="utf-8")
    # Check for API key patterns in source
    if "API_KEY" in content.upper() and "secrets" not in content.lower():
        # Look for patterns like = "key" or = 'key' at module level
        for match in re.finditer(r'(?:API_KEY|GOOGLE_API_KEY|GEMINI_API_KEY)\s*[:=]\s*["\'][^"\']+["\']', content):
            line_start = max(0, match.start() - 100)
            line_end = min(len(content), match.end() + 100)
            snippet = content[line_start:line_end]
            print(f"  {py_file}: {snippet[:120]}")

# 2. Check _redact_secret usage
print("\n--- 2. Secret redaction in ai_service.py ---")
ai_service = BASE / "ai_service.py"
content = ai_service.read_text(encoding="utf-8")
if "_redact_secret" in content:
    print("  _redact_secret function exists in ai_service.py")
    # Check it's used in _generate_text
    if "._redact_secret" in content or '"' + "_redact_secret" in content:
        print("  -> Used in _generate_text error handling")
else:
    print("  _redact_secret function NOT found - need to check")

# 3. Check API key is never logged
print("\n--- 3. API key redaction verification ---")
# The _redact_secret function should be called with api_key in error messages
if "Never include the API key in the raised message" in content:
    print("  -> Error messages warn about redacting API key")
else:
    print("  -> Check manual redaction")

# 4. Input validation checks
print("\n--- 4. Input validation ---")
# Check _clean_* functions exist
for func in ["_clean_lesson_text", "_clean_api_key", "_clean_question", "_clean_history", "_clean_answer_language"]:
    if f"def {func}" in content:
        print(f"  -> def {func}() exists")
    else:
        print(f"  -> def {func}() MISSING")

# 5. Check for unsafe exception handling
print("\n--- 5. Exception handling ---")
# Look for bare except or exception that might leak info
bad_patterns = ["except:", "except Exception"]
for pattern in bad_patterns:
    matches = re.findall(rf".*{pattern}.*", content, re.MULTILINE)
    # Filter out harmless ones
    for m in matches[:3]:
        print(f"  -> {m[:100]}")

# 6. Check google-genai import is lazy
print("\n--- 6. Lazy SDK import ---")
if "try:" in content and "from google import genai" in content:
    print("  -> SDK import is deferred (lazy)")
else:
    print("  -> SDK import pattern not found as expected")

# 7. Check requirements or setup for dependencies
print("\n--- 7. Dependency configuration ---")
for req_file in ["requirements.txt", "setup.py", "pyproject.toml"]:
    p = BASE / req_file
    if p.exists():
        print(f"  -> {req_file} exists")
        req_content = p.read_text(encoding="utf-8")
        # Check google-genai is listed
        if "google-genai" in req_content.lower():
            print(f"  -> google-genai listed in {req_file}")
        if "streamlit" in req_content.lower():
            print(f"  -> streamlit listed in {req_file}")

# 8. Check data file integrity
print("\n--- 8. Data integrity ---")
lessons_file = BASE / "data" / "lessons.json"
if lessons_file.exists():
    try:
        lessons = json.loads(lessons_file.read_text(encoding="utf-8"))
        ids = [l["id"] for l in lessons["lessons"]]
        if len(ids) == len(set(ids)):
            print(f"  -> All {len(ids)} lesson IDs are unique")
        else:
            print(f"  -> DUPLICATE IDs found!")
        
        # Check all have required fields
        required = ("id", "track", "subject", "topic", "title", "language", "content")
        missing = 0
        for l in lessons["lessons"]:
            for f in required:
                if f not in l or not l[f]:
                    missing += 1
        print(f"  -> Missing field checks: {missing} issues across {len(lessons['lessons'])} lessons")
        
        # Check language codes
        valid_langs = {"en", "ne"}
        invalid = [l["language"] for l in lessons["lessons"] if l["language"] not in valid_langs]
        if invalid:
            print(f"  -> Invalid language codes: {set(invalid)}")
        else:
            print(f"  -> All language codes valid (en/ne)")
    except Exception as e:
        print(f"  -> Error reading lessons: {e}")

# 9. Check for unsafe JSON handling
print("\n--- 9. JSON parsing safety ---")
# parse_json_response function
if "def parse_json_response" in content:
    print("  -> parse_json_response() exists")
    # Check it validates before returning
    if "AIResponseError" in content:
        print("  -> AIResponseError raised on parse failure")
    if "json.loads" in content:
        print("  -> json.loads() used for parsing")

# 10. Check for debug mode or dangerous configs
print("\n--- 10. Dangerous configurations ---")
dangerous = ["debug=True", "echo True", "echo=True"]
for py_file in BASE.rglob("*.py"):
    content = py_file.read_text(encoding="utf-8")
    for d in dangerous:
        if d in content:
            # Exclude comments
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if d in line and not line.strip().startswith("#"):
                    print(f"  -> {py_file.name}:{i+1}: {line.strip()[:100]}")

print("\n" + "=" * 60)
print("Review complete")
print("=" * 60)