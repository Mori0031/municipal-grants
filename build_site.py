from __future__ import annotations

import argparse
import json
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


TEMPLATE = r'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="自治体公式サイトを出典とする助成金・給付金情報の検索サイト">
<title>LOCAL GRANTS — 自治体制度検索</title>
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
    <a href="#" class="text-sm font-semibold tracking-[.24em]">LOCAL GRANTS</a>
    <p class="hidden text-[11px] tracking-[.18em] text-[#aaa69b] sm:block">OFFICIAL MUNICIPAL SOURCES</p>
  </nav>
  <div class="mx-auto grid max-w-7xl lg:grid-cols-[1.25fr_.75fr]">
    <div class="px-5 pb-14 pt-16 lg:px-10 lg:pb-24 lg:pt-24">
      <p class="mb-7 text-[11px] font-semibold tracking-[.28em] text-[#b7a881]">FIND THE RIGHT SUPPORT</p>
      <h1 class="serif max-w-4xl text-[clamp(2.5rem,6vw,5.8rem)] leading-[1.08] tracking-[-.03em]">必要な制度を、<br><span class="text-[#b7a881]">一次情報</span>から探す。</h1>
      <p class="mt-8 max-w-xl text-sm leading-7 text-[#bdb9ae]">自治体の公式ページを出典に、対象者・支給額・申請期限を整理しています。申請前には必ず公式ページで最新情報をご確認ください。</p>
    </div>
    <div class="relative hidden border-l border-white/15 lg:block" aria-hidden="true">
      <div class="absolute inset-0 grid grid-cols-3"> <i class="border-r border-white/10"></i><i class="border-r border-white/10"></i><i></i></div>
      <div class="absolute bottom-10 left-10 right-10 border-t border-[#b7a881] pt-4 text-right text-[10px] tracking-[.22em] text-[#b7a881]">47 PREFECTURES / PRIMARY SOURCES</div>
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
        <label class="text-xs font-semibold tracking-wider">対象者<select id="target" class="field mt-2"><option value="">すべての対象者</option><option value="個人">個人</option><option value="法人">法人</option><option value="個人事業主">個人事業主</option></select></label>
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
function render(){const needle=q.value.trim().toLowerCase();const rows=grants.filter(g=>{const hay=[g.title,g.target,g.amount,g.deadline,g.prefecture,g.city].join(' ').toLowerCase();return(!needle||hay.includes(needle))&&(!pref.value||g.prefecture===pref.value)&&(!target.value||String(g.target||'').includes(target.value))});
 document.getElementById('count').textContent=rows.length;document.getElementById('empty').classList.toggle('hidden',rows.length>0);
 document.getElementById('results').innerHTML=rows.map((g,i)=>`<article class="card flex min-h-[340px] flex-col bg-[#f8f6ef] p-6 lg:p-9">
 <div class="flex items-center justify-between"><p class="text-[10px] font-semibold tracking-[.18em] text-[#8b764d]">${esc(g.prefecture)} / ${esc(g.city)}</p><span class="serif text-sm text-[#8d897f]">${String(i+1).padStart(2,'0')}</span></div>
 <h3 class="serif mt-7 text-[1.45rem] leading-[1.55]">${esc(g.title)}</h3>
 <dl class="mt-8 grid gap-4 text-sm"><div class="grid grid-cols-[5.5rem_1fr] border-t hairline pt-3"><dt class="text-xs text-[#6d6a61]">対象</dt><dd class="leading-6">${esc(g.target)}</dd></div><div class="grid grid-cols-[5.5rem_1fr] border-t hairline pt-3"><dt class="text-xs text-[#6d6a61]">金額・補助率</dt><dd class="leading-6">${esc(g.amount)}</dd></div><div class="grid grid-cols-[5.5rem_1fr] border-t hairline pt-3"><dt class="text-xs text-[#6d6a61]">申請期限</dt><dd class="leading-6">${esc(g.deadline)}</dd></div></dl>
 <div class="mt-auto flex items-end justify-between gap-4 pt-8"><time class="text-[10px] tracking-wider text-[#77736a]">取得 ${esc(g.updated_at)}</time><a href="${esc(g.source_url)}" target="_blank" rel="noopener noreferrer" class="group text-xs font-semibold tracking-wider">公式情報を見る <span class="arrow ml-2 inline-block text-[#9c8353]">→</span></a></div></article>`).join('')}
[q,pref,target].forEach(el=>el.addEventListener('input',render));document.getElementById('reset').addEventListener('click',()=>{q.value='';pref.value='';target.value='';render();q.focus()});render();
</script></body></html>'''


def build(input_path: Path, output_path: Path) -> None:
    grants = json.loads(input_path.read_text(encoding="utf-8"))
    payload = json.dumps(grants, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    options = "".join(f'<option value="{name}">{name}</option>' for name in PREFECTURES)
    html = TEMPLATE.replace("__GRANT_DATA__", payload).replace("__PREFECTURE_OPTIONS__", options)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="検索サイトを生成します")
    parser.add_argument("--input", type=Path, default=Path("data/grants.json"))
    parser.add_argument("--output", type=Path, default=Path("docs/index.html"))
    args = parser.parse_args()
    build(args.input, args.output)
