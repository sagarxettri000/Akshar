import json
from pathlib import Path

with Path('data/lessons.json').open(encoding='utf-8') as f:
    data = json.load(f)

print(f'Version: {data.get("version")}')
lessons = data.get('lessons', [])
print(f'Total lessons: {len(lessons)}')
with open('lesson_inventory.txt', 'w', encoding='utf-8') as f:
    f.write(f'Version: {data.get("version")}\n')
    f.write(f'Total lessons: {len(lessons)}\n')
    for i, l in enumerate(lessons):
        f.write(f'Lesson {i}:\n')
        for k, v in l.items():
            f.write(f'  {k}: {str(v)[:80] if v else None}\n')
        f.write('\n')
print('Written to lesson_inventory.txt')