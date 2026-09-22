"""Fetches pages over HTTP with a configurable User-Agent, timeout and retries."""

from dataclasses import dataclass
from time import sleep

import requests

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "WebScraperToolkit/1.0 (+https://github.com/halittiryakicom/web-scraper-toolkit)"
)


@dataclass
class FetchResult:
    """Outcome of fetching a single URL."""

    url: str
    success: bool
    status_code: int | None = None
    html: str = ""
    error: str = ""
    attempts: int = 0


class HttpClient:
    """Thin wrapper around ``requests`` with retry and timeout handling."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = 15.0,
        max_retries: int = 2,
        retry_backoff: float = 1.5,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

    def fetch(self, url: str) -> FetchResult:
        """Fetch ``url``, retrying connection failures and 5xx responses.

        4xx responses are never retried (the request itself is fine, retrying
        a 404 or 403 just wastes time), only connection errors, timeouts and
        server errors are.
        """
        headers = {"User-Agent": self.user_agent}
        last_error = ""
        attempts = 0

        for attempt in range(self.max_retries + 1):
            attempts = attempt + 1
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
            except requests.exceptions.RequestException as error:
                last_error = str(error)
                if attempt < self.max_retries:
                    sleep(self.retry_backoff * attempts)
                continue

            if response.status_code >= 500 and attempt < self.max_retries:
                last_error = f"HTTP {response.status_code}"
                sleep(self.retry_backoff * attempts)
                continue

            if response.status_code >= 400:
                return FetchResult(
                    url=url,
                    success=False,
                    status_code=response.status_code,
                    error=f"HTTP {response.status_code}",
                    attempts=attempts,
                )

            return FetchResult(
                url=url,
                success=True,
                status_code=response.status_code,
                html=response.text,
                attempts=attempts,
            )

        return FetchResult(url=url, success=False, error=last_error, attempts=attempts)
