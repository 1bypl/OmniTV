#!/usr/bin/env bash
# Jednorazowa instalacja zależności OmniTV (Ubuntu/Debian).
set -euo pipefail
cd "$(dirname "$0")"

if ! ldconfig -p 2>/dev/null | grep -qi libmpv; then
  echo "Brak libmpv — instaluję pakiet systemowy (poprosi o hasło sudo)..."
  sudo apt-get update
  sudo apt-get install -y libmpv2 || sudo apt-get install -y libmpv1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Brak ffmpeg — nagrywanie wymaga FFmpeg. Instaluję pakiet systemowy..."
  sudo apt-get install -y ffmpeg || echo "Uwaga: zainstaluj ffmpeg ręcznie, aby nagrywać."
fi

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo
echo "Gotowe. Uruchom aplikację poleceniem: ./run.sh"
