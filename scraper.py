from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import date
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


def run(config_path: Path, output_path: Path, dry_run: bool = False) -> None:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    session = PoliteSession(float(config.get("request_interval_seconds", MIN_INTERVAL_SECONDS)))
    records = load_existing(output_path)

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
