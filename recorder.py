"""Nagrywanie oryginalnego strumienia bez rekompresji (stream copy).

Domyślnie zapisujemy do AVI, a jeśli kontener nie obsługuje kodeków strumienia,
automatycznie ponawiamy do MKV. Pliki trafiają do ~/Wideo.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import time
import urllib.parse

import requests
from PySide6.QtCore import QObject, QProcess, Signal

from omnity.i18n import tr

DEFAULT_USER_AGENT = "Mozilla/5.0 (OmniTV)"


def video_dir() -> str:
    home = os.path.expanduser("~")
    for name in ("Wideo", "Videos", "wideo"):
        path = os.path.join(home, name)
        if os.path.isdir(path):
            return path
    path = os.path.join(home, "Wideo")
    os.makedirs(path, exist_ok=True)
    return path


def _safe_name(name: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", (name or "kanal").strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned[:80] or "kanal"


def _find_ffmpeg() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    roots = (exe_dir, os.path.join(exe_dir, "_internal"), source_dir, os.getcwd())
    for root in roots:
        for name in ("ffmpeg", "ffmpeg.exe"):
            candidate = os.path.join(root, name)
            if os.path.isfile(candidate):
                return candidate
    return None


def best_stream_url(
    url: str,
    referrer: str | None = None,
    user_agent: str | None = None,
    timeout: int = 6,
    headers: dict[str, str] | None = None,
) -> str:
    """Dla playlisty HLS zwraca wariant o największym BANDWIDTH."""
    if ".m3u8" not in urllib.parse.urlsplit(url).path.lower():
        return url
    request_headers = dict(headers or {})
    if referrer:
        request_headers["Referer"] = referrer
    request_headers["User-Agent"] = (
        user_agent
        or request_headers.get("User-Agent")
        or DEFAULT_USER_AGENT
    )
    try:
        response = requests.get(
            url,
            headers=request_headers,
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.RequestException:
        return url

    lines = response.text.splitlines()
    best_url = None
    best_bandwidth = -1
    for index, line in enumerate(lines):
        if not line.startswith("#EXT-X-STREAM-INF"):
            continue
        match = re.search(r"BANDWIDTH=(\d+)", line)
        bandwidth = int(match.group(1)) if match else 0
        for candidate in lines[index + 1 :]:
            candidate = candidate.strip()
            if not candidate or candidate.startswith("#"):
                continue
            if bandwidth > best_bandwidth:
                best_bandwidth = bandwidth
                best_url = urllib.parse.urljoin(response.url, candidate)
            break
    return best_url or url


class Recorder(QObject):
    started = Signal(str)
    stopped = Signal(str)
    failed = Signal(str)
    fallback = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process: QProcess | None = None
        self._path = ""
        self._url = ""
        self._audio_url = None
        self._referrer = None
        self._user_agent = None
        self._headers: dict[str, str] = {}
        self._buffer = ""
        self._stopping = False
        self._fallback_done = False
        self._started_at = 0.0

    @property
    def is_recording(self) -> bool:
        return self._process is not None

    def start(
        self,
        url: str,
        channel_name: str,
        referrer: str | None = None,
        user_agent: str | None = None,
        headers: dict[str, str] | None = None,
        audio_url: str | None = None,
    ) -> bool:
        if self._process is not None:
            return False
        ffmpeg = _find_ffmpeg()
        if not ffmpeg:
            self.failed.emit(tr("recording_unavailable"))
            return False

        self._url = best_stream_url(
            url, referrer, user_agent, headers=headers
        )
        self._audio_url = (
            best_stream_url(audio_url, referrer, user_agent, headers=headers)
            if audio_url
            else None
        )
        self._referrer = referrer
        self._user_agent = user_agent
        self._headers = dict(headers or {})
        self._stopping = False
        self._fallback_done = False
        self._started_at = time.monotonic()

        stamp = time.strftime("%Y%m%d_%H%M%S")
        base = f"{_safe_name(channel_name)}_{stamp}"
        self._path = os.path.join(video_dir(), base + ".avi")
        return self._start_process(ffmpeg, self._path)

    def _start_process(self, ffmpeg: str, path: str) -> bool:
        process = QProcess(self)
        process.setProcessChannelMode(QProcess.MergedChannels)
        args = ["-hide_banner", "-loglevel", "warning", "-nostdin", "-y"]
        request_headers = dict(self._headers)
        if self._referrer:
            request_headers["Referer"] = self._referrer
        request_headers["User-Agent"] = (
            self._user_agent
            or request_headers.get("User-Agent")
            or DEFAULT_USER_AGENT
        )
        header_lines = [f"{key}: {value}" for key, value in request_headers.items()]
        input_headers = ["-headers", "\r\n".join(header_lines) + "\r\n"]
        args.extend(input_headers)
        args.extend(["-i", self._url])
        if self._audio_url:
            args.extend(input_headers)
            args.extend(["-i", self._audio_url])
        args.extend(["-map", "0:v:0?"])
        args.extend(
            ["-map", "1:a:0?" if self._audio_url else "0:a:0?"]
        )
        args.extend(["-c", "copy"])
        if path.lower().endswith(".mkv"):
            args.extend(["-f", "matroska"])
        else:
            args.extend(["-f", "avi"])
        args.append(path)

        self._buffer = ""
        process.readyReadStandardOutput.connect(self._read_output)
        process.finished.connect(self._on_finished)
        self._process = process
        process.start(ffmpeg, args)
        if not process.waitForStarted(3000):
            self._process = None
            self.failed.emit(tr("recording_failed", error=process.errorString()))
            return False
        self.started.emit(path)
        return True

    def _read_output(self):
        if self._process is None:
            return
        data = bytes(self._process.readAllStandardOutput()).decode(
            "utf-8", errors="replace"
        )
        self._buffer = (self._buffer + data)[-4000:]

    def _on_finished(self, exit_code: int, _status):
        process = self._process
        if process is not None:
            self._read_output()
        self._process = None
        if process is not None:
            process.deleteLater()

        if self._stopping:
            self._stopping = False
            self.stopped.emit(self._path)
            return

        if (
            exit_code != 0
            and not self._fallback_done
            and time.monotonic() - self._started_at < 20
            and self._path.lower().endswith(".avi")
        ):
            self._fallback_done = True
            try:
                os.remove(self._path)
            except OSError:
                pass
            mkv_path = os.path.splitext(self._path)[0] + ".mkv"
            self._path = mkv_path
            ffmpeg = _find_ffmpeg()
            if ffmpeg and self._start_process(ffmpeg, mkv_path):
                self.fallback.emit(mkv_path)
                return

        if exit_code == 0:
            self.stopped.emit(self._path)
        else:
            detail = self._buffer.strip() or f"ffmpeg exit {exit_code}"
            self.failed.emit(tr("recording_failed", error=detail[-1200:]))

    def stop(self):
        if self._process is None:
            return
        self._stopping = True
        self._process.terminate()
        if not self._process.waitForFinished(3000):
            self._process.kill()
            self._process.waitForFinished(1000)

    def shutdown(self):
        if self._process is not None:
            self.stop()
