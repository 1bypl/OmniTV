#!/usr/bin/env bash
# Buduje pakiet .deb dla OmniTV (uruchamiaj na Ubuntu/Debian).
set -euo pipefail

APP_NAME="omnity"
EXE_NAME="OmniTV"
APP_VERSION="${APP_VERSION:-0.2.0}"
ARCH="${ARCH:-$(dpkg --print-architecture)}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/build/deb"
LINUX_DIST="$ROOT/build/linux-dist"
LINUX_WORK="$ROOT/build/linux-work"
OUT="$ROOT/dist/${APP_NAME}_${APP_VERSION}_${ARCH}.deb"

PYINSTALLER="${PYINSTALLER:-$ROOT/.venv/bin/pyinstaller}"
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  if [ ! -x "$PYINSTALLER" ]; then
    if command -v pyinstaller >/dev/null; then
      PYINSTALLER="$(command -v pyinstaller)"
    else
      echo "Brak PyInstaller: .venv/bin/pip install pyinstaller"; exit 1
    fi
  fi
fi
command -v dpkg-deb >/dev/null || { echo "Brak dpkg-deb: sudo apt install dpkg"; exit 1; }

cd "$ROOT"
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  "$PYINSTALLER" --clean --noconfirm \
      --distpath "$LINUX_DIST" --workpath "$LINUX_WORK" \
      packaging/omnity.spec
fi

# Nowsze dystrybucje (glibc 2.4x) potrafią przypisać część funkcji libc/libm
# do nowych wersji symboli. Obniżamy bezpieczne wymagania do GLIBC_2.2.5,
# żeby pakiet działał na Ubuntu 24.04 / Debianie 13 (glibc >= 2.39).
python3 "$ROOT/packaging/linux/fix_glibc_compat.py" "$LINUX_DIST/$EXE_NAME"

rm -rf "$PKG"
mkdir -p "$PKG/DEBIAN" \
         "$PKG/usr/lib/$APP_NAME" \
         "$PKG/usr/bin" \
         "$PKG/usr/share/applications" \
         "$PKG/usr/share/icons/hicolor/256x256/apps" \
         "$PKG/usr/share/doc/$APP_NAME"

cp -r "$LINUX_DIST/$EXE_NAME/." "$PKG/usr/lib/$APP_NAME/"
install -m 644 "$ROOT/LICENSE" "$PKG/usr/share/doc/$APP_NAME/LICENSE"
ln -sf "/usr/lib/$APP_NAME/$EXE_NAME" "$PKG/usr/bin/$APP_NAME"
install -m 644 "$ROOT/packaging/linux/omnity.desktop" \
    "$PKG/usr/share/applications/$APP_NAME.desktop"

if [ -f "$ROOT/packaging/linux/omnity.png" ]; then
  install -m 644 "$ROOT/packaging/linux/omnity.png" \
      "$PKG/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"
fi

INSTALLED_SIZE="$(du -sk "$PKG/usr" | cut -f1)"

cat > "$PKG/DEBIAN/control" <<EOF
Package: $APP_NAME
Version: $APP_VERSION
Section: video
Priority: optional
Architecture: $ARCH
Maintainer: 1bypl <1bypl@users.noreply.github.com>
Depends: libc6 (>= 2.39), libmpv2 | libmpv1, ffmpeg, libxcb-cursor0, libxcb-icccm4, libxcb-image0, libxcb-keysyms1, libxcb-render-util0, libxcb-xkb1, libxkbcommon-x11-0, libxcb-randr0, libxcb-shape0, libxcb-xinerama0, libxcb-xfixes0
Installed-Size: $INSTALLED_SIZE
Description: OmniTV - odtwarzacz darmowych kanalow TV online
 Przegladarka i odtwarzacz publicznie dostepnych kanalow IPTV
 z bazy iptv-org, z wbudowanym odtwarzaczem libmpv.
EOF

dpkg-deb --build --root-owner-group "$PKG" "$OUT"
mkdir -p "$ROOT/dist"
( cd "$ROOT/dist" && sha256sum "$(basename "$OUT")" > "$(basename "$OUT").sha256" )
echo
echo "Gotowe: $OUT"
echo "Suma SHA-256: $OUT.sha256"
echo "Instalacja: sudo apt install \"$OUT\""
