import re
import json

path = "../Nepluro/create_syllabus_structure.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Find occurrences of subjects
matches = re.findall(r'"grade":\s*"([^"]+)",\s*"subject":\s*"([^"]+)"', text)
print("Found subjects:", matches)
