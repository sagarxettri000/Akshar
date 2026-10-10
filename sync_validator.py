from pathlib import Path

src = Path("validate_inventory.py").read_text(encoding="utf-8")
dst = Path("../Nepluro/validate_inventory.py")
dst.write_text(src, encoding="utf-8")
print(f"Copied validate_inventory.py to {dst} ({len(src)} bytes)")
