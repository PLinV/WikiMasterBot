#!/bin/bash
# Nettoyage
pkill -f chrome
pkill Xvfb
sleep 2

# Supprime les verrous du profil
rm -f "$HOME/WikiMasterBot/profil_neuf"/Singleton*

# Écran virtuel
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2
export DISPLAY=:99

# Chrome avec le port de debug
google-chrome --no-sandbox --disable-dev-shm-usage --disable-gpu \
  --window-size=1920,1080 --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir="$HOME/WikiMasterBot/profil_neuf" \
  > /tmp/chrome.log 2>&1 &

sleep 5
curl -s http://127.0.0.1:9222/json/version && echo "OK : Chrome écoute sur 9222"