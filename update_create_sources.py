import re
from pathlib import Path

path = Path("../Nepluro/create_sources.py")
code = path.read_text(encoding="utf-8")

# In create_sources.py, each row is formatted like:
# ["CDC_PHYS_11", ..., "https://...", "SOURCE_INSPECTED", "Compulsory..."]
# We want to insert "PUBLIC_ACCESS", before the status
def fix_row(m):
    prefix = m.group(1) # up to url
    status = m.group(2)
    notes = m.group(3)
    return f'{prefix}, "PUBLIC_ACCESS", "{status}", "{notes}"]'

pattern = r'(\["CDC_[^"]+",\s*"[^"]+",\s*"[^"]+",\s*"\d+",\s*"[^"]+",\s*"\d+",\s*"[^"]+",\s*"[^"]+")\s*,\s*"([^"]+)"\s*,\s*"([^"]*)"\]'

fixed_code = re.sub(pattern, fix_row, code)
path.write_text(fixed_code, encoding="utf-8")
print(f"Updated {path}")
