#!/usr/bin/env python3
"""naoblock ⌐◨-◨ 欄（index.html の .art-grid）の6枚を差し替える。

使い方（リポジトリのルートで実行）:
  1) 画像を取ってくる
     python3 .claude/skills/naoblock-insta-update/insta_update.py fetch URL1 URL2 ... URL6
     → assets/insta/01.jpg〜06.jpg を上書きし、各投稿のキャプション冒頭を表示。
       /tmp/insta_update.json に URL と仮の alt を書き出す。
  2) /tmp/insta_update.json の alt を画像を見て書き直す
  3) HTML を書き換える
     python3 .claude/skills/naoblock-insta-update/insta_update.py apply

  手元の写真を使う場合: fetch のあとに
     python3 .../insta_update.py local 番号 写真のパス   （例: local 4 ~/Downloads/a.jpg）
"""
import html
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

SIZE = 480  # index.html の width/height と合わせる
QUALITY = 75
ROOT = Path.cwd()
INSTA_DIR = ROOT / "assets" / "insta"
INDEX = ROOT / "index.html"
STATE = Path("/tmp/insta_update.json")
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def normalize(url):
    m = re.search(r"instagram\.com/(?:[^/]+/)?(p|reel|tv)/([A-Za-z0-9_-]+)", url)
    if not m:
        sys.exit(f"インスタの投稿URLではありません: {url}")
    kind = "reel" if m.group(1) in ("reel", "tv") else "p"
    return f"https://www.instagram.com/{kind}/{m.group(2)}/", m.group(2)


def image_url(embed_html):
    m = re.search(r'class="EmbeddedMediaImage"[^>]*', embed_html)
    if not m:
        return None
    tag = m.group(0)
    srcset = re.search(r'srcset="([^"]+)"', tag)
    if srcset:
        best = max(
            (c.strip().rsplit(" ", 1) for c in html.unescape(srcset.group(1)).split(",")),
            key=lambda p: int(p[1].rstrip("w")) if len(p) == 2 and p[1].rstrip("w").isdigit() else 0,
        )
        return best[0]
    src = re.search(r'src="([^"]+)"', tag)
    return html.unescape(src.group(1)) if src else None


def caption(embed_html):
    m = re.search(r'class="Caption"[^>]*>(.*?)</div>', embed_html, re.S)
    if not m:
        return ""
    text = re.sub(r"<[^>]+>", " ", m.group(1))
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return re.sub(r"^naoblock\.jp\s*", "", text)[:120]


def save_square(data, dest):
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    img = ImageOps.fit(img, (SIZE, SIZE), Image.LANCZOS, centering=(0.5, 0.5))
    img.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return dest.stat().st_size


def cmd_fetch(urls):
    if len(urls) != 6:
        sys.exit(f"URLは6件ちょうど渡してください（今は{len(urls)}件）")
    INSTA_DIR.mkdir(parents=True, exist_ok=True)
    items, failed = [], []
    for i, raw in enumerate(urls, 1):
        url, code = normalize(raw)
        dest = INSTA_DIR / f"{i:02d}.jpg"
        cap = ""
        try:
            embed = get(f"https://www.instagram.com/p/{code}/embed/captioned/").decode("utf-8", "replace")
            cap = caption(embed)
            src = image_url(embed)
            if not src:
                raise RuntimeError("埋め込みページに画像が見つからない")
            size = save_square(get(src), dest)
            print(f"{i:02d} OK {size // 1024}KB  {url}\n   キャプション: {cap or '（なし）'}")
        except Exception as e:  # 取れなかった枠は写真をもらって local で入れる
            failed.append(i)
            print(f"{i:02d} 失敗 {url}  ({e})")
        items.append({"url": url, "alt": cap[:40] or "（作品名）"})
    STATE.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    print(f"\n{STATE} に書き出しました。alt を画像を見て直してから apply してください。")
    if failed:
        print(f"取れなかった枠: {failed} → 写真をもらって local で入れる")


def cmd_local(num, path):
    size = save_square(Path(path).expanduser().read_bytes(), INSTA_DIR / f"{int(num):02d}.jpg")
    print(f"{int(num):02d} OK {size // 1024}KB  {path}")


def cmd_apply():
    items = json.loads(STATE.read_text())
    if len(items) != 6:
        sys.exit("項目が6件ではありません")
    lis = []
    for i, it in enumerate(items, 1):
        lis.append(
            "          <li>\n"
            f'            <a class="art-tile" href="{html.escape(it["url"])}" target="_blank" rel="noopener noreferrer">\n'
            f'              <img src="assets/insta/{i:02d}.jpg" alt="{html.escape(it["alt"])}" width="{SIZE}" height="{SIZE}" loading="lazy" decoding="async" />\n'
            "            </a>\n"
            "          </li>"
        )
    src = INDEX.read_text()
    new, n = re.subn(
        r'(<ul class="art-grid">\n).*?(\n\s*</ul>)',
        lambda m: m.group(1) + "\n".join(lis) + m.group(2),
        src,
        count=1,
        flags=re.S,
    )
    if n != 1:
        sys.exit('index.html に <ul class="art-grid"> が見つかりません')
    INDEX.write_text(new)
    print("index.html の6枚を書き換えました")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "fetch":
        cmd_fetch(args)
    elif cmd == "local" and len(args) == 2:
        cmd_local(*args)
    elif cmd == "apply":
        cmd_apply()
    else:
        sys.exit(__doc__)
