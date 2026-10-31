#!/usr/bin/env python3
"""naoblock ⌐◨-◨ 欄（index.html の .art-grid）を Instagram の最新6件に自動で差し替える。

GitHub Actions（.github/workflows/insta-auto.yml）から1日2回動く。手元で試すときはリポジトリのルートで:
  python3 tools/insta_auto.py
トークンは環境変数 IG_TOKEN、なければ ~/.config/naoblock/ig_token から読む（読むだけの権限 instagram_basic）。
投稿の並びも写真（リールのカバー差し替えなど）も変わっていなければ何もしない（毎回の空コミットを避ける）。
"""
import hashlib
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


def square(data):
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    return ImageOps.fit(img, (SIZE, SIZE), Image.LANCZOS, centering=(0.5, 0.5))


def same_picture(a, b):
    """縮小して見比べる。JPEG の保存し直しやPillowの版の違いでは「変わった」にしない"""
    a, b = (ImageOps.grayscale(x).resize((32, 32), Image.BILINEAR) for x in (a, b))
    diff = sum(abs(x - y) for x, y in zip(a.getdata(), b.getdata())) / (32 * 32)
    return diff < 6


def main():
    items = latest()
    src = INDEX.read_text()
    if not GRID.search(src):
        sys.exit('index.html に <ul class="art-grid"> が見つかりません')

    INSTA_DIR.mkdir(parents=True, exist_ok=True)
    lis, changed = [], []
    for i, it in enumerate(items, 1):
        dest = INSTA_DIR / f"{i:02d}.jpg"
        img_url = it.get("thumbnail_url") if it["media_type"] == "VIDEO" else it.get("media_url")
        new = square(get(img_url))
        if not (dest.exists() and same_picture(Image.open(dest).convert("RGB"), new)):
            new.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
            changed.append(i)
        alt = alt_text(it.get("caption"))
        ver = hashlib.md5(dest.read_bytes()).hexdigest()[:8]  # 写真が変わったらURLも変えてキャッシュを外す
        lis.append(
            "          <li>\n"
            f'            <a class="art-tile" href="{html.escape(it["permalink"])}" target="_blank" rel="noopener noreferrer">\n'
            f'              <img src="assets/insta/{i:02d}.jpg?v={ver}" alt="{html.escape(alt)}" width="{SIZE}" height="{SIZE}" loading="lazy" decoding="async" />\n'
            "            </a>\n"
            "          </li>"
        )
    new_src = GRID.sub(lambda m: m.group(1) + "\n".join(lis) + m.group(2), src, count=1)
    if new_src == src:
        print("投稿の並びも写真も今のまま。変更なし")
        return
    INDEX.write_text(new_src)
    print(f"index.html を書き換えました（写真を入れ替えた枠: {changed or 'なし'}）")


if __name__ == "__main__":
    main()
