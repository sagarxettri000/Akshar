import sys
sys.stdout.reconfigure(encoding="utf-8")

with open("../Nepluro/create_syllabus_structure.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines[205:255], start=206):
    print(f"{idx}: {line.rstrip()}")
