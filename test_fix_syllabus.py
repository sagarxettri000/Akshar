import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

with open("../Nepluro/create_syllabus_structure.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the parentheses outside quotes in lines 213-242
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

try:
    data = json.loads(content)
    print("SUCCESS! Loaded JSON with", len(data), "subjects.")
    for item in data:
        print(f"Grade {item['grade']} {item['subject']} ({item['subject_code']})")
except Exception as e:
    print("JSON Parse error:", e)
