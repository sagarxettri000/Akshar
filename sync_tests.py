from pathlib import Path

src = Path("tests/test_validate_inventory.py").read_text(encoding="utf-8")
dst = Path("../Nepluro/tests/test_validate_inventory.py")
dst.write_text(src, encoding="utf-8")
print(f"Copied test_validate_inventory.py to {dst}")
