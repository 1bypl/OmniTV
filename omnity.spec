# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))

# libmpv na Windows: jesli libmpv-2.dll lezy w katalogu projektu, dolacz go.
binaries = []
windows_dll = os.path.join(ROOT, "libmpv-2.dll")
if os.path.exists(windows_dll):
    binaries.append((windows_dll, "."))

datas = []
yt_dlp_datas, yt_dlp_binaries, yt_dlp_hiddenimports = collect_all("yt_dlp")
datas.extend(yt_dlp_datas)
binaries.extend(yt_dlp_binaries)
icon = os.path.join(ROOT, "packaging", "linux", "omnity.png")
if os.path.exists(icon):
    datas.append((icon, "omnity_assets"))

a = Analysis(
    [os.path.join(ROOT, "omnity", "main.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=["mpv", *yt_dlp_hiddenimports],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Na Linuksie korzystamy z systemowych bibliotek multimedialnych i kryptograficznych,
# aby uniknąć konfliktów wersji między GnuTLS, Nettle i Hogweed.
system_libs = {
    "libaom.so.3",
    "libasound.so.2",
    "libglib-2.0.so.0",
    "libglycin-2.so.0",
    "libgnutls.so.30",
    "liblcms2.so.2",
    "libmvec.so.1",
    "libsystemd.so.0",
    "libtinfo.so.6",
}
system_prefixes = (
    "libavcodec.",
    "libavdevice.",
    "libavfilter.",
    "libavformat.",
    "libavutil.",
    "libass.",
    "libdrm.",
    "libjxl",
    "libhogweed.",
    "libmp3lame.",
    "libmpv.",
    "libnettle.",
    "libplacebo.",
    "libpostproc.",
    "libssh.",
    "libswresample.",
    "libswscale.",
    "libva",
    "termios.",
)

def _is_system_lib(name):
    return name in system_libs or name.startswith(system_prefixes)

a.binaries = [b for b in a.binaries if not _is_system_lib(os.path.basename(b[0]))]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="OmniTV",
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="OmniTV",
)
