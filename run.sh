#!/usr/bin/env bash
# Uruchamia OmniTV. Na Waylandzie wymusza XWayland (xcb), bo osadzanie libmpv
# przez wid działa pewnie tylko na X11 — chyba że użytkownik ustawi QT_QPA_PLATFORM sam.
set -e
cd "$(dirname "$0")"

if [ -z "${QT_QPA_PLATFORM:-}" ] && [ "${XDG_SESSION_TYPE:-}" = "wayland" ]; then
  export QT_QPA_PLATFORM=xcb
fi

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

exec "$PYTHON" -m omnity.main "$@"
