import hashlib
import json
import pathlib
import time
from collections import deque
from datetime import datetime, timezone
from urllib.parse import urljoin, urldefrag

import requests
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "configs/sources.yaml").read_text(encoding="utf-8"))

HEADERS = {"User-Agent": "rag-eval-lab/0.1"}

def ok_url(url: str, prefixes: list[str]) -> bool:
    return any(url.startswith(p) for p in prefixes)

def stable_doc_id(source_id: str, url: str) -> str:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    return f"{source_id}_{h}"

def extract_created_at(soup: BeautifulSoup):
    # 尽量抓公开页面里已有的时间信息；抓不到就留空
    for selector, attr in [
        ('meta[property="article:published_time"]', "content"),
        ('meta[name="last-modified"]', "content"),
        ('time[datetime]', "datetime"),
    ]:
        node = soup.select_one(selector)
        if node and node.get(attr):
            return node.get(attr)
    return None

def extract_main_markdown(html: str):
    soup = BeautifulSoup(html, "lxml")

    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(" ", strip=True)
    elif soup.title:
        title = soup.title.get_text(" ", strip=True)

    main = (
        soup.select_one("main")
        or soup.select_one("article")
        or soup.select_one('[role="main"]')
        or soup.body
    )

    if main is None:
        return title, ""

    text_md = md(str(main), heading_style="ATX")
    return title, text_md

all_meta = []

for src in CFG["sources"]:
    source_id = src["source_id"]
    q = deque(src["seed_urls"])
    seen = set()
    kept = 0

    raw_dir = ROOT / "data/raw/html" / source_id
    md_dir = ROOT / "data/processed/md" / source_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)

    while q and kept < src["max_docs"]:
        url = urldefrag(q.popleft())[0]
        if url in seen:
            continue
        seen.add(url)

        if not ok_url(url, src["allow_prefixes"]):
            continue

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
        except Exception:
            continue

        if "text/html" not in r.headers.get("content-type", ""):
            continue

        soup = BeautifulSoup(r.text, "lxml")
        title, text_md = extract_main_markdown(r.text)
        if not text_md.strip():
            continue

        doc_id = stable_doc_id(source_id, url)

        (raw_dir / f"{doc_id}.html").write_text(r.text, encoding="utf-8")
        (md_dir / f"{doc_id}.md").write_text(text_md, encoding="utf-8")

        meta = {
            "doc_id": doc_id,
            "source": source_id,
            "source_url": url,
            "title": title or doc_id,
            "section": "root",
            "created_at": extract_created_at(soup),
            "topic": src["topic"],
            "language": src["language"],
            "doc_type": "documentation",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "local_path": str((md_dir / f"{doc_id}.md").relative_to(ROOT)),
        }
        all_meta.append(meta)
        kept += 1

        for a in soup.select("a[href]"):
            nxt = urldefrag(urljoin(url, a["href"]))[0]
            if ok_url(nxt, src["allow_prefixes"]) and nxt not in seen:
                q.append(nxt)

        time.sleep(0.5)

out_path = ROOT / "metadata/documents.jsonl"
out_path.write_text(
    "\n".join(json.dumps(x, ensure_ascii=False) for x in all_meta),
    encoding="utf-8",
)

print(f"saved {len(all_meta)} docs -> {out_path}")
