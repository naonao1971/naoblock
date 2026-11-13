# naoblock
naoblock.jp ─ 咲耶GAMES・ナノブロック・Nouns ⌐◨-◨

## ゲームの足し方（台帳 assets/games.json）

トップページのゲームのカードと、一覧ページ（/games/）は、どちらも `assets/games.json` を読んで並べます。

- 新しいゲームは `games` の**先頭**に1件足すだけ（HTML の書き換えは要らない）
- `pickup: true` のものが、上から5件までトップに出る（PC は1列5枚）
- `tags` はジャンルとキャラ。選べるタグは `groups` に並べる（一覧ページのボタンになる）
- `released` は公開日（新しい順・古い順の並べ替えに使う）、`badge` は NEW / UPDATE など
- `thumb` を省くと、ゲームの URL の `ogp.png` を使う
