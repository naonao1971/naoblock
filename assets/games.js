// ゲームの台帳（assets/games.json）を読んで、カードを作る。トップページと /games/ の一覧で使う
const esc = (v) => String(v).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
// タイトルの中の英字（Noun など）は英字の書体で
const titleHtml = (t) => esc(t).replace(/[A-Za-z][A-Za-z0-9 ]*/g, (m) => `<span class="en">${m}</span>`);

export async function loadGames(base = "") {
  const r = await fetch(`${base}assets/games.json?v=${Math.floor(Date.now() / 600000)}`); // 10分ごとに読み直す
  if (!r.ok) throw new Error(`games.json ${r.status}`);
  return r.json();
}

// detail: 一覧ページ用（説明とタグも出す）
export function gameCard(g, { detail = false } = {}) {
  const thumb = g.thumb || `${g.url.replace(/\/?$/, "/")}ogp.png`;
  return `<a class="game-card c-${esc(g.color || "yellow")}${detail ? " is-detail" : ""}" href="${esc(g.url)}">`
    + (g.badge ? `<span class="badge-new">${esc(g.badge)}</span>` : "")
    + `<span class="thumb"><img src="${esc(thumb)}" alt="" width="1200" height="630" loading="lazy" decoding="async" /></span>`
    + `<span class="game-title">${titleHtml(g.title)}</span>`
    + (detail
      ? `<span class="game-desc">${esc(g.desc || "")}</span><span class="game-tags">${(g.tags || []).map((t) => `<i>${esc(t)}</i>`).join("")}</span>`
      : "")
    + `</a>`;
}
