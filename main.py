"""Punkt wejścia aplikacji OmniTV."""

import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from omnity.ui.main_window import MainWindow


def _icon_path() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "omnity_assets", "omnity.png")
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, os.pardir, "packaging", "linux", "omnity.png")


def _configure_platform() -> None:
    """Na Waylandzie wymuś XWayland: osadzanie obrazu libmpv przez wid
    działa pewnie tylko na X11."""
    if (
        "QT_QPA_PLATFORM" not in os.environ
        and os.environ.get("XDG_SESSION_TYPE") == "wayland"
    ):
        os.environ["QT_QPA_PLATFORM"] = "xcb"


def _selftest_mpv() -> int:
    import ctypes.util
    import locale

    import mpv as _m

    print("OmniTV mpv self-test", flush=True)
    print("backend:", getattr(_m.backend, "_name", "?"), flush=True)
    print("find_library:", ctypes.util.find_library("mpv"), flush=True)
    print("LC_NUMERIC:", locale.setlocale(locale.LC_NUMERIC), flush=True)

    handle = _m._mpv_create()
    print("mpv_create (bez Qt):", handle, "value:", getattr(handle, "value", None), flush=True)
    if handle:
        print("api:", _m._mpv_client_api_version(), flush=True)
        print("set vo:", _m._mpv_set_option_string(handle, b"vo", b"null"), flush=True)
        print("initialize:", _m._mpv_initialize(handle), flush=True)
        _m._mpv_terminate_destroy(handle)

    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    print("LC_NUMERIC po Qt:", locale.setlocale(locale.LC_NUMERIC), flush=True)
    try:
        locale.setlocale(locale.LC_NUMERIC, "C")
    except locale.Error:
        pass
    print("LC_NUMERIC naprawione:", locale.setlocale(locale.LC_NUMERIC), flush=True)
    handle = _m._mpv_create()
    print("mpv_create (po Qt):", handle, "value:", getattr(handle, "value", None), flush=True)
    if handle:
        print("set vo2:", _m._mpv_set_option_string(handle, b"vo", b"null"), flush=True)
        print("initialize2:", _m._mpv_initialize(handle), flush=True)
        _m._mpv_terminate_destroy(handle)
    print("MPV SELFTEST DONE", flush=True)
    return 0


def _playtest(channel_id: str) -> int:
    import time

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    deadline = time.time() + 90
    while time.time() < deadline and window._catalog is None:
        app.processEvents()
        time.sleep(0.05)
    if window._catalog is None:
        print("playtest: baza się nie wczytała", flush=True)
        return 2

    channel = next((c for c in window._channels if c.get("id") == channel_id), None)
    if channel is None:
        print("playtest: brak kanału", channel_id, flush=True)
        return 3
    stream = window._catalog.best_stream(channel_id)
    if not stream:
        print("playtest: brak strumienia", channel_id, flush=True)
        return 4

    print("playtest: kanał", channel.get("name"), flush=True)
    print("playtest: URL", stream.get("url"), flush=True)
    window._player.play(
        stream["url"], stream.get("referrer"), stream.get("user_agent")
    )

    end = time.time() + 20
    while time.time() < end:
        app.processEvents()
        time.sleep(0.05)

    player = window._player._player
    status = 0
    if player is None:
        print("playtest: brak obiektu player", flush=True)
        status = 1
    else:
        try:
            print(
                "playtest: idle=%s time_pos=%s w=%s h=%s"
                % (player.idle_active, player.time_pos, player.width, player.height),
                flush=True,
            )
            print(
                "playtest: hwdec=%s framedrop=%s threads=%s cache_secs=%s sws=%s"
                % (
                    player.hwdec,
                    player.framedrop,
                    player.vd_lavc_threads,
                    player.cache_secs,
                    player.sws_scaler,
                ),
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001
            print("playtest: odczyt stanu nieudany:", exc, flush=True)

    window._player.shutdown()
    window.close()
    app.processEvents()
    return status


def _selftest() -> int:
    print("OmniTV self-test")
    print("QT_QPA_PLATFORM:", os.environ.get("QT_QPA_PLATFORM") or "(domyślny)")
    try:
        import PySide6

        print("PySide6:", PySide6.__version__)
    except Exception as exc:  # noqa: BLE001
        print("PySide6: FAIL", exc)
    try:
        import mpv  # noqa: F401

        print("python-mpv: OK")
    except Exception as exc:  # noqa: BLE001
        print("python-mpv: FAIL", exc)
    icon = os.path.normpath(_icon_path())
    print("ikona:", "OK" if os.path.exists(icon) else "BRAK", icon)
    return 0


def main():
    _configure_platform()

    if "--selftest-mpv" in sys.argv:
        sys.exit(_selftest_mpv())
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    if "--playtest" in sys.argv:
        index = sys.argv.index("--playtest")
        channel_id = (
            sys.argv[index + 1]
            if index + 1 < len(sys.argv)
            else "PlutoTVAction.us"
        )
        sys.exit(_playtest(channel_id))

    app = QApplication(sys.argv)
    app.setApplicationName("OmniTV")
    app.setOrganizationName("OmniTV")

    icon_path = os.path.normpath(_icon_path())
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    try:
        app.setStyle("Fusion")
    except Exception:
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
