import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
md_root = ROOT / "data/processed/md"
rows = []

for md_file in md_root.rglob("*.md"):
    doc_id = md_file.stem
    lines = md_file.read_text(encoding="utf-8").splitlines()
    headings = []
    for i, line in enumerate(lines, start=1):
        m = re.match(r"^(#{1,6})\s+(.*)", line.strip())
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            headings.append({"line_no": i, "level": level, "text": text})
    rows.append({"doc_id": doc_id, "headings": headings})

out = ROOT / "metadata/headings.jsonl"
out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
print(f"saved -> {out}")
