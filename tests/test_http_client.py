from unittest.mock import Mock, patch

import requests

from core.http_client import HttpClient


def _response(status_code=200, text="<html></html>"):
    response = Mock()
    response.status_code = status_code
    response.text = text
    response.raise_for_status = Mock()
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(f"{status_code}")
    return response


@patch("core.http_client.requests.get")
def test_fetch_succeeds_on_first_try(mock_get):
    mock_get.return_value = _response(200, "<p>ok</p>")

    result = HttpClient(max_retries=2).fetch("https://example.com")

    assert result.success is True
    assert result.status_code == 200
    assert result.html == "<p>ok</p>"
    assert result.attempts == 1
    mock_get.assert_called_once()


@patch("core.http_client.requests.get")
def test_fetch_sends_the_configured_user_agent(mock_get):
    mock_get.return_value = _response(200)

    HttpClient(user_agent="MyBot/1.0", max_retries=0).fetch("https://example.com")

    _, kwargs = mock_get.call_args
    assert kwargs["headers"]["User-Agent"] == "MyBot/1.0"


@patch("core.http_client.sleep", return_value=None)
@patch("core.http_client.requests.get")
def test_fetch_retries_on_server_error_then_succeeds(mock_get, _mock_sleep):
    mock_get.side_effect = [_response(503), _response(200, "<p>ok</p>")]

    result = HttpClient(max_retries=2).fetch("https://example.com")

    assert result.success is True
    assert result.attempts == 2
    assert mock_get.call_count == 2


@patch("core.http_client.sleep", return_value=None)
@patch("core.http_client.requests.get")
def test_fetch_gives_up_after_max_retries(mock_get, _mock_sleep):
    mock_get.side_effect = requests.exceptions.ConnectionError("boom")

    result = HttpClient(max_retries=2).fetch("https://example.com")

    assert result.success is False
    assert result.attempts == 3
    assert "boom" in result.error


@patch("core.http_client.requests.get")
def test_fetch_reports_client_errors_without_retrying(mock_get):
    mock_get.return_value = _response(404)

    result = HttpClient(max_retries=2).fetch("https://example.com/missing")

    assert result.success is False
    assert mock_get.call_count == 1
