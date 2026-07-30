# 自治体 助成金・給付金コレクター

自治体公式サイトから候補ページを収集し、LLMで本文中の事実だけを構造化し、検索可能な静的サイトを生成します。

デジタル庁が運営するJグランツ公開APIから、47都道府県の募集中案件も毎日取得します。Jグランツの結果はAPIの構造化項目をそのまま使用するため、LLMによる要約は行いません。

`data/personal_grants.json`には国の公式ページで確認した個人向け制度を収録し、毎朝公式URLの有効性を確認して統合します。金額や期限が個別条件で変わる制度は推測せず、公式窓口での確認を案内します。

## 構成

```text
.
├─ scraper.py                 # 一覧・詳細ページの収集、URL単位の更新
├─ extractor.py               # LLMによる事実抽出
├─ build_site.py              # docs/index.html の生成
├─ content_pages.py           # 運営者情報・方針・独自記事の生成
├─ sources.yml                # 対象自治体とCSSセレクター
├─ requirements.txt
├─ .env.example
├─ data/grants.json
├─ data/personal_grants.json  # 個人向け制度の公式カタログ
├─ docs/index.html            # build_site.pyで生成
├─ docs/robots.txt            # 検索エンジン向けクロール設定
├─ docs/sitemap.xml           # Google Search Console送信用
└─ .github/workflows/daily_scrape.yml
```

生成サイトには、キーワード・地域・対象者検索に加えて、締切順などの並べ替え、最大3制度の比較、簡易的な対象候補の絞り込みを備えています。判定結果は受給資格を保証しないため、必ずリンク先の公式情報で確認します。

運営者情報、プライバシーポリシー、お問い合わせ、編集方針、免責事項、制度の選び方も `build_site.py` の実行時に `docs/` 配下へ生成されます。

## 初回実行

Python 3.11以上を用意し、依存パッケージをインストールします。`.env.example`を参考に `OPENAI_API_KEY` を環境変数へ設定してください。

```bash
pip install -r requirements.txt
python scraper.py --dry-run
python scraper.py
python build_site.py
```

GitHubリポジトリでは `OPENAI_API_KEY` をActions secretに登録し、PagesのSourceを「GitHub Actions」に設定します。

## 自治体の追加

`sources.yml` に一覧URL、地域、一覧リンクと本文領域のCSSセレクターを追加します。利用規約とrobots.txtを確認し、許可されないページは対象にしないでください。
