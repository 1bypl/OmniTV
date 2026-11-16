#!/usr/bin/env bash
# Buduje pakiet RPM dla OmniTV (najlepiej uruchamiać na Fedorze).
set -euo pipefail

APP_VERSION="${APP_VERSION:-0.2.0}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# rpmbuild nie radzi sobie ze spacjami w ścieżce katalogu roboczego
# (rozbija %{_sourcedir}/%{buildroot} na osobne argumenty). Używamy
# dowiązania pod ścieżką bez spacji; pliki trafiają do tego samego drzewa.
RPM_TMP="$(mktemp -d "${TMPDIR:-/tmp}/omnity-rpm.XXXXXX")"
ln -s "$ROOT" "$RPM_TMP/src"
B="$RPM_TMP/src"
trap 'rm -rf "$RPM_TMP"' EXIT

TOP="$B/build/rpm"
LINUX_DIST="$B/build/linux-dist"
LINUX_WORK="$B/build/linux-work"

PYINSTALLER="${PYINSTALLER:-$B/.venv/bin/pyinstaller}"
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  if [ ! -x "$PYINSTALLER" ]; then
    if command -v pyinstaller >/dev/null; then
      PYINSTALLER="$(command -v pyinstaller)"
    else
      echo "Brak PyInstaller: .venv/bin/pip install pyinstaller"; exit 1
    fi
  fi
fi

SPEC_VERSION="$(awk '/^Version:/{print $2; exit}' "$B/packaging/fedora/omnity.spec")"
if [ "$APP_VERSION" != "$SPEC_VERSION" ]; then
  echo "Niezgodna wersja: APP_VERSION=$APP_VERSION, spec=$SPEC_VERSION"; exit 1
fi

RPMBUILD="${RPMBUILD:-$(command -v rpmbuild || true)}"
if [ -z "$RPMBUILD" ]; then
  echo "Brak rpmbuild. Na Fedorze: sudo dnf install rpm-build"
  echo "Na Ubuntu/Debian można wskazać RPMBUILD=/sciezka/do/rpmbuild."
  exit 1
fi

cd "$B"
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  "$PYINSTALLER" --clean --noconfirm \
      --distpath "$LINUX_DIST" --workpath "$LINUX_WORK" \
      packaging/omnity.spec
fi

# Nowsze dystrybucje (glibc 2.4x) potrafią przypisać część funkcji libc/libm
# do nowych wersji symboli. Obniżamy bezpieczne wymagania do GLIBC_2.2.5,
# żeby pakiet działał na Fedorze 40+ (glibc >= 2.39).
python3 "$B/packaging/linux/fix_glibc_compat.py" "$LINUX_DIST/OmniTV"

rm -rf "$TOP"
mkdir -p "$TOP/BUILD" "$TOP/BUILDROOT" "$TOP/RPMS" "$TOP/SOURCES" \
         "$TOP/SPECS" "$TOP/SRPMS" "$TOP/rpmdb"
cp -a "$LINUX_DIST/OmniTV" "$TOP/SOURCES/OmniTV"
cp "$B/packaging/linux/omnity.desktop" "$TOP/SOURCES/omnity.desktop"
cp "$B/packaging/linux/omnity.png" "$TOP/SOURCES/omnity.png"
cp "$B/LICENSE" "$TOP/SOURCES/LICENSE"

"$RPMBUILD" --define "_topdir $TOP" --define "_dbpath $TOP/rpmdb" -bb \
    "$B/packaging/fedora/omnity.spec"

RPM_FILE="$(find "$TOP/RPMS" -name '*.rpm' -type f | head -n 1)"
if [ -z "$RPM_FILE" ]; then
  echo "rpmbuild nie utworzył pakietu"; exit 1
fi
cp "$RPM_FILE" "$ROOT/dist/"
RPM_NAME="$(basename "$RPM_FILE")"
mkdir -p "$ROOT/dist"
( cd "$ROOT/dist" && sha256sum "$RPM_NAME" > "$RPM_NAME.sha256" )
echo
echo "Gotowe: $ROOT/dist/$RPM_NAME"
echo "Suma SHA-256: $ROOT/dist/$RPM_NAME.sha256"
echo "Instalacja: sudo dnf install \"$ROOT/dist/$RPM_NAME\""
