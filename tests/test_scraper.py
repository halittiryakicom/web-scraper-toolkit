from unittest.mock import patch

from core.http_client import FetchResult
from core.parser import SelectorType
from core.scraper import PageResult, ScraperEngine, ScrapeReport

SAMPLE_HTML = "<html><body><h2 class='title'>Hello</h2><h2 class='title'>World</h2></body></html>"


class FakeHttpClient:
    """A stand-in HttpClient that returns canned responses instead of hitting the network."""

    def __init__(self, responses: dict[str, FetchResult]):
        self.responses = responses
        self.user_agent = "FakeBot/1.0"

    def fetch(self, url: str) -> FetchResult:
        return self.responses[url]


def _allow_all_robots():
    """robots.txt lookups go over the network too; always-allow for these tests."""
    return patch("core.scraper._is_allowed_by_robots", return_value=True)


def test_scrape_url_returns_extracted_values():
    client = FakeHttpClient({"https://a.test": FetchResult("https://a.test", True, 200, SAMPLE_HTML)})
    engine = ScraperEngine(client=client)

    with _allow_all_robots():
        result = engine.scrape_url("https://a.test", "h2.title", SelectorType.CSS)

    assert result.success is True
    assert result.values == ["Hello", "World"]


def test_scrape_url_reports_fetch_failure():
    client = FakeHttpClient({"https://a.test": FetchResult("https://a.test", False, error="timed out")})
    engine = ScraperEngine(client=client)

    with _allow_all_robots():
        result = engine.scrape_url("https://a.test", "h2.title", SelectorType.CSS)

    assert result.success is False
    assert "timed out" in result.error


def test_scrape_url_reports_bad_selector_without_crashing():
    client = FakeHttpClient({"https://a.test": FetchResult("https://a.test", True, 200, SAMPLE_HTML)})
    engine = ScraperEngine(client=client)

    with _allow_all_robots():
        result = engine.scrape_url("https://a.test", ":::bad:::", SelectorType.CSS)

    assert result.success is False
    assert result.error


def test_scrape_url_skips_when_disallowed_by_robots():
    client = FakeHttpClient({})
    engine = ScraperEngine(client=client)

    with patch("core.scraper._is_allowed_by_robots", return_value=False):
        result = engine.scrape_url("https://a.test", "h2.title", SelectorType.CSS)

    assert result.success is False
    assert result.skipped_by_robots is True


def test_robots_txt_unreachable_is_treated_as_allowed():
    """A host that's merely unreachable for robots.txt must not be silently skipped."""
    from unittest.mock import patch as _patch

    import core.scraper as scraper_module

    scraper_module._robots_cache.clear()
    with _patch("core.scraper.RobotFileParser.read", side_effect=OSError("dns failure")):
        assert scraper_module._is_allowed_by_robots("https://unreachable.test/page", "TestBot/1.0") is True


def test_scrape_many_continues_after_one_bad_url():
    client = FakeHttpClient({
        "https://a.test": FetchResult("https://a.test", True, 200, SAMPLE_HTML),
        "https://b.test": FetchResult("https://b.test", False, error="404"),
        "https://c.test": FetchResult("https://c.test", True, 200, SAMPLE_HTML),
    })
    engine = ScraperEngine(client=client)
    progress = []

    with _allow_all_robots():
        report = engine.scrape_many(
            ["https://a.test", "https://b.test", "https://c.test"],
            "h2.title",
            SelectorType.CSS,
            on_progress=lambda done, total, url: progress.append((done, total)),
        )

    assert (report.succeeded, report.failed) == (2, 1)
    assert report.total_values == 4
    assert progress[0] == (0, 3) and progress[-1] == (3, 3)


def test_report_to_rows_tags_each_value_with_its_source_url():
    report = ScrapeReport()
    report.results.append(PageResult(url="https://a.test", success=True, values=["Hello", "World"]))

    rows = report.to_rows()

    assert rows == [
        {"Source URL": "https://a.test", "Value": "Hello"},
        {"Source URL": "https://a.test", "Value": "World"},
    ]
