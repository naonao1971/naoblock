#!/usr/bin/env python3
"""naoblock ⌐◨-◨ 欄（index.html の .art-grid）を Instagram の最新6件に自動で差し替える。

GitHub Actions（.github/workflows/insta-auto.yml）から1日2回動く。手元で試すときはリポジトリのルートで:
  python3 tools/insta_auto.py
トークンは環境変数 IG_TOKEN、なければ ~/.config/naoblock/ig_token から読む（読むだけの権限 instagram_basic）。
最新6件が今の並びと同じなら何もしない（毎回の空コミットを避ける）。
"""
import html
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

IG_USER_ID = "17841422145701631"  # @naoblock.jp
COUNT = 6
SIZE = 480  # index.html の width/height と合わせる
QUALITY = 75
ROOT = Path(__file__).resolve().parent.parent
INSTA_DIR = ROOT / "assets" / "insta"
INDEX = ROOT / "index.html"
GRID = re.compile(r'(<ul class="art-grid">\n).*?(\n\s*</ul>)', re.S)


def token():
    t = os.environ.get("IG_TOKEN", "").strip()
    if not t:
        p = Path.home() / ".config" / "naoblock" / "ig_token"
        t = p.read_text().strip() if p.exists() else ""
    if not t:
        sys.exit("トークンがありません（IG_TOKEN か ~/.config/naoblock/ig_token）")
    return t


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()


def latest():
    q = urllib.parse.urlencode({
        "fields": "media_type,media_url,thumbnail_url,permalink,caption",
        "limit": COUNT,
        "access_token": token(),
    })
    try:
        data = json.loads(get(f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media?{q}"))
    except urllib.error.HTTPError as e:  # 本文にトークンは入らないが、URLは出さない
        sys.exit(f"Instagram API エラー {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")
    items = data.get("data", [])[:COUNT]
    if len(items) < COUNT:
        sys.exit(f"投稿が{COUNT}件取れませんでした（{len(items)}件）")
    return items


def alt_text(caption):
    line = (caption or "").strip().splitlines()[0] if (caption or "").strip() else ""
    line = re.sub(r"#(\S+)", r"\1", line)
    line = re.sub(r"[\U0001F000-\U0001FFFF☀-➿️]", "", line).strip()
    return line[:50] or "naoblock の作品"


def code_of(permalink):
    return permalink.rstrip("/").rsplit("/", 1)[-1]


def save_square(data, dest):
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    img = ImageOps.fit(img, (SIZE, SIZE), Image.LANCZOS, centering=(0.5, 0.5))
    img.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)


def main():
    items = latest()
    src = INDEX.read_text()
    m = GRID.search(src)
    if not m:
        sys.exit('index.html に <ul class="art-grid"> が見つかりません')
    current = re.findall(r'class="art-tile" href="([^"]+)"', m.group(0))
    if current == [it["permalink"] for it in items]:
        print("最新6件は今の並びと同じ。変更なし")
        return

    INSTA_DIR.mkdir(parents=True, exist_ok=True)
    lis = []
    for i, it in enumerate(items, 1):
        img_url = it.get("thumbnail_url") if it["media_type"] == "VIDEO" else it.get("media_url")
        save_square(get(img_url), INSTA_DIR / f"{i:02d}.jpg")
        alt = alt_text(it.get("caption"))
        print(f"{i:02d} {it['permalink']}  {alt}")
        lis.append(
            "          <li>\n"
            f'            <a class="art-tile" href="{html.escape(it["permalink"])}" target="_blank" rel="noopener noreferrer">\n'
            f'              <img src="assets/insta/{i:02d}.jpg?v={code_of(it["permalink"])}" alt="{html.escape(alt)}" width="{SIZE}" height="{SIZE}" loading="lazy" decoding="async" />\n'
            "            </a>\n"
            "          </li>"
        )
    INDEX.write_text(GRID.sub(lambda m: m.group(1) + "\n".join(lis) + m.group(2), src, count=1))
    print("index.html の6枚を書き換えました")


if __name__ == "__main__":
    main()
