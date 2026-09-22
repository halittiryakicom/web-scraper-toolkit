import pytest

from core.parser import SelectorError, SelectorType, extract

SAMPLE_HTML = """
<html><body>
  <h2 class="title">First Post</h2>
  <h2 class="title">Second Post &amp; More</h2>
  <a href="/one" class="link">One</a>
  <a href="https://example.com/two" class="link">Two</a>
  <p></p>
</body></html>
"""


def test_css_selector_extracts_text_in_document_order():
    assert extract(SAMPLE_HTML, "h2.title", SelectorType.CSS) == [
        "First Post",
        "Second Post & More",
    ]


def test_css_selector_extracts_an_attribute():
    assert extract(SAMPLE_HTML, "a.link", SelectorType.CSS, attribute="href") == [
        "/one",
        "https://example.com/two",
    ]


def test_xpath_extracts_text():
    assert extract(SAMPLE_HTML, "//h2[@class='title']", SelectorType.XPATH) == [
        "First Post",
        "Second Post & More",
    ]


def test_xpath_can_select_attribute_values_directly():
    assert extract(SAMPLE_HTML, "//a/@href", SelectorType.XPATH) == [
        "/one",
        "https://example.com/two",
    ]


def test_empty_matches_are_dropped():
    assert extract(SAMPLE_HTML, "p", SelectorType.CSS) == []


def test_no_matches_returns_empty_list():
    assert extract(SAMPLE_HTML, ".does-not-exist", SelectorType.CSS) == []


def test_blank_selector_raises():
    with pytest.raises(SelectorError):
        extract(SAMPLE_HTML, "   ", SelectorType.CSS)


def test_invalid_css_selector_raises():
    with pytest.raises(SelectorError):
        extract(SAMPLE_HTML, ":::not-a-selector", SelectorType.CSS)


def test_invalid_xpath_raises():
    with pytest.raises(SelectorError):
        extract(SAMPLE_HTML, "///[[[", SelectorType.XPATH)
