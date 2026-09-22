import json

import pandas as pd
import pytest

from core.scraper import PageResult, ScrapeReport
from services.export_service import ExportError, export_csv, export_excel, export_json


@pytest.fixture
def report():
    r = ScrapeReport()
    r.results.append(PageResult(url="https://a.test", success=True, values=["Alpha", "Béta"]))
    r.results.append(PageResult(url="https://b.test", success=False, error="404"))
    return r


def test_export_csv(tmp_path, report):
    path = export_csv(report, tmp_path / "out.csv")
    df = pd.read_csv(path)
    assert list(df["Value"]) == ["Alpha", "Béta"]
    assert list(df["Source URL"]) == ["https://a.test", "https://a.test"]


def test_export_excel(tmp_path, report):
    path = export_excel(report, tmp_path / "out.xlsx")
    df = pd.read_excel(path)
    assert list(df["Value"]) == ["Alpha", "Béta"]


def test_export_json(tmp_path, report):
    path = export_json(report, tmp_path / "out.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == [
        {"Source URL": "https://a.test", "Value": "Alpha"},
        {"Source URL": "https://a.test", "Value": "Béta"},
    ]


def test_export_raises_when_nothing_to_export(tmp_path):
    empty_report = ScrapeReport()
    with pytest.raises(ExportError):
        export_csv(empty_report, tmp_path / "out.csv")
