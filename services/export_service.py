"""Exports a scrape report's rows to CSV, Excel or JSON."""

from pathlib import Path

import pandas as pd

from core.scraper import ScrapeReport


class ExportError(RuntimeError):
    """Raised when there is nothing to export or the target path can't be written."""


def _rows_or_raise(report: ScrapeReport) -> list[dict]:
    rows = report.to_rows()
    if not rows:
        raise ExportError("There is nothing to export - no values were extracted.")
    return rows


def export_csv(report: ScrapeReport, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(_rows_or_raise(report)).to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def export_excel(report: ScrapeReport, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(_rows_or_raise(report)).to_excel(output_path, index=False, engine="openpyxl")
    return output_path


def export_json(report: ScrapeReport, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(_rows_or_raise(report)).to_json(output_path, orient="records", indent=2, force_ascii=False)
    return output_path


EXPORTERS = {
    "csv": export_csv,
    "excel": export_excel,
    "json": export_json,
}
