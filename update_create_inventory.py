from pathlib import Path

path = Path("../Nepluro/create_inventory.py")
code = path.read_text(encoding="utf-8")
code = code.replace('"Compulsory (all streams)"', '"Compulsory (All streams)"')
path.write_text(code, encoding="utf-8")
print(f"Updated {path}")
