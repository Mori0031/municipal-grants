from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import shutil
from datetime import date
from pathlib import Path


PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
]
SITE_URL = "https://mori0031.github.io/municipal-grants/"


TEMPLATE = r'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="全国の補助金・助成金・給付金・交付金を都道府県、対象者、キーワードから検索。自治体とデジタル庁の公式情報を毎日更新します。">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="https://mori0031.github.io/municipal-grants/">
<meta property="og:type" content="website"><meta property="og:locale" content="ja_JP">
<meta property="og:site_name" content="LOCAL GRANTS"><meta property="og:title" content="全国の補助金・助成金・給付金検索 | LOCAL GRANTS">
<meta property="og:description" content="自治体とデジタル庁の公式情報から、全国の支援制度を検索できます。">
<meta property="og:url" content="https://mori0031.github.io/municipal-grants/">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="全国の補助金・助成金・給付金検索 | LOCAL GRANTS">
<title>全国の補助金・助成金・給付金・交付金検索 | LOCAL GRANTS</title>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"LOCAL GRANTS","url":"https://mori0031.github.io/municipal-grants/","inLanguage":"ja","description":"全国の補助金・助成金・給付金・交付金を公式情報から検索できるサイト"}</script>
<script src="https://cdn.tailwindcss.com"></script>
<style>
:root{--ink:#11110f;--paper:#f2f0e9;--gold:#a58a55;--line:#d2cec2;--muted:#6d6a61}
html{scroll-behavior:smooth}body{background:var(--paper);color:var(--ink);font-family:"Noto Sans JP","Yu Gothic",sans-serif}
.serif{font-family:"Yu Mincho","Hiragino Mincho ProN",serif}.hairline{border-color:var(--line)}
.field{width:100%;border:0;border-bottom:1px solid #8f8b80;background:transparent;padding:.8rem 2rem .8rem 0;color:var(--ink);outline:none;border-radius:0}
.field:focus{border-color:var(--gold);box-shadow:0 1px 0 var(--gold)}
.card{transition:transform .25s ease,border-color .25s ease}.card:hover{transform:translateY(-3px);border-color:#a58a55}
.arrow{transition:transform .2s ease}.card:hover .arrow{transform:translateX(4px)}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
</style></head>
<body>
<header class="border-b border-white/20 bg-[#0b0b0a] text-[#f4f1e8]">
  <nav class="mx-auto flex max-w-7xl items-center justify-between px-5 py-6 lg:px-10" aria-label="主要ナビゲーション">
    <a href="#" class="text-[11px] font-semibold tracking-[.24em]">LOCAL GRANTS</a>
    <p class="hidden text-[10px] tracking-[.18em] text-[#aaa69b] sm:block">OFFICIAL PUBLIC SOURCES / UPDATED DAILY</p>
  </nav>
  <div class="mx-auto grid max-w-7xl lg:grid-cols-[1.25fr_.75fr]">
    <div class="px-5 pb-14 pt-14 lg:px-10 lg:pb-20 lg:pt-20">
      <p class="mb-7 text-[11px] font-semibold tracking-[.24em] text-[#b7a881]">全国の補助金・助成金・給付金・交付金を検索</p>
      <h1 class="serif max-w-4xl text-[clamp(2.35rem,4.5vw,4.8rem)] leading-[1.14] tracking-[-.035em]"><span class="block">必要な制度を、</span><span class="block"><span class="text-[#b7a881]">一次情報</span>から探す。</span></h1>
      <p class="mt-8 max-w-2xl text-sm leading-7 text-[#bdb9ae]">自治体とデジタル庁の公式情報をもとに、対象者・支給額・申請期限を整理しています。申請前にはリンク先で最新の条件をご確認ください。</p>
    </div>
    <aside class="border-t border-white/15 px-5 py-10 lg:border-l lg:border-t-0 lg:px-10 lg:py-20" aria-label="このサイトについて">
      <p class="text-[10px] font-semibold tracking-[.24em] text-[#b7a881]">ABOUT THIS SERVICE</p>
      <h2 class="serif mt-4 text-2xl text-[#f4f1e8]">公的な支援制度を、<br>探しやすく。</h2>
      <p class="mt-5 max-w-md text-sm leading-7 text-[#aaa69b]">全国の募集中案件を毎朝更新。都道府県と対象者を選び、制度名・目的・金額から横断検索できます。</p>
      <dl class="mt-9 grid grid-cols-2 gap-px border-y border-white/15 bg-white/15">
        <div class="bg-[#0b0b0a] py-5 pr-5"><dt class="text-[9px] tracking-[.18em] text-[#77736a]">PREFECTURES</dt><dd class="serif mt-1 text-2xl text-[#f4f1e8]">47</dd></div>
        <div class="bg-[#0b0b0a] py-5 pl-5"><dt class="text-[9px] tracking-[.18em] text-[#77736a]">LISTINGS</dt><dd class="serif mt-1 text-2xl text-[#f4f1e8]">__GRANT_COUNT__</dd></div>
      </dl>
      <p class="mt-5 text-[10px] leading-5 tracking-wider text-[#77736a]">掲載情報は申請を保証するものではありません。</p>
    </aside>
    </div>
  </div>
</header>

<main>
  <section class="border-b hairline" aria-labelledby="search-heading">
    <div class="mx-auto max-w-7xl px-5 py-12 lg:px-10 lg:py-16">
      <div class="mb-10 flex items-end justify-between gap-5"><div><p class="text-[10px] tracking-[.24em] text-[#8b764d]">SEARCH</p><h2 id="search-heading" class="serif mt-2 text-3xl">制度を絞り込む</h2></div><button id="reset" class="text-xs underline decoration-[#a58a55] underline-offset-4">条件をクリア</button></div>
      <div class="grid gap-8 md:grid-cols-3">
        <label class="text-xs font-semibold tracking-wider">キーワード<input id="query" type="search" placeholder="制度名・対象・金額" class="field mt-2"></label>
        <label class="text-xs font-semibold tracking-wider">都道府県<select id="prefecture" class="field mt-2"><option value="">全国すべて</option>__PREFECTURE_OPTIONS__</select></label>
        <label class="text-xs font-semibold tracking-wider">対象者<select id="target" class="field mt-2"><option value="">すべての対象者</option><option value="事業者">事業者</option><option value="個人">個人</option><option value="法人">法人</option><option value="個人事業主">個人事業主</option></select></label>
      </div>
    </div>
  </section>

  <section class="mx-auto max-w-7xl px-5 py-12 lg:px-10 lg:py-20" aria-labelledby="results-heading">
    <div class="mb-8 flex items-baseline justify-between border-b border-black pb-5">
      <h2 id="results-heading" class="serif text-2xl">掲載制度</h2>
      <p class="text-xs tracking-wider"><strong id="count" class="serif mr-1 text-3xl font-normal" aria-live="polite">0</strong>件</p>
    </div>
    <div id="results" class="grid gap-px bg-[#d2cec2] border border-[#d2cec2] md:grid-cols-2"></div>
    <div id="empty" class="hidden border-b hairline py-20 text-center"><p class="serif text-2xl">該当する制度はありません</p><p class="mt-3 text-sm text-[#6d6a61]">条件を変えてもう一度お試しください。</p></div>
  </section>
</main>
<footer class="bg-[#0b0b0a] text-[#aaa69b]"><div class="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-9 text-[11px] tracking-wider sm:flex-row sm:items-center sm:justify-between lg:px-10"><p>LOCAL GRANTS</p><p>掲載内容は申請を保証するものではありません。公式情報をご確認ください。</p></div></footer>

<script id="grant-data" type="application/json">__GRANT_DATA__</script>
<script>
const grants=JSON.parse(document.getElementById('grant-data').textContent);
const q=document.getElementById('query'),pref=document.getElementById('prefecture'),target=document.getElementById('target');
const esc=s=>String(s??'公式ページで確認').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function render(){const needle=q.value.trim().toLowerCase();const rows=grants.filter(g=>{const hay=[g.title,g.target,g.amount,g.deadline,g.prefecture,g.city].join(' ').toLowerCase();const targetText=String(g.target||'');const targetMatch=!target.value||(target.value==='個人'?(targetText.includes('個人')&&!targetText.includes('個人事業主')):targetText.includes(target.value));return(!needle||hay.includes(needle))&&(!pref.value||g.prefecture===pref.value)&&targetMatch});
 document.getElementById('count').textContent=rows.length;document.getElementById('empty').classList.toggle('hidden',rows.length>0);
 document.getElementById('results').innerHTML=rows.map((g,i)=>`<article class="card flex min-h-[340px] flex-col bg-[#f8f6ef] p-6 lg:p-9">
 <div class="flex items-center justify-between"><p class="text-[10px] font-semibold tracking-[.18em] text-[#8b764d]">${esc(g.prefecture)} / ${esc(g.city)}</p><span class="serif text-sm text-[#8d897f]">${String(i+1).padStart(2,'0')}</span></div>
 <h3 class="serif mt-7 text-[1.45rem] leading-[1.55]">${esc(g.title)}</h3>
 <dl class="mt-8 grid gap-4 text-sm"><div class="grid grid-cols-[5.5rem_1fr] border-t hairline pt-3"><dt class="text-xs text-[#6d6a61]">対象</dt><dd class="leading-6">${esc(g.target)}</dd></div><div class="grid grid-cols-[5.5rem_1fr] border-t hairline pt-3"><dt class="text-xs text-[#6d6a61]">金額・補助率</dt><dd class="leading-6">${esc(g.amount)}</dd></div><div class="grid grid-cols-[5.5rem_1fr] border-t hairline pt-3"><dt class="text-xs text-[#6d6a61]">申請期限</dt><dd class="leading-6">${esc(g.deadline)}</dd></div></dl>
 <div class="mt-auto flex items-end justify-between gap-4 pt-8"><time class="text-[10px] tracking-wider text-[#77736a]">取得 ${esc(g.updated_at)}</time><div class="flex items-center gap-4"><a href="${esc(g.detail_url)}" class="text-xs underline decoration-[#a58a55] underline-offset-4">制度詳細</a><a href="${esc(g.source_url)}" target="_blank" rel="noopener noreferrer" class="group text-xs font-semibold tracking-wider">公式情報 <span class="arrow ml-1 inline-block text-[#9c8353]">→</span></a></div></div></article>`).join('')}
[q,pref,target].forEach(el=>el.addEventListener('input',render));document.getElementById('reset').addEventListener('click',()=>{q.value='';pref.value='';target.value='';render();q.focus()});render();
</script></body></html>'''

DETAIL_TEMPLATE = r'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ | LOCAL GRANTS</title><meta name="description" content="__DESCRIPTION__"><meta name="robots" content="index,follow"><link rel="canonical" href="__CANONICAL__">
<meta property="og:type" content="article"><meta property="og:locale" content="ja_JP"><meta property="og:title" content="__TITLE__"><meta property="og:description" content="__DESCRIPTION__"><meta property="og:url" content="__CANONICAL__">
<style>:root{--ink:#11110f;--paper:#f2f0e9;--gold:#a58a55;--line:#d2cec2}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Sans JP","Yu Gothic",sans-serif}header{background:#0b0b0a;color:#f4f1e8;padding:24px 5vw}header a{color:inherit;text-decoration:none;font-size:11px;font-weight:700;letter-spacing:.24em}main{max-width:900px;margin:auto;padding:64px 24px 100px}.area{font-size:11px;letter-spacing:.18em;color:#806d48}.serif{font-family:"Yu Mincho","Hiragino Mincho ProN",serif}h1{font-size:clamp(2rem,5vw,3.6rem);line-height:1.35;font-weight:400;margin:22px 0 48px}dl{border-top:1px solid #111}dl div{display:grid;grid-template-columns:130px 1fr;gap:24px;padding:22px 0;border-bottom:1px solid var(--line)}dt{font-size:12px;color:#68655e}dd{margin:0;line-height:1.8}.actions{display:flex;flex-wrap:wrap;gap:16px;margin-top:48px}.button{display:inline-block;padding:14px 20px;background:#111;color:white;text-decoration:none;font-size:13px}.back{display:inline-block;padding:14px 0;color:#111;text-underline-offset:5px}footer{border-top:1px solid var(--line);padding:30px 24px;text-align:center;font-size:11px;color:#6d6a61}@media(max-width:600px){dl div{grid-template-columns:1fr;gap:7px}}</style>
</head><body><header><a href="__HOME__">LOCAL GRANTS</a></header><main><p class="area">__AREA__</p><h1 class="serif">__TITLE__</h1><dl><div><dt>対象</dt><dd>__TARGET__</dd></div><div><dt>金額・補助率</dt><dd>__AMOUNT__</dd></div><div><dt>申請期限</dt><dd>__DEADLINE__</dd></div><div><dt>情報取得日</dt><dd>__UPDATED__</dd></div></dl><div class="actions"><a class="button" href="__SOURCE__" target="_blank" rel="noopener noreferrer">公式情報を確認する →</a><a class="back" href="__HOME__">検索一覧へ戻る</a></div></main><footer>申請前に必ず公式ページで最新情報をご確認ください。</footer></body></html>'''


def build(input_path: Path, output_path: Path) -> None:
    grants = json.loads(input_path.read_text(encoding="utf-8"))
    site_grants = []
    for grant in grants:
        slug = hashlib.sha256(grant["source_url"].encode("utf-8")).hexdigest()[:16]
        site_grants.append({**grant, "detail_url": f"grants/{slug}/"})
    payload = json.dumps(site_grants, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    options = "".join(f'<option value="{name}">{name}</option>' for name in PREFECTURES)
    html = (TEMPLATE.replace("__GRANT_DATA__", payload)
            .replace("__PREFECTURE_OPTIONS__", options)
            .replace("__GRANT_COUNT__", str(len(grants))))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    grants_root = output_path.parent / "grants"
    if grants_root.exists():
        shutil.rmtree(grants_root)
    detail_urls = []
    for grant in site_grants:
        detail_dir = output_path.parent / grant["detail_url"]
        detail_dir.mkdir(parents=True, exist_ok=True)
        canonical = SITE_URL + grant["detail_url"]
        description = f"{grant.get('prefecture') or '全国'}の{grant.get('title')}。対象、金額・補助率、申請期限を公式情報から確認できます。"
        values = {
            "__TITLE__": grant.get("title") or "制度情報",
            "__DESCRIPTION__": description,
            "__CANONICAL__": canonical,
            "__HOME__": SITE_URL,
            "__AREA__": " / ".join(filter(None, [grant.get("prefecture"), grant.get("city")])) or "全国",
            "__TARGET__": grant.get("target") or "公式ページで確認",
            "__AMOUNT__": grant.get("amount") or "公式ページで確認",
            "__DEADLINE__": grant.get("deadline") or "公式ページで確認",
            "__UPDATED__": grant.get("updated_at") or "",
            "__SOURCE__": grant["source_url"],
        }
        page = DETAIL_TEMPLATE
        for token, value in values.items():
            page = page.replace(token, html_lib.escape(str(value), quote=True))
        (detail_dir / "index.html").write_text(page, encoding="utf-8")
        detail_urls.append(canonical)
    output_path.with_name("robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8"
    )
    lastmod = date.today().isoformat()
    sitemap_entries = [f'  <url><loc>{SITE_URL}</loc><lastmod>{lastmod}</lastmod><changefreq>daily</changefreq></url>']
    sitemap_entries.extend(f'  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod><changefreq>daily</changefreq></url>' for url in detail_urls)
    output_path.with_name("sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap_entries) + '\n</urlset>\n', encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="検索サイトを生成します")
    parser.add_argument("--input", type=Path, default=Path("data/grants.json"))
    parser.add_argument("--output", type=Path, default=Path("docs/index.html"))
    args = parser.parse_args()
    build(args.input, args.output)
