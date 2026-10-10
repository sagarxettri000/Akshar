import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("../Nepluro/create_syllabus_structure.py", "r", encoding="utf-8") as f:
    content = f.read()

fixes = [
    ('"विकास र राष्ट्रवाद" (Development and Nationalism)', '"विकास र राष्ट्रवाद (Development and Nationalism)"'),
    ('"साहित्य प्रसार" (Literature dissemination)', '"साहित्य प्रसार (Literature dissemination)"'),
    ('" भाषा कौशल विकास" (Language skill development)', '"भाषा कौशल विकास (Language skill development)"'),
    ('" नेपाली भाषाको ज्ञान" (Knowledge of Nepali language)', '"नेपाली भाषाको ज्ञान (Knowledge of Nepali language)"'),
    ('" नेपाली भाषाको इतिहास र विकास" (History and development of Nepali language)', '"नेपाली भाषाको इतिहास र विकास (History and development of Nepali language)"'),
    ('" कविता र उपन्यास" (Poetry and Novel)', '"कविता र उपन्यास (Poetry and Novel)"'),
    ('" भाषाको उत्थान" (Language development)', '"भाषाको उत्थान (Language development)"'),
    ('" राष्ट्रीय एकता" (National unity)', '"राष्ट्रिय एकता (National unity)"'),
    ('" नेपाリग文学को इतिहास" (History of Nepali literature)', '"नेपाली साहित्यको इतिहास (History of Nepali literature)"'),
]

for old, new in fixes:
    content = content.replace(old, new)

data = json.loads(content)
for i, item in enumerate(data):
    s = item["syllabus_structure"]
    print(f"Subject {i+1}: Grade {item['grade']} {item['subject']} ({item['subject_code']})")
    print(f"  Objectives: {len(s.get('curriculum_objectives', []))}")
    print(f"  Units: {len(s.get('units', []))}")
    for u in s.get("units", []):
        print(f"    - Unit {u.get('unit_number')}: {u.get('unit_title')}")
    print(f"  Topics: {len(s.get('topics_and_subtopics', []))}")
    print(f"  Learning Outcomes: {len(s.get('learning_outcomes', []))}")
    print(f"  Assessment: {s.get('assessment_components', {})}")
