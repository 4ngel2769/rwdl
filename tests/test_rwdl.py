import os
import pytest
import requests
from rwdl import normalize_url, is_valid_extension, parse_directory, download_file

class DummyResponse:
    def __init__(self, text=None, content=None, status_code=200):
        self.text = text
        self._content = content or b""
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size=8192):
        for i in range(0, len(self._content), chunk_size):
            yield self._content[i : i + chunk_size]


def test_normalize_url():
    assert normalize_url("http://google.com") == "http://google.com/"
    assert normalize_url("http://google.com/") == "http://google.com/"


def test_is_valid_extension():
    exts = [".txt", ".md"]
    assert is_valid_extension("readme.md", exts)
    assert not is_valid_extension("image.png", exts)


def test_parse_directory_filters_links(monkeypatch):
    html = """
    <html><body>
      <a href="../">up</a>
      <a href="./">self</a>
      <a href="?query">q</a>
      <a href="file.txt">file</a>
      <a href="folder/">folder</a>
      <a href="mailto:test@example.com">mail</a>
    </body></html>
    """
    # dummy simulation of file download
    def mock_get(url, headers, timeout):
        return DummyResponse(text=html)

    monkeypatch.setattr(requests, "get", mock_get)
    links = parse_directory("http://example.com/")
    assert "file.txt" in links
    assert "folder/" in links
    assert "../" not in links
    assert "./" not in links
    assert "?query" not in links
    assert "mailto:test@example.com" not in links


def test_download_file_success(monkeypatch, tmp_path):
    data = b"hello world"

    def mock_get(url, headers, stream, timeout):
        return DummyResponse(content=data)

    monkeypatch.setattr(requests, "get", mock_get)
    out_file = tmp_path / "out.bin"
    result = download_file("http://example.com/out.bin", str(out_file))
    assert result is True
    assert out_file.read_bytes() == data


def test_download_file_failure(monkeypatch, tmp_path, capsys):
    def mock_get(url, headers, stream, timeout):
        return DummyResponse(status_code=404)

    monkeypatch.setattr(requests, "get", mock_get)
    out_file = tmp_path / "fail.bin"
    result = download_file("http://example.com/fail.bin", str(out_file))
    captured = capsys.readouterr()
    assert result is False
    assert "Download failed" in captured.out
