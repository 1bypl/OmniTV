"""Pobieranie i lokalny cache publicznej bazy kanałów z iptv-org.

Dane pochodzą z https://github.com/iptv-org/api (publicznie dostępne strumienie).
Pobieramy je raz i zapisujemy w katalogu danych użytkownika, żeby nie ściągać
kilku megabajtów przy każdym uruchomieniu.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

import requests

from omnity.i18n import tr

API_BASE = "https://iptv-org.github.io/api"
HTTP_TIMEOUT = 30

# (nazwa pliku w API, nazwa atrybutu w klasie Catalog)
DATASETS = (
    ("channels.json", "channels"),
    ("categories.json", "categories"),
    ("countries.json", "countries"),
    ("logos.json", "logos"),
    ("streams.json", "streams"),
    ("blocklist.json", "blocklist"),
)


class CatalogError(RuntimeError):
    """Błąd pobierania lub parsowania bazy kanałów."""


def data_dir() -> str:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(base, "omnity")
    os.makedirs(path, exist_ok=True)
    return path


def cache_dir() -> str:
    path = os.path.join(data_dir(), "cache")
    os.makedirs(path, exist_ok=True)
    return path


def _download(name: str, should_stop=None):
    url = f"{API_BASE}/{name}"
    try:
        with requests.get(url, timeout=HTTP_TIMEOUT, stream=True) as response:
            response.raise_for_status()
            chunks = []
            for chunk in response.iter_content(chunk_size=1 << 16):
                if should_stop is not None and should_stop():
                    raise CatalogError(tr("download_cancelled"))
                if chunk:
                    chunks.append(chunk)
        return json.loads(b"".join(chunks))
    except CatalogError:
        raise
    except (requests.RequestException, ValueError) as exc:
        raise CatalogError(
            tr("download_failed", name=name, error=exc)
        ) from exc


def load_dataset(name: str, force: bool = False, should_stop=None):
    """Zwraca dane z cache albo pobiera je z API. Zapis jest atomowy."""
    if should_stop is not None and should_stop():
        raise CatalogError(tr("download_stopped"))

    path = os.path.join(cache_dir(), name)
    if not force and os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, ValueError):
            pass

    data = _download(name, should_stop=should_stop)

    file_descriptor, tmp_path = tempfile.mkstemp(
        dir=cache_dir(), prefix=name, suffix=".tmp"
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        os.replace(tmp_path, path)
    except OSError:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
    return data


class Catalog:
    """Indeks kanałów, kategorii, krajów i strumieni."""

    def __init__(self):
        self.channels = []
        self.categories = []
        self.countries = []
        self.logos = []
        self.streams = []
        self.blocklist = []

        self.country_by_code = {}
        self.category_by_id = {}
        self.streams_by_channel = {}
        self.logo_by_channel = {}
        self._blocked = set()
        self._playable = None

    def load(self, force: bool = False, progress=None, should_stop=None):
        for filename, attribute in DATASETS:
            if progress:
                progress(tr("progress_downloading", name=filename))
            setattr(
                self,
                attribute,
                load_dataset(filename, force=force, should_stop=should_stop),
            )
        self._build_indexes()
        if progress:
            progress(tr("progress_done"))

    def _build_indexes(self):
        self.country_by_code = {
            country["code"]: country
            for country in self.countries
            if country.get("code")
        }
        self.category_by_id = {
            category["id"]: category
            for category in self.categories
            if category.get("id")
        }

        self.streams_by_channel = {}
        for stream in self.streams:
            channel_id = stream.get("channel")
            if channel_id:
                self.streams_by_channel.setdefault(channel_id, []).append(stream)

        self._blocked = {
            entry.get("channel") for entry in self.blocklist if entry.get("channel")
        }

        # Najlepsze logo dla każdego kanału (preferuj: używane, rastrowe, wystarczająco duże).
        best = {}
        for logo in self.logos:
            channel_id = logo.get("channel")
            url = logo.get("url")
            if not channel_id or not url:
                continue
            fmt = (logo.get("format") or "").upper()
            width = logo.get("width") or 0
            score = (
                0 if logo.get("in_use") else 1,
                0 if fmt in ("PNG", "WEBP", "JPEG") else (1 if fmt == "SVG" else 2),
                0 if width >= 64 else 1,
                abs(width - 256),
            )
            if channel_id not in best or score < best[channel_id][0]:
                best[channel_id] = (score, url)
        self.logo_by_channel = {
            channel_id: value[1] for channel_id, value in best.items()
        }

        self._playable = None

    def playable_channels(self):
        """Kanały, które da się odtworzyć: aktywne, nie-NSFW, nie zablokowane, z transmisją."""
        if self._playable is not None:
            return self._playable

        result = []
        for channel in self.channels:
            channel_id = channel.get("id")
            if not channel_id:
                continue
            if channel.get("closed") or channel.get("is_nsfw"):
                continue
            if channel_id in self._blocked:
                continue
            if channel_id not in self.streams_by_channel:
                continue
            result.append(channel)

        result.sort(key=lambda channel: channel.get("name", "").lower())
        self._playable = result
        return result

    def best_stream(self, channel_id: str):
        """Najlepszy strumień kanału: preferuj pełnodobowe i nie geoblokowane."""
        streams = self.streams_by_channel.get(channel_id, [])
        if not streams:
            return None

        def rank(stream):
            labels = stream.get("labels") or []
            geo_blocked = 1 if "Geo-blocked" in labels else 0
            not_24_7 = 1 if "Not 24/7" in labels else 0
            return (geo_blocked, not_24_7)

        return sorted(streams, key=rank)[0]

    def logo_url(self, channel_id: str) -> str | None:
        return self.logo_by_channel.get(channel_id)

    def country_flag(self, code: str) -> str:
        country = self.country_by_code.get(code or "")
        flag = country.get("flag", "") if country else ""
        if flag:
            return flag
        if len(code or "") == 2 and code.isascii() and code.isalpha():
            return "".join(chr(ord(char.upper()) + 127397) for char in code)
        return ""

    def country_name(self, code: str) -> str:
        country = self.country_by_code.get(code or "")
        if country:
            return country.get("name", code or "")
        return code or ""
