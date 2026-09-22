"""Ties fetching and parsing together, and runs them over one or many URLs."""

from dataclasses import dataclass, field
from typing import Callable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from core.http_client import HttpClient
from core.parser import SelectorError, SelectorType, extract

ProgressCallback = Callable[[int, int, str], None]


@dataclass
class PageResult:
    """Outcome of scraping a single URL."""

    url: str
    success: bool
    values: list[str] = field(default_factory=list)
    error: str = ""
    skipped_by_robots: bool = False


@dataclass
class ScrapeReport:
    """Combined results for a batch of URLs, plus a running summary."""

    results: list[PageResult] = field(default_factory=list)

    @property
    def succeeded(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failed(self) -> int:
        return len(self.results) - self.succeeded

    @property
    def total_values(self) -> int:
        return sum(len(r.values) for r in self.results)

    def to_rows(self) -> list[dict]:
        """Flatten every extracted value into one row per value, tagged with its source URL."""
        rows = []
        for result in self.results:
            if not result.success:
                continue
            for value in result.values:
                rows.append({"Source URL": result.url, "Value": value})
        return rows


_robots_cache: dict[str, RobotFileParser] = {}


def _is_allowed_by_robots(url: str, user_agent: str) -> bool:
    """Check robots.txt for ``url``'s host, caching one parser per host per run."""
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    parser = _robots_cache.get(origin)
    if parser is None:
        parser = RobotFileParser()
        parser.set_url(f"{origin}/robots.txt")
        try:
            parser.read()
        except Exception:
            # Could not fetch robots.txt at all (DNS failure, connection
            # refused, ...). RobotFileParser's own default in that case is to
            # deny everything (can_fetch() falls through to "not checked yet
            # -> False"), which would silently skip every page on a merely
            # unreachable host. Treat "couldn't check" as "allowed" instead.
            parser.allow_all = True
        _robots_cache[origin] = parser

    try:
        return parser.can_fetch(user_agent, url)
    except Exception:
        return True


class ScraperEngine:
    """Scrapes one or more URLs with the same selector and collects the results."""

    def __init__(self, client: HttpClient | None = None, respect_robots_txt: bool = True) -> None:
        self.client = client or HttpClient()
        self.respect_robots_txt = respect_robots_txt

    def scrape_url(
        self,
        url: str,
        selector: str,
        selector_type: SelectorType = SelectorType.CSS,
        attribute: str | None = None,
    ) -> PageResult:
        """Scrape a single URL and return its result (never raises)."""
        url = url.strip()

        if self.respect_robots_txt and not _is_allowed_by_robots(url, self.client.user_agent):
            return PageResult(url=url, success=False, skipped_by_robots=True, error="Disallowed by robots.txt")

        fetch_result = self.client.fetch(url)
        if not fetch_result.success:
            return PageResult(url=url, success=False, error=fetch_result.error)

        try:
            values = extract(fetch_result.html, selector, selector_type, attribute)
        except SelectorError as error:
            return PageResult(url=url, success=False, error=str(error))

        return PageResult(url=url, success=True, values=values)

    def scrape_many(
        self,
        urls: list[str],
        selector: str,
        selector_type: SelectorType = SelectorType.CSS,
        attribute: str | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> ScrapeReport:
        """Scrape every URL in ``urls`` with the same selector; one bad URL never stops the batch."""
        cleaned_urls = [u.strip() for u in urls if u.strip()]
        report = ScrapeReport()

        for index, url in enumerate(cleaned_urls):
            if on_progress:
                on_progress(index, len(cleaned_urls), url)
            report.results.append(self.scrape_url(url, selector, selector_type, attribute))

        if on_progress:
            on_progress(len(cleaned_urls), len(cleaned_urls), cleaned_urls[-1] if cleaned_urls else "")

        return report
