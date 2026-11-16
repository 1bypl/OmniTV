"""Best-effort EPG: pobieranie i parsowanie przewodników XMLTV.

Nie każdy kanał ma dostępny program TV, a identyfikatory kanałów w XMLTV bywają
różne od tych z iptv-org. Dopasowujemy więc po znormalizowanej nazwie kanału.
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from datetime import datetime, timezone
from io import BytesIO
from xml.etree import ElementTree as ET

import requests

from omnity.core.catalog import cache_dir

CACHE_TTL = 12 * 3600
HTTP_TIMEOUT = 25
PLUTO_EPG_BASE = "https://i.mjh.nz/PlutoTV"


def sources_for_channel(channel_id: str, country: str | None = None) -> list[str]:
    """Publiczne feedy XMLTV dla znanych dostawców.

    iptv-org nie publikuje już adresów przewodników w guides.json, więc dla
    kanałów Pluto TV korzystamy z publicznych feedów i.mjh.nz (per region).
    """
    if not channel_id:
        return []

    region = channel_id.rsplit(".", 1)[-1].lower() if "." in channel_id else ""
    if not region and country:
        region = country.lower()

    if channel_id.startswith("PlutoTV") and region:
        return [f"{PLUTO_EPG_BASE}/{region}.xml"]
    return []


def _epg_cache_dir() -> str:
    path = os.path.join(cache_dir(), "epg")
    os.makedirs(path, exist_ok=True)
    return path


def fetch_xmltv(url: str) -> bytes:
    path = os.path.join(
        _epg_cache_dir(), hashlib.sha1(url.encode()).hexdigest() + ".xml"
    )
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < CACHE_TTL:
        with open(path, "rb") as handle:
            return handle.read()

    response = requests.get(url, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    data = response.content
    try:
        with open(path, "wb") as handle:
            handle.write(data)
    except OSError:
        pass
    return data


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def _parse_time(value: str | None):
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y%m%d%H%M%S %z", "%Y%m%d%H%M%S"):
        try:
            moment = datetime.strptime(value, fmt)
        except ValueError:
            continue
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return moment.timestamp()
    return None


def find_programmes(xml_bytes: bytes, channel_name: str, count: int = 6):
    """Zwraca bieżący i najbliższe programy: dicts z title, desc, start_ts, stop_ts."""
    target = _normalize(channel_name)
    if not target:
        return []

    names_by_id: dict[str, list[str]] = {}
    programmes = []
    try:
        for _, element in ET.iterparse(BytesIO(xml_bytes), events=("end",)):
            if element.tag == "channel":
                channel_id = element.get("id")
                if channel_id:
                    names = [
                        _normalize(display.text)
                        for display in element.findall("display-name")
                        if display.text
                    ]
                    if names:
                        names_by_id[channel_id] = names
                element.clear()
            elif element.tag == "programme":
                channel_id = element.get("channel")
                title = (element.findtext("title") or "").strip()
                start = _parse_time(element.get("start"))
                stop = _parse_time(element.get("stop"))
                desc = (element.findtext("desc") or "").strip()
                if channel_id and title and start is not None:
                    programmes.append((channel_id, start, stop, title, desc))
                element.clear()
    except ET.ParseError:
        return []

    matched = None
    for channel_id, names in names_by_id.items():
        if target in names:
            matched = channel_id
            break
    if matched is None:
        for channel_id, names in names_by_id.items():
            if any(target in name or name in target for name in names if name):
                matched = channel_id
                break
    if matched is None:
        for channel_id in names_by_id:
            normalized_id = _normalize(channel_id)
            if normalized_id and (target in normalized_id or normalized_id in target):
                matched = channel_id
                break
    if matched is None:
        return []

    now = time.time()
    candidates = [
        (start, stop, title, desc)
        for channel_id, start, stop, title, desc in programmes
        if channel_id == matched
    ]
    candidates.sort(key=lambda item: item[0])

    result = []
    for start, stop, title, desc in candidates:
        if stop is not None and stop < now:
            continue
        result.append(
            {"title": title, "desc": desc, "start_ts": start, "stop_ts": stop}
        )
        if len(result) >= count:
            break
    return result
