"""Tłumaczenie napisów kanału na język interfejsu.

Tekst napisów pochodzi z odtwarzacza (WebVTT/wbudowana ścieżka napisów).
Tłumaczenie jest wysyłane do publicznego endpointu Google; w razie błędu
próbujemy awaryjnie MyMemory. Wysyłany jest wyłącznie tekst napisów.
"""

from __future__ import annotations

import html
import json

from PySide6.QtCore import QObject, QTimer, QUrl, QUrlQuery, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

GOOGLE_URL = "https://translate.googleapis.com/translate_a/single"
MYMEMORY_URL = "https://api.mymemory.translated.net/get"
USER_AGENT = "Mozilla/5.0 (OmniTV)"
MAX_TEXT_LENGTH = 1000


class SubtitleTranslator(QObject):
    translated = Signal(int, str)
    failed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._manager = QNetworkAccessManager(self)
        self._cache: dict[tuple[str, str], str] = {}
        self._sequence = 0

    def translate(self, text: str, language: str) -> int:
        text = (text or "").strip()
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]
        self._sequence += 1
        sequence = self._sequence
        if not text:
            self.failed.emit(sequence)
            return sequence

        cached = self._cache.get((language, text))
        if cached is not None:
            QTimer.singleShot(
                0, lambda s=sequence, t=cached: self.translated.emit(s, t)
            )
            return sequence

        url = QUrl(GOOGLE_URL)
        query = QUrlQuery()
        query.addQueryItem("client", "gtx")
        query.addQueryItem("sl", "auto")
        query.addQueryItem("tl", language)
        query.addQueryItem("dt", "t")
        query.addQueryItem("q", text)
        url.setQuery(query)
        self._request(url, sequence, language, text, fallback=True)
        return sequence

    def _request(
        self,
        url: QUrl,
        sequence: int,
        language: str,
        text: str,
        fallback: bool,
    ):
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.UserAgentHeader, USER_AGENT)
        try:
            request.setTransferTimeout(10000)
        except AttributeError:
            pass
        reply = self._manager.get(request)
        reply.finished.connect(
            lambda r=reply, s=sequence, lang=language, src=text, fb=fallback: self._finish(
                r, s, lang, src, fb
            )
        )

    def _finish(
        self,
        reply: QNetworkReply,
        sequence: int,
        language: str,
        text: str,
        fallback: bool,
    ):
        try:
            status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            raw = bytes(reply.readAll()).decode("utf-8", errors="replace")
        finally:
            reply.deleteLater()

        translated = None
        if status == 200:
            translated = self._parse_google(raw) or self._parse_mymemory(raw)
        if translated:
            self._store(sequence, language, text, translated)
        elif fallback:
            self._request(
                self._mymemory_url(language, text),
                sequence,
                language,
                text,
                fallback=False,
            )
        else:
            self.failed.emit(sequence)

    def _mymemory_url(self, language: str, text: str) -> QUrl:
        url = QUrl(MYMEMORY_URL)
        query = QUrlQuery()
        query.addQueryItem("q", text)
        query.addQueryItem("langpair", f"Autodetect|{language}")
        url.setQuery(query)
        return url

    @staticmethod
    def _parse_google(raw: str) -> str | None:
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError):
            return None
        if not isinstance(payload, list) or not payload:
            return None
        segments = payload[0]
        if isinstance(segments, str):
            return html.unescape(segments)
        if not isinstance(segments, list):
            return None
        translated = "".join(
            segment[0]
            for segment in segments
            if isinstance(segment, list)
            and segment
            and isinstance(segment[0], str)
        )
        return html.unescape(translated) if translated else None

    @staticmethod
    def _parse_mymemory(raw: str) -> str | None:
        try:
            payload = json.loads(raw)
            translated = payload["responseData"]["translatedText"]
        except (KeyError, TypeError, ValueError):
            return None
        if not isinstance(translated, str):
            return None
        return html.unescape(translated)

    def _store(self, sequence: int, language: str, text: str, translated: str):
        self._cache[(language, text)] = translated
        if len(self._cache) > 1000:
            self._cache.pop(next(iter(self._cache)))
        self.translated.emit(sequence, translated)
