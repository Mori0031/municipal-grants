from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
import yaml
from bs4 import BeautifulSoup

from extractor import extract_grant

USER_AGENT = "MunicipalGrantCollector/1.0 (+https://github.com/your-org/municipal-grants; public-interest research)"
MIN_INTERVAL_SECONDS = 2.0
GRANT_WORDS = ("補助金", "助成金", "給付金", "支援金", "奨励金", "交付金")
PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
]
JGRANTS_API = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"


class PoliteSession:
    def __init__(self, interval: float = MIN_INTERVAL_SECONDS) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "ja,en;q=0.5"})
        self.interval = max(interval, MIN_INTERVAL_SECONDS)
        self.last_request_at = 0.0
        self.robots: dict[str, RobotFileParser] = {}

    def _allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self.robots:
            robots_url = urljoin(origin, "/robots.txt")
            parser = RobotFileParser(robots_url)
            try:
                response = self.session.get(robots_url, timeout=(10, 20))
                if response.status_code == 404:
                    parser.parse(["User-agent: *", "Allow: /"])
                else:
                    response.raise_for_status()
                    parser.parse(response.text.splitlines())
            except requests.RequestException:
                # robots.txtが一時的に確認不能なサイトにはアクセスしない（安全側）。
                parser.parse(["User-agent: *", "Disallow: /"])
                logging.warning("robots.txtを確認できないため取得を見送ります: %s", origin)
            self.robots[origin] = parser
        return self.robots[origin].can_fetch(USER_AGENT, url)

    def get(self, url: str) -> requests.Response:
        if not self._allowed(url):
            raise PermissionError(f"robots.txtにより取得できません: {url}")
        wait = self.interval - (time.monotonic() - self.last_request_at)
        if wait > 0:
            time.sleep(wait)
        response = self.session.get(url, timeout=(10, 30))
        self.last_request_at = time.monotonic()
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        return response

    def get_api(self, url: str, *, params: dict[str, str]) -> requests.Response:
        """公開API用。robots.txtの代わりにAPI利用規約に従い、同じ間隔制御を行う。"""
        wait = self.interval - (time.monotonic() - self.last_request_at)
        if wait > 0:
            time.sleep(wait)
        response = self.session.get(url, params=params, timeout=(10, 30))
        self.last_request_at = time.monotonic()
        response.raise_for_status()
        return response


def page_text(html: str, selector: str = "main") -> str:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.select("script, style, nav, footer, noscript"):
        node.decompose()
    root = soup.select_one(selector) or soup.body or soup
    return "\n".join(line.strip() for line in root.get_text("\n").splitlines() if line.strip())


def discover_links(html: str, base_url: str, link_selector: str, limit: int) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    found: list[str] = []
    for anchor in soup.select(link_selector):
        label = anchor.get_text(" ", strip=True)
        href = anchor.get("href")
        if not href or not any(word in label for word in GRANT_WORDS):
            continue
        url = urljoin(base_url, href).split("#", 1)[0]
        if urlparse(url).netloc == urlparse(base_url).netloc and url not in found:
            found.append(url)
        if len(found) >= limit:
            break
    return found


def load_existing(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    records = json.loads(path.read_text(encoding="utf-8"))
    return {item["source_url"]: item for item in records if item.get("source_url")}


def _iso_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value


def _yen(value: Any) -> str | None:
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return None
    return f"上限{amount:,}円" if amount > 0 else None


def collect_jgrants(session: PoliteSession, settings: dict[str, Any]) -> list[dict[str, Any]]:
    """デジタル庁Jグランツ公開APIから、現在募集中の全国案件を収集する。"""
    if not settings.get("enabled", True):
        return []

    keywords = settings.get("keywords", ["補助金", "助成金", "給付金", "支援金", "奨励金"])
    queries: list[dict[str, str]] = []
    # 主要語は都道府県別に検索し、少なくとも各地域の案件を拾う。
    primary = str(keywords[0])
    for prefecture in PREFECTURES:
        queries.append({"keyword": primary, "target_area_search": prefecture})
    # 表記が異なる制度は全国検索で補完する。
    queries.extend({"keyword": str(keyword)} for keyword in keywords[1:])

    by_id: dict[str, dict[str, Any]] = {}
    common = {"sort": "created_date", "order": "DESC", "acceptance": "1"}
    for query in queries:
        try:
            response = session.get_api(JGRANTS_API, params={**common, **query})
            for item in response.json().get("result", []):
                if item.get("id"):
                    by_id[item["id"]] = item
        except Exception as exc:
            logging.error("JグランツAPI取得失敗 %s: %s", query, exc)

    today = date.today().isoformat()
    records: list[dict[str, Any]] = []
    for item in by_id.values():
        area = item.get("target_area_search") or "全国"
        prefectures = [name for name in PREFECTURES if name in area]
        prefecture = prefectures[0] if len(prefectures) == 1 else "全国"
        employee = item.get("target_number_of_employees")
        target = "事業者" + (f"（{employee}）" if employee and employee != "従業員数の制約なし" else "")
        source_url = f"https://www.jgrants-portal.go.jp/subsidy/{item['id']}"
        records.append({
            "title": item.get("title") or item.get("institution_name") or "名称未設定",
            "target": target,
            "amount": _yen(item.get("subsidy_max_limit")),
            "deadline": _iso_date(item.get("acceptance_end_datetime")),
            "prefecture": prefecture,
            "city": "",
            "source_url": source_url,
            "updated_at": today,
        })
    logging.info("Jグランツから募集中案件を%d件取得", len(records))
    return records


def collect_personal_catalog(session: PoliteSession, catalog_path: Path) -> list[dict[str, Any]]:
    """国の公式ページで確認した個人向け制度を読み込み、URLの有効性を毎日確認する。"""
    if not catalog_path.exists():
        return []
    items = json.loads(catalog_path.read_text(encoding="utf-8"))
    today = date.today().isoformat()
    records: list[dict[str, Any]] = []
    for item in items:
        try:
            session.get(item["source_url"])
            item["updated_at"] = today
            records.append(item)
        except Exception as exc:
            logging.error("個人向け制度の公式ページ確認失敗 %s: %s", item.get("source_url"), exc)
    logging.info("個人向け公式制度を%d件確認", len(records))
    return records


def run(config_path: Path, output_path: Path, dry_run: bool = False) -> None:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    session = PoliteSession(float(config.get("request_interval_seconds", MIN_INTERVAL_SECONDS)))
    records = load_existing(output_path)

    for grant in collect_jgrants(session, config.get("jgrants", {})):
        records[grant["source_url"]] = grant

    personal_path = Path(config.get("personal_catalog", "data/personal_grants.json"))
    for grant in collect_personal_catalog(session, personal_path):
        records[grant["source_url"]] = grant

    for source in config.get("sources", []):
        try:
            listing = session.get(source["list_url"])
            urls = discover_links(
                listing.text,
                source["list_url"],
                source.get("link_selector", "main a"),
                int(source.get("max_pages", 20)),
            )
        except Exception as exc:
            logging.error("一覧取得失敗 %s: %s", source.get("list_url"), exc)
            continue

        for url in urls:
            try:
                detail = session.get(url)
                text = page_text(detail.text, source.get("content_selector", "main"))
                if dry_run:
                    logging.info("検出: %s (%d文字)", url, len(text))
                    continue
                grant = extract_grant(
                    text=text[:60_000],
                    prefecture=source["prefecture"],
                    city=source["city"],
                    source_url=url,
                    updated_at=date.today().isoformat(),
                )
                if grant:
                    records[url] = grant
                    logging.info("更新: %s", grant["title"])
            except Exception as exc:
                logging.error("詳細取得・抽出失敗 %s: %s", url, exc)

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        ordered = sorted(records.values(), key=lambda item: (item.get("prefecture") or "", item.get("city") or "", item.get("title") or ""))
        output_path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自治体公式サイトから助成制度を収集します")
    parser.add_argument("--config", type=Path, default=Path("sources.yml"))
    parser.add_argument("--output", type=Path, default=Path("data/grants.json"))
    parser.add_argument("--dry-run", action="store_true", help="LLMを呼ばず候補URLだけ確認")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run(args.config, args.output, args.dry_run)
