"""Extracts data from HTML using either a CSS selector or an XPath expression."""

from enum import Enum

from lxml import html as lxml_html
from lxml.etree import XPathEvalError


class SelectorType(str, Enum):
    CSS = "css"
    XPATH = "xpath"


class SelectorError(ValueError):
    """Raised when a selector is malformed or matches nothing usable."""


def extract(
    html: str,
    selector: str,
    selector_type: SelectorType = SelectorType.CSS,
    attribute: str | None = None,
) -> list[str]:
    """Return the text (or a named attribute) of every element matching ``selector``.

    Args:
        html: Raw HTML of the page.
        selector: A CSS selector (e.g. ``h2.title``) or an XPath expression
            (e.g. ``//h2[@class='title']``).
        selector_type: Whether ``selector`` is CSS or XPath.
        attribute: When set, the named attribute's value is returned instead
            of the element's text (e.g. ``href`` to collect link targets).

    Returns:
        The matched values, in document order, with surrounding whitespace
        stripped and empty results dropped.
    """
    if not selector.strip():
        raise SelectorError("Selector cannot be empty.")

    try:
        tree = lxml_html.fromstring(html)
    except Exception as error:  # lxml raises plain Exception/ParserError on bad markup
        raise SelectorError(f"Could not parse the page as HTML: {error}") from error

    try:
        if selector_type == SelectorType.CSS:
            elements = tree.cssselect(selector)
        else:
            result = tree.xpath(selector)
            # An XPath expression can select elements, or directly select
            # strings/attribute values (e.g. "//a/@href") - handle both.
            if result and isinstance(result[0], str):
                return [value.strip() for value in result if value and value.strip()]
            elements = result
    except XPathEvalError as error:
        raise SelectorError(f"Invalid XPath expression: {error}") from error
    except Exception as error:  # invalid CSS selector syntax from cssselect
        raise SelectorError(f"Invalid CSS selector: {error}") from error

    values: list[str] = []
    for element in elements:
        if not hasattr(element, "get"):
            # xpath() can return non-element nodes (e.g. comments); skip them.
            continue
        raw = element.get(attribute) if attribute else element.text_content()
        if raw and raw.strip():
            values.append(raw.strip())
    return values
