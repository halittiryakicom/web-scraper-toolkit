# Changelog

All notable changes to this project are documented in this file.

## [0.5.0] - 2026-09-22

### Added

- Core scraping engine (`core/http_client.py`, `core/parser.py`, `core/scraper.py`):
  fetch with a configurable User-Agent/timeout, automatic retries on
  connection errors and 5xx responses, CSS selector and XPath extraction
  (including attribute extraction), robots.txt awareness, and batch
  scraping of multiple URLs where one bad URL never stops the run.
- Export to CSV, Excel and JSON (`services/export_service.py`).
- PySide6 desktop interface (`gui/main_window.py`) with a URL box,
  selector options, output/format selection, a progress bar and a log
  panel.
- PyInstaller build spec (`app.spec`) for a standalone Windows `.exe`.
- 25 pytest unit tests covering the parser, HTTP client (retry logic) and
  the scraper engine (batch handling, robots.txt).

## [0.1.0] - 2026-07-15

### Added

- Initial project structure, README, MIT license, `.gitignore` and
  `requirements.txt`.
