import json

with open("../Nepluro/data/lessons.json", "r", encoding="utf-8") as f:
    lessons = json.load(f)["lessons"]

bio_lessons = [l for l in lessons if l["subject"] == "Biology"]
for b in bio_lessons:
    print(b["id"], b.get("subject"), b.get("title"), b.get("topic"), b.get("track"))
