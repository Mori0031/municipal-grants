from __future__ import annotations

import html
from datetime import date
from pathlib import Path

SITE_URL = "https://mori0031.github.io/municipal-grants/"
CONTACT_EMAIL = "daichiprojectwork@gmail.com"
OPERATOR = "LOCAL GRANTS運営事務局"


def _layout(path: str, title: str, description: str, body: str) -> str:
    canonical = SITE_URL + path + "/"
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | LOCAL GRANTS</title><meta name="description" content="{html.escape(description.split('|', 1)[-1])}"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}">
<style>:root{{--ink:#11110f;--paper:#f2f0e9;--gold:#927a4d;--line:#d2cec2}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Sans JP","Yu Gothic",sans-serif}}header{{background:#0b0b0a;color:#f4f1e8;padding:24px 5vw}}header a{{color:inherit;text-decoration:none;font-size:11px;font-weight:700;letter-spacing:.24em}}main{{max-width:900px;margin:auto;padding:64px 24px 100px}}.eyebrow{{font-size:10px;letter-spacing:.22em;color:var(--gold)}}h1,h2{{font-family:"Yu Mincho","Hiragino Mincho ProN",serif;font-weight:400}}h1{{font-size:clamp(2.2rem,5vw,4rem);line-height:1.3;margin:15px 0 45px}}h2{{font-size:1.55rem;margin:48px 0 15px;padding-top:25px;border-top:1px solid var(--line)}}p,li{{font-size:15px;line-height:2}}a{{color:#564722;text-underline-offset:4px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:16px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;line-height:1.7}}th{{width:180px;font-size:12px;color:#666}}.note{{margin-top:35px;padding:20px;border:1px solid var(--line);font-size:13px;line-height:1.8}}footer{{background:#0b0b0a;padding:30px 24px;text-align:center;color:#aaa69b;font-size:11px}}footer a{{color:#d5d0c4;margin:0 10px}}input,select,textarea{{width:100%;padding:13px;border:1px solid #aaa59a;background:#faf8f2;font:inherit}}label{{display:block;margin-top:18px;font-size:13px}}button{{margin-top:22px;padding:14px 22px;border:0;background:#111;color:white;font-weight:700;cursor:pointer}}@media(max-width:600px){{th,td{{display:block;width:100%;padding:10px 0}}}}</style></head>
<body><header><a href="{SITE_URL}">LOCAL GRANTS</a></header><main><p class="eyebrow">PUBLIC INFORMATION / EDITORIAL POLICY</p><h1>{html.escape(title)}</h1>{body}</main>
<footer><a href="{SITE_URL}">制度検索</a><a href="{SITE_URL}about/">運営者情報</a><a href="{SITE_URL}privacy/">プライバシー</a><a href="{SITE_URL}contact/">お問い合わせ</a></footer></body></html>'''


def build_content_pages(root: Path, grant_count: int) -> list[str]:
    today = date.today().isoformat()
    pages = {
        "about": ("運営者情報", f"運営者情報|{OPERATOR}の運営目的、情報源、連絡先をご案内します。", f'''
<table><tr><th>サイト名</th><td>LOCAL GRANTS</td></tr><tr><th>運営者</th><td>{OPERATOR}</td></tr><tr><th>目的</th><td>国・自治体の補助金、助成金、給付金、交付金を探しやすい形で整理し、必ず一次情報へ案内すること</td></tr><tr><th>掲載件数</th><td>{grant_count}件（生成時点）</td></tr><tr><th>連絡先</th><td><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></td></tr></table>
<h2>情報源</h2><p>デジタル庁が運営するJグランツ公開API、国の行政機関、地方公共団体が公開する公式ページを使用します。民間まとめサイトの記述を一次情報として転載しません。</p>
<h2>運営姿勢</h2><p>制度の利用を勧誘・保証するものではありません。掲載情報から公式ページへ移動し、最新の募集要項と申請条件を確認できることを最優先にします。</p>'''),
        "privacy": ("プライバシーポリシー", f"プライバシーポリシー|{OPERATOR}における個人情報、Cookie、広告配信の取扱いを説明します。", f'''
<p>{OPERATOR}（以下「当事務局」）は、本サイトで取り扱う情報を以下の方針に基づいて管理します。</p>
<h2>取得する情報</h2><p>通常の閲覧だけで、当事務局が氏名・住所・電話番号を直接取得することはありません。お問い合わせ時には、利用者が入力した氏名または名称、メールアドレス、問い合わせ内容を受信します。</p>
<h2>利用目的</h2><ul><li>問い合わせへの回答</li><li>誤掲載・更新情報の確認</li><li>サービス改善および不正利用防止</li></ul>
<h2>問い合わせフォーム</h2><p>フォームは利用者のメールアプリを起動する方式です。入力内容は当サイトのサーバーへ保存されず、利用者が選択したメールサービスを経由して当事務局へ送信されます。</p>
<h2>広告配信とCookie</h2><p>将来Google AdSenseを導入する場合、Googleなどの第三者配信事業者がCookieを使用し、過去のアクセス情報に基づいて広告を配信することがあります。導入時には必要な告知、同意管理、広告設定を追加します。現時点ではAdSense広告コードを設置していません。</p>
<h2>第三者提供</h2><p>法令に基づく場合を除き、本人の同意なく問い合わせ情報を第三者へ提供しません。</p>
<h2>安全管理・保管</h2><p>問い合わせ情報は回答と必要な記録のために限定して利用し、不要となった情報は合理的な範囲で削除します。</p>
<h2>外部リンク</h2><p>リンク先で行われる情報収集については、各運営者のプライバシーポリシーをご確認ください。</p>
<h2>改定</h2><p>法令・サービス内容・広告導入状況に応じて本方針を改定します。重要な変更は本ページで告知します。</p><p class="note">制定・最終更新日：{today}<br>お問い合わせ：<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>'''),
        "contact": ("お問い合わせ", f"お問い合わせ|掲載情報の訂正、削除、取材、その他のお問い合わせを受け付けます。", f'''
<p>掲載情報の訂正・削除依頼、公式情報の追加提案、その他のご連絡を受け付けています。個人番号、口座番号、健康情報などの機微情報は送信しないでください。</p>
<form id="contact-form"><label>お名前または名称<input id="contact-name" required maxlength="80"></label><label>返信先メールアドレス<input id="contact-from" type="email" required maxlength="160"></label><label>種別<select id="contact-category"><option>掲載情報の訂正</option><option>制度の追加提案</option><option>削除依頼</option><option>広告・取材</option><option>その他</option></select></label><label>お問い合わせ内容<textarea id="contact-message" rows="8" required maxlength="3000"></textarea></label><button type="submit">メールアプリを開く</button></form>
<p class="note">送信ボタンを押すと端末のメールアプリが開きます。開かない場合は <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> へ直接お送りください。通常5営業日以内を目安に確認しますが、返信を保証するものではありません。</p>
<script>document.getElementById('contact-form').addEventListener('submit',e=>{{e.preventDefault();const v=id=>document.getElementById(id).value.trim();const subject=`[LOCAL GRANTS] ${{v('contact-category')}}`;const body=`お名前・名称: ${{v('contact-name')}}\n返信先: ${{v('contact-from')}}\n\n${{v('contact-message')}}`;location.href=`mailto:{CONTACT_EMAIL}?subject=${{encodeURIComponent(subject)}}&body=${{encodeURIComponent(body)}}`;}});</script>'''),
        "editorial-policy": ("編集方針・情報更新方針", f"編集方針・情報更新方針|公式情報の収集、確認、更新、訂正に関するLOCAL GRANTSの方針です。", f'''
<h2>一次情報を優先</h2><p>国、地方公共団体、独立行政法人その他の公的機関が公開するページを出典とし、各制度から必ず公式情報へリンクします。</p>
<h2>事実抽出の原則</h2><p>制度名、対象者、金額・補助率、期限、地域を掲載します。本文にない説明、評価、受給可能性を付け加えません。不明な項目は「公式ページで確認」と表示します。</p>
<h2>更新頻度</h2><p>Jグランツの募集中案件と個人向け公式ページの有効性を、原則として毎日確認します。情報源の障害や仕様変更により更新が遅れる場合があります。</p>
<h2>重複・終了制度</h2><p>公式URLを識別子として重複を抑制します。終了・移転・削除を確認した制度は、データ更新時に非表示または訂正します。</p>
<h2>AIの利用</h2><p>自治体ページの項目抽出にAIを利用する場合がありますが、要約や推測は指示せず、本文中の事実抽出に限定します。Jグランツの構造化項目はAIを介さず利用します。</p>
<h2>訂正</h2><p>誤りを発見した場合は、制度名・公式URL・訂正内容を<a href="{SITE_URL}contact/">お問い合わせページ</a>からお知らせください。公式情報を確認して修正します。</p><p class="note">最終更新日：{today}</p>'''),
        "disclaimer": ("免責事項", f"免責事項|LOCAL GRANTSの掲載情報、外部リンク、制度判定機能に関する免責事項です。", '''
<h2>掲載情報</h2><p>正確性と最新性に配慮しますが、掲載内容の完全性、正確性、適用可能性を保証しません。制度内容は予告なく変更・終了する場合があります。</p>
<h2>申請・受給判断</h2><p>検索、比較、対象判定は候補を探す参考機能です。受給資格、採択、支給額、申請期限を確定するものではありません。必ず公式の募集要項を確認し、必要に応じて制度窓口または専門家へ相談してください。</p>
<h2>損害</h2><p>本サイトの利用または利用不能、掲載情報に基づく判断、外部サイトの利用によって生じた損害について、当事務局は法令上認められる範囲で責任を負いません。</p>
<h2>外部サイト</h2><p>外部リンク先の内容、安全性、個人情報の取扱いについて当事務局は管理しません。</p>
<h2>著作権</h2><p>制度名や事実情報を除き、本サイト独自の文章・デザイン等の権利は当事務局または正当な権利者に帰属します。</p>'''),
        "guide/how-to-choose": ("補助金・助成金・給付金の選び方", "guide/how-to-choose/|対象制度を探す順序、確認項目、申請前の注意点を解説します。", '''
<p>名称だけで判断せず、「誰が」「何に使えて」「いつまでに」「何を満たすか」の順で確認すると、候補を効率よく絞れます。</p>
<h2>1. 自分の区分を決める</h2><p>一般個人、個人事業主、法人では利用できる制度が異なります。個人事業主は「個人」ではなく「事業者」に含まれる制度が多い点に注意してください。</p>
<h2>2. 地域を確認する</h2><p>全国制度、都道府県制度、市区町村制度の順に探します。自治体制度では、居住地・所在地だけでなく、転入予定、納税状況、居住年数などが条件になる場合があります。</p>
<h2>3. 目的から探す</h2><p>子育て、教育、住居、就職、移住、省エネ、創業、設備投資など、支出や課題に近い言葉で検索します。</p>
<h2>4. 金額より先に対象条件を見る</h2><p>所得、年齢、世帯構成、事業規模、対象経費、事前着手禁止などを確認します。上限額は必ず受け取れる額ではありません。</p>
<h2>5. 期限と予算終了を確認する</h2><p>期限前でも予算到達で終了する制度があります。購入・契約後の申請が認められない制度もあるため、行動前に公式窓口へ確認してください。</p>
<h2>6. 公式情報で最終確認する</h2><p>募集要項、申請様式、必要書類、問い合わせ先を確認します。本サイトの比較・対象判定は候補抽出にのみ利用してください。</p>'''),
    }
    urls = []
    for path, (title, description, body) in pages.items():
        directory = root / path
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(
            _layout(path, title, description.split("|", 1)[-1], body), encoding="utf-8"
        )
        urls.append(SITE_URL + path + "/")
    return urls
