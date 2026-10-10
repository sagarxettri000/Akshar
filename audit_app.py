"""Audit app.py language handling."""

with open("C:\\Users\\dipso\\OneDrive\\Desktop\\Hackathon\\Nepluro\\app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find ASK_LANGUAGE_OPTIONS and related language handling
print("=== ASK_LANGUAGE_OPTIONS ===")
match = re.search(r"ASK_LANGUAGE_OPTIONS\s*=\s*\{(.*?)\}", content, re.DOTALL)
if match:
    print(match.group(0))

print("\n=== require_api_key function ===")
start = content.find("def require_api_key")
if start >= 0:
    end = content.find("\n\ndef ", start + 1)
    if end < 0:
        end = len(content)
    print(content[start:end])

print("\n=== ASK tab language selector ===")
# Find the st.selectbox for answer language in render_ask_tab
import re
# Look for the language selectbox in the ask tab
match = re.search(r"language_label\s*=\s*st\.selectbox.*?key=f\"ask-lang", content, re.DOTALL)
if match:
    print(match.group(0))

print("\n=== render_ai_notice ===")
match = re.search(r"def render_ai_notice\(\$\](.*?)(?=\n\ndef|\Z)", content, re.DOTALL)
if match:
    print(match.group(0))

print("\n=== Tab labels ===")
# Find tab titles
for label in ["📝 Explain", "💬 Ask", "🎯 Practise", "🧠 Flashcards"]:
    if f'["{label}"' in content or f'["{label}"]' in content:
        print(f"  Found tab: {label}")

print("\n=== Language labels in UI ===")
# Check for "Auto (match lesson)" etc.
for label in ["Auto (match lesson)", "English", "Nepali", "नेपाली"]:
    if label in content:
        # Find context
        idx = content.find(label)
        context = content[max(0, idx-50):idx+50]
        print(f"  Found '{label}': {context}")