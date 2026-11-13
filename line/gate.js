// LINE友だち限定の先行公開（全ゲーム共通）。ゲームの <head> の最初のほうに 1 行だけ足す：
//   <script src="https://naoblock.com/line/gate.js" data-title="咲耶フットボール"></script>
// 公式LINEの友だちだと分かっている人（naoblock.com/line/ が置いた目印のクッキー nb_line がある人）はそのまま遊べる。
// ない人には全画面の案内を出して、naoblock.com/line/ で確かめてから戻ってきてもらう。
// 一般公開するときは、ゲームからこの 1 行を消すだけ（台帳 games.json の line: true も外す）。
// ブラウザ内だけの簡易判定（本気で抜けようとすれば抜けられる。先行公開ならこれで十分という判断）
(function () {
  var host = location.hostname;
  // 手元の確認（localhost）やプレビューの URL では止めない
  if (!(host === "naoblock.com" || /\.naoblock\.com$/.test(host))) return;
  if (/(?:^|;\s*)nb_line=/.test(document.cookie)) return;

  var me = document.currentScript;
  var title = (me && me.getAttribute("data-title")) || "このゲーム";
  var GATE = "https://naoblock.com/line/";
  var open = true;

  // 案内が出ている間は、ゲームにキーを渡さない（ゲームより先に読み込まれるので、先に受け取れる）
  ["keydown", "keyup", "keypress"].forEach(function (t) {
    window.addEventListener(t, function (e) {
      if (open) e.stopImmediatePropagation();
    }, true);
  });

  var esc = function (s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  };
  var css =
    "#nb-line-gate,#nb-line-gate *{box-sizing:border-box}#nb-line-gate{position:fixed;inset:0;z-index:2147483647;display:grid;place-items:center;padding:20px;background:rgba(6,7,12,.94);font-family:'Noto Sans JP','Hiragino Kaku Gothic ProN',system-ui,sans-serif;color:#151515;overflow:auto}" +
    "#nb-line-gate .b{width:min(100%,440px);background:#fff;border:3px solid #151515;box-shadow:5px 5px 0 #06c755;padding:26px 20px;text-align:center;line-height:1.8}" +
    "#nb-line-gate h2{margin:0 0 10px;font-size:1.15rem}#nb-line-gate p{margin:0 0 12px;font-size:.95rem}" +
    "#nb-line-gate .go{display:inline-block;margin:6px 0 4px;padding:12px 22px;border:3px solid #151515;background:#06c755;color:#fff;font-weight:900;font-size:1rem;text-decoration:none}" +
    "#nb-line-gate .s{font-size:.78rem;color:#5d5d5d;margin:14px 0 0}#nb-line-gate .s a{color:#5d5d5d}";

  var show = function () {
    if (document.getElementById("nb-line-gate")) return;
    var st = document.createElement("style");
    st.textContent = css;
    document.head.appendChild(st);
    var d = document.createElement("div");
    d.id = "nb-line-gate";
    d.setAttribute("role", "dialog");
    d.setAttribute("aria-modal", "true");
    var back = location.href.split("#")[0];
    d.innerHTML =
      '<div class="b"><h2>🔒 LINE友だち限定の先行公開</h2>' +
      "<p><b>" + esc(title) + "</b>は、いまは公式LINE「NCNPナオブロックラボ」の友だちだけが先に遊べます。</p>" +
      "<p>LINE でログインすると、そのまま友だち追加もできます。一度確かめれば、しばらくはそのまま遊べます。</p>" +
      '<a class="go" href="' + GATE + "?back=" + encodeURIComponent(back) + '">LINE で確かめて遊ぶ</a>' +
      '<p class="s"><a href="https://naoblock.com/games/">ほかのゲームを見る</a>　<a href="' + GATE + 'privacy.html">プライバシーポリシー</a></p></div>';
    document.body.appendChild(d);
    // 遊べる状態のまま戻ってきた（別のタブで確かめた等）ときは、案内を閉じる
    window.addEventListener("pageshow", function () {
      if (/(?:^|;\s*)nb_line=/.test(document.cookie)) { open = false; d.remove(); }
    });
  };
  if (document.body) show();
  else document.addEventListener("DOMContentLoaded", show);
})();
