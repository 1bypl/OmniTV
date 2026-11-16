"""Widżet osadzający libmpv w oknie Qt."""

from __future__ import annotations

import locale
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from omnity.i18n import tr

try:
    import mpv as _mpv
    _MPV_IMPORT_ERROR = None
except Exception as _exc:  # pragma: no cover - zależne od systemu
    _mpv = None
    _MPV_IMPORT_ERROR = str(_exc)


class PlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(Qt.WA_NativeWindow)
        self.setStyleSheet("background-color: black;")
        self.setMinimumSize(480, 270)

        self._player = None
        self._default_user_agent = None
        self._volume = 70
        self._muted = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._message = QLabel(self._initial_message())
        self._message.setAlignment(Qt.AlignCenter)
        self._message.setWordWrap(True)
        self._message.setStyleSheet("color: #cfcfcf; font-size: 13px; padding: 24px;")
        layout.addWidget(self._message)

    def _initial_message(self) -> str:
        if _mpv is None:
            return tr(
                "player_unavailable",
                error=_MPV_IMPORT_ERROR or "python-mpv",
            )
        return tr("player_hint")

    def retranslate(self):
        if self._player is None:
            self._message.setText(self._initial_message())

    def is_muted(self) -> bool:
        return self._muted

    @property
    def available(self) -> bool:
        return _mpv is not None

    def _ensure_player(self):
        if self._player is not None:
            return self._player
        if _mpv is None:
            raise RuntimeError(
                tr("mpv_unavailable", error=_MPV_IMPORT_ERROR or "")
            )

        # Qt przy starcie ustawia LC_NUMERIC na locale systemowe, a libmpv
        # wymaga "C" — inaczej mpv_create() zwraca NULL i powoduje segfault.
        try:
            locale.setlocale(locale.LC_NUMERIC, "C")
        except locale.Error:
            pass

        # Zabezpieczenie: sprawdź, czy klient libmpv da się utworzyć.
        try:
            probe = _mpv._mpv_create()
            if not probe:
                raise RuntimeError(tr("mpv_locale_error"))
            _mpv._mpv_terminate_destroy(probe)
        except AttributeError:
            pass

        options = dict(
            wid=str(int(self.winId())),
            input_default_bindings=False,
            input_vo_keyboard=False,
            osc=False,
            ytdl=True,
        )
        vo = os.environ.get("OMNITY_VO")
        if vo:
            options["vo"] = vo
        elif sys.platform.startswith("linux"):
            # Na X11/XWayland najbardziej stabilny bywa software'owy vo=x11;
            # vo=gpu potrafi wywalić asercję na VM bez sprawnego EGL/GLX.
            options["vo"] = "x11"
        self._player = _mpv.MPV(**options)

        # Strojenie pod słabsze maszyny (VM, 4 GB RAM, bez GPU).
        def _int_env(name: str, default: int) -> int:
            try:
                return int(os.environ.get(name, default))
            except ValueError:
                return default

        cache_secs = max(2, _int_env("OMNITY_CACHE_SECS", 15))
        threads = max(1, _int_env("OMNITY_THREADS", min(4, os.cpu_count() or 4)))
        hwdec = os.environ.get("OMNITY_HWDEC", "no" if sys.platform.startswith("linux") else "auto")
        hls = os.environ.get("OMNITY_HLS_BITRATE")

        settings = (
            ("cache", True),
            ("cache_secs", cache_secs),
            ("demuxer_readahead_secs", max(2, cache_secs // 2)),
            ("demuxer_max_bytes", 64 * 1024 * 1024),
            ("demuxer_max_back_bytes", 16 * 1024 * 1024),
            ("network_timeout", 20),
            ("hwdec", hwdec),
            ("framedrop", "vo"),
            ("video_sync", "audio"),
            ("vd_lavc_threads", threads),
            ("sws_scaler", "fast-bilinear"),
        )
        if hls:
            settings += (("hls_bitrate", hls),)
        # Ustawienia opcjonalne — jeśli któraś opcja nie istnieje, ignorujemy.
        for name, value in settings:
            try:
                setattr(self._player, name, value)
            except Exception:
                pass

        try:
            self._default_user_agent = self._player.user_agent
        except Exception:
            self._default_user_agent = None
        self._player.volume = self._volume
        self._player.mute = self._muted
        return self._player

    def play(
        self,
        url: str,
        referrer: str | None = None,
        user_agent: str | None = None,
        headers: dict[str, str] | None = None,
        audio_url: str | None = None,
    ):
        player = self._ensure_player()

        try:
            request_headers = dict(headers or {})
            if referrer:
                request_headers["Referer"] = referrer
            if user_agent:
                request_headers["User-Agent"] = user_agent
            player.http_header_fields = [
                f"{key}: {value}"
                for key, value in request_headers.items()
                if key.lower() != "user-agent"
            ]
        except Exception:
            pass

        try:
            player.user_agent = user_agent or (headers or {}).get(
                "User-Agent"
            ) or self._default_user_agent
        except Exception:
            pass

        player.play(url)
        if audio_url:
            player.command("audio-add", audio_url, "select")
        self._message.hide()

    def stop(self):
        self.clear_subtitle()
        if self._player is not None:
            self._player.stop()
            self._message.setText(tr("player_hint"))
            self._message.show()

    def toggle_pause(self):
        if self._player is not None:
            self._player.pause = not self._player.pause

    def set_volume(self, value: int):
        self._volume = int(value)
        if self._player is not None:
            self._player.volume = self._volume

    def toggle_mute(self) -> bool:
        self._muted = not self._muted
        if self._player is not None:
            self._player.mute = self._muted
        return self._muted

    # -------------------------------------------------------------- napisy
    def subtitle_tracks(self) -> list:
        if self._player is None:
            return []
        try:
            return [
                track
                for track in self._player.track_list
                if track.get("type") == "sub"
            ]
        except Exception:
            return []

    def prepare_subtitles(self) -> bool:
        if self._player is None:
            return False
        text_tracks = [
            track
            for track in self.subtitle_tracks()
            if not track.get("image")
        ]
        if not text_tracks:
            return False
        track_id = text_tracks[0].get("id")
        try:
            if self._player.sid != track_id:
                self._player.sid = track_id
            self._player.sub_visibility = False
            return True
        except Exception:
            return False

    def current_subtitle_text(self) -> str:
        if self._player is None:
            return ""
        try:
            return (self._player.sub_text or "").strip()
        except Exception:
            return ""

    def show_subtitle(self, text: str):
        if self._player is None or not text:
            return
        dimensions = {}
        try:
            dimensions = self._player.osd_dimensions or {}
        except Exception:
            pass
        width = int(dimensions.get("w") or 0)
        height = int(dimensions.get("h") or 0)
        if width <= 0:
            try:
                width = int(self._player.width or 1280)
            except Exception:
                width = 1280
        if height <= 0:
            try:
                height = int(self._player.height or 720)
            except Exception:
                height = 720
        font_size = max(18, min(44, round(height * 0.045)))
        margin = max(28, round(height * 0.075))
        y = max(font_size + 16, height - margin)
        safe = (
            text.replace("\\", "\\\\")
            .replace("{", "(")
            .replace("}", ")")
            .replace("\r", "")
            .replace("\n", "\\N")
        )
        ass = (
            f"{{\\an2\\pos({width // 2},{y})\\fs{font_size}"
            f"\\bord2\\shad0\\c&HFFFFFF&}}{safe}"
        )
        try:
            self._player.command(
                "osd-overlay", 1, "ass-events", ass, width, height, 0
            )
        except Exception:
            pass

    def clear_subtitle(self):
        if self._player is None:
            return
        try:
            self._player.command("osd-overlay", 1, "none", "", 0, 0)
        except Exception:
            pass

    def restore_subtitles(self):
        if self._player is None:
            return
        self.clear_subtitle()
        try:
            self._player.sub_visibility = True
        except Exception:
            pass

    def shutdown(self):
        self.clear_subtitle()
        if self._player is not None:
            try:
                self._player.terminate()
            except Exception:
                pass
            self._player = None
