"""Resolve supported streaming-site pages to playable media URLs."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from PySide6.QtCore import QThread, Signal


SUPPORTED_DOMAINS = (
    "youtube.com",
    "youtu.be",
    "twitch.tv",
    "rumble.com",
    "kick.com",
    "vimeo.com",
    "dailymotion.com",
    "odysee.com",
)


def _select_playable_stream(
    info: dict[str, Any], max_video_height: int | None = None
) -> dict[str, Any]:
    formats = info.get("requested_formats") or []
    if max_video_height and info.get("is_live"):
        available = info.get("formats") or []
        video_formats = [
            item
            for item in available
            if isinstance(item, dict)
            and item.get("url")
            and item.get("vcodec") != "none"
            and isinstance(item.get("height"), (int, float))
            and item["height"] <= max_video_height
        ]
        video = max(
            video_formats,
            key=lambda item: (
                item.get("height") or 0,
                item.get("tbr") or 0,
            ),
            default=None,
        )
        audio_formats = [
            item
            for item in available
            if isinstance(item, dict)
            and item.get("url")
            and item.get("vcodec") == "none"
            and item.get("acodec") != "none"
        ]
        audio = max(
            audio_formats,
            key=lambda item: (
                item.get("abr") or 0,
                item.get("tbr") or 0,
                item.get("source_preference") or 0,
            ),
            default=None,
        )
        if video and audio:
            return {
                "url": video["url"],
                "audio_url": audio["url"],
                "headers": video.get("http_headers")
                or info.get("http_headers")
                or {},
            }

    url = info.get("url")
    if isinstance(url, str) and url:
        return {
            "url": url,
            "audio_url": None,
            "headers": info.get("http_headers") or {},
        }

    video = next(
        (
            item
            for item in formats
            if isinstance(item, dict)
            and item.get("url")
            and item.get("vcodec") != "none"
        ),
        None,
    )
    audio = next(
        (
            item
            for item in formats
            if isinstance(item, dict)
            and item.get("url")
            and item.get("acodec") != "none"
        ),
        None,
    )
    if video and audio:
        return {
            "url": video["url"],
            "audio_url": audio["url"],
            "headers": video.get("http_headers")
            or info.get("http_headers")
            or {},
        }
    raise ValueError("Serwis nie zwrócił odtwarzalnego strumienia.")


def requires_resolution(url: str) -> bool:
    try:
        host = (urlsplit(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return False
    return any(
        host == domain or host.endswith("." + domain)
        for domain in SUPPORTED_DOMAINS
    )


def _is_youtube_url(url: str) -> bool:
    try:
        host = (urlsplit(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return False
    return host == "youtu.be" or host == "youtube.com" or host.endswith(
        ".youtube.com"
    )


class StreamResolver(QThread):
    resolved = Signal(int, object)
    failed = Signal(int, str)

    def __init__(self, request_id: int, url: str, parent=None):
        super().__init__(parent)
        self._request_id = request_id
        self._url = url

    def run(self):
        try:
            import yt_dlp

            options = {
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "format": (
                    "best[acodec!=none][vcodec!=none]/"
                    "bestvideo*+bestaudio/best"
                ),
                "socket_timeout": 20,
            }
            with yt_dlp.YoutubeDL(options) as extractor:
                info = extractor.extract_info(self._url, download=False)
            if self.isInterruptionRequested():
                return
            if not isinstance(info, dict):
                raise ValueError("Serwis nie zwrócił odtwarzalnego strumienia.")
            max_video_height = (
                720 if _is_youtube_url(self._url) and info.get("is_live") else None
            )
            self.resolved.emit(
                self._request_id,
                _select_playable_stream(info, max_video_height),
            )
        except Exception as exc:
            if not self.isInterruptionRequested():
                self.failed.emit(self._request_id, str(exc))
