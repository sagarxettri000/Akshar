import re

with open("../Nepluro/create_sources.py", "r", encoding="utf-8") as f:
    code = f.read()

# Extract rows = [...]
match = re.search(r'rows = \[\s*(.*?)\s*\]\s*# Write CSV', code, re.DOTALL)
if match:
    rows_str = match.group(1)
    # evaluate in safe dict
    rows = eval(f"[{rows_str}]")
    print(f"Extracted {len(rows)} rows from create_sources.py")
    for i, r in enumerate(rows[:5]):
        print(f"Row {i} (len {len(r)}): {r}")
