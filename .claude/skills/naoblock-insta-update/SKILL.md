---
name: naoblock-insta-update
description: >
  naoblock.jp の「naoblock ⌐◨-◨」欄（トップページのブロックアート欄・インスタ作品6枚）を差し替えるスキル。
  なおなおがインスタの投稿URLを6件渡して「インスタ欄を差し替えて」「⌐◨-◨欄を最新にして」「インスタ更新した」と頼んだときに使う。
  スマホの Claude（Claude Code on the web）から、Macを使わずに実行できる。
---

# naoblock ⌐◨-◨ 欄の差し替え

`index.html` の `<ul class="art-grid">` の6枚と、`assets/insta/01.jpg`〜`06.jpg` を、渡された6件の投稿に入れ替える。
この欄は手動タイル方式（HTMLに直接書く）。インスタに投稿しただけではサイトに出ないので、このスキルで入れ替える。

> **2026-10-31〜 自動更新あり**：`.github/workflows/insta-auto.yml` が1日2回（7:00・21:00 JST）、インスタの最新6件に自動で差し替える（`tools/insta_auto.py`）。
> 「今すぐ最新にして」なら、このスキルではなく Actions の insta-auto を手動実行する（`gh workflow run insta-auto`）。
> このスキルで手動で入れ替えても、次の自動実行で最新6件に戻る。推しを固定したい場合は、先に自動更新の作りを変える相談をする。

## 1. URLを受け取る
- 6件ちょうど。**並び順はなおなおに渡された順のまま**（左上→右へ→次の段）。新しい順に、と言われたら投稿日の新しい順に並べ替える（日付はインスタの投稿ページで確認。分からなければ渡された順で進めて、そのことを伝える）
- 6件より少ない／多いときは、作業に入る前に聞き返す
- `https://www.instagram.com/p/…/`・`/reel/…/`・末尾に `?igsh=…` が付いたものも、そのまま使える

## 2. 画像を取って正方形に切り出す
リポジトリのルートで実行する。Pillow がなければ先に `pip install pillow`。
```bash
python3 .claude/skills/naoblock-insta-update/insta_update.py fetch URL1 URL2 URL3 URL4 URL5 URL6
```
- インスタの埋め込みページ（ログイン不要）から画像を取り、中央を正方形に切り出して 480px・JPEG にする。キャプションの冒頭も表示される
- **「失敗」の枠が出たら**、その枠の写真をなおなおに頼んで、もらった画像で入れる：
  `python3 .claude/skills/naoblock-insta-update/insta_update.py local 番号 画像のパス`
- インスタの画像URLを `<img>` に直接書かない（期限つきで、しばらくすると表示が切れる）

## 3. 画像を見て alt を書く
- `assets/insta/01.jpg`〜`06.jpg` を1枚ずつ開いて見る。キャプションも参考にして、`/tmp/insta_update.json` の `alt` を書き直す
- 書き方は今の欄に合わせる。例：「にんナノ展：緑のお城とグレーの猫の作品」「メガネフェス in 鯖江「ミニナノ展」のブース」
- 正方形にしたら作品がほとんど写っていない枠は、なおなおに伝えて、別の投稿か元の写真をもらう

## 4. HTMLを書き換える
```bash
python3 .claude/skills/naoblock-insta-update/insta_update.py apply
git diff --stat   # index.html と assets/insta/ だけが変わっていること
```

## 5. 確認してもらってから公開する
- `main` に push すると数分で本番（naoblock.jp、GitHub Pages）に出る。**なおなおのOKなしに `main` へ push しない**
- なおなおに、6枠の「番号・alt・投稿URL」を表で見せる
- **スマホ（Claude Code on the web）のとき**：作業用のブランチにコミットして push し、プルリクエストを作る。GitHubアプリの「Files changed」で6枚の画像が見られる。なおなおがOKならマージしてもらう（マージすると本番に出る）
- **Mac（秘書室bot）のとき**：`python3 -m http.server 8000 --bind 0.0.0.0` で携帯から見てもらい（家のWi-Fiなら http://MacのIP:8000/ 、IPは `ipconfig getifaddr en0` で調べる）、OKをもらってから `main` に push する
- 公開して数分したら https://naoblock.jp/ を開いて、6枚が新しくなっているか確かめる（キャッシュで古いままのときは少し待つ）

コミットメッセージ例：`naoblock ⌐◨-◨ 欄のインスタ作品6点を差し替え`

## 守ること
- 見出し・ボタンには「ナノブロック」をブランド名として使わない（カワダの商標）。リード文や alt で「ナノブロックで作った」と素材として触れるのはよい（作品はすべてナノブロック製）
- 触るのは `index.html` の `.art-grid` の中と `assets/insta/` だけ。CSSやほかの欄は変えない
- 6枚以外の数にしたいと言われたら、CSSの並び（スマホ2列・PC3列）が崩れるので、相談してから進める
