# Mémo perso : WikiMasterBot

> Fichier privé : à garder hors de git (ajouté au `.gitignore`).
> Complète les `IP_DE_LA_VM` avec ta vraie IP, à la main, sur ta machine.

## Repères

| Élément | Valeur |
|---|---|
| PC (local) | `paulylap`, dossier du projet `~/Documents/auto_click` |
| VM | `paulin` (Debian, sans interface), dossier `~/WikiMasterBot` |
| Utilisateur | `pverriere` |
| IP de la VM | `162.38.112.157` |
| Port de debug Chrome | `9222` |
| Écran virtuel (VM) | `:99` (Xvfb, 1920x1080) |
| Profil Chrome local | `~/Documents/chrome_bot` |
| Profil Chrome VM | `~/WikiMasterBot/chrome_bot` |

---

# PARTIE 1 : LOCAL (sur mon PC)

## Lancer le bot

```bash
cd ~/Documents/auto_click
source env/bin/activate                  # active le venv Python
```

```bash
pkill -x chrome                          # ferme Chrome (nom exact, sans risque de se tuer soi-même)
export XDG_SESSION_TYPE=x11              # force X11 pour que PyAutoGUI voie l'écran
google-chrome --ozone-platform=x11 \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir="$HOME/Documents/chrome_bot" \
  --disable-gpu --window-size=1920,1080 &
```
- `--ozone-platform=x11` : Chrome utilise X11 au lieu de Wayland
- `--remote-debugging-port=9222` : ouvre le port auquel Selenium se connecte
- `--remote-allow-origins=*` : autorise la connexion de Selenium au port de debug
- `--user-data-dir=...` : profil dédié (obligatoire pour le debug, contient ma session)
- `&` : lance en arrière-plan pour garder le terminal

```bash
curl http://127.0.0.1:9222/json/version  # du JSON = Chrome écoute bien
python wikimasterbot.py                  # lance le bot (Ctrl+C pour arrêter)
```

## Ouvrir Chrome normalement avec le profil du bot (pour me connecter / vérifier)

```bash
google-chrome --user-data-dir="$HOME/Documents/chrome_bot"
```
Sans port de debug : sert juste à voir le site avec la session du bot.
Si le message `Opening in existing browser session` apparaît, un Chrome utilise déjà ce profil : `pkill -x chrome` puis relancer.

## Cookies (plus nécessaire normalement)

`export_cookies.py` exporte les cookies d'un Chrome lancé sur le port 9222 vers `cookies.json`.
Je ne m'en sers plus : sur la VM, je me connecte directement par VNC. Cookie = mot de passe, ne jamais le versionner.

---

# PARTIE 2 : VM (Debian sans interface)

## Connexion et envoi de fichiers

```bash
ssh pverriere@162.38.112.157                                  # se connecter à la VM
scp wikimasterbot.py pverriere@162.38.112.157:~/WikiMasterBot/ # PC -> VM
scp pverriere@162.38.112.157:~/WikiMasterBot/debug_ecran_virtuel.png .   # VM -> PC (voir ce que voit le bot)
```

## tmux (le bot continue si je ferme le SSH)

```bash
tmux new -s bot            # crée la session "bot"
# Ctrl+B puis D            # détacher (le bot continue)
tmux attach -t bot         # revenir dans la session
tmux ls                    # lister les sessions
tmux kill-session -t bot   # tuer la session
```

## Démarrage normal (à chaque fois)

```bash
tmux new -s bot
cd ~/WikiMasterBot
bash start_chrome.sh                       # Xvfb + Chrome, doit finir par "OK : Chrome écoute sur 9222"
source env/bin/activate
python wikimasterbot.py
```

## `start_chrome.sh` (version de référence)

```bash
#!/bin/bash
PROFIL="$HOME/WikiMasterBot/chrome_bot"

pkill -x chrome                  # ferme Chrome (-x = nom exact, le script ne se tue pas lui-même)
pkill -x Xvfb                    # ferme l'écran virtuel
sleep 2

rm -f "$PROFIL"/Singleton*       # supprime les verrous du profil
rm -f /tmp/.X99-lock             # supprime le verrou de l'écran :99

Xvfb :99 -screen 0 1920x1080x24 &   # écran virtuel 1920x1080, 24 bits
sleep 2
export DISPLAY=:99

google-chrome --no-sandbox --disable-dev-shm-usage --disable-gpu \
  --window-size=1920,1080 --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --disable-session-crashed-bubble --hide-crash-restore-bubble --test-type \
  --user-data-dir="$PROFIL" \
  > /tmp/chrome.log 2>&1 &

sleep 5
curl -s http://127.0.0.1:9222/json/version && echo "OK : Chrome écoute sur 9222"
```

| Option | Rôle |
|---|---|
| `--no-sandbox` | Nécessaire sur la VM (sinon Chrome refuse de démarrer selon l'utilisateur/le noyau) |
| `--disable-dev-shm-usage` | Évite les crashs quand `/dev/shm` est trop petit |
| `--disable-gpu` | Pas de GPU sur la VM |
| `--remote-debugging-port=9222` | Port auquel Selenium se connecte |
| `--remote-allow-origins=*` | Autorise la connexion Selenium |
| `--disable-session-crashed-bubble`, `--hide-crash-restore-bubble` | Supprime la bulle « Restore pages? » |
| `--test-type` | Supprime la barre bleue `--no-sandbox` (qui décalait la page de ~60 px) |
| `> /tmp/chrome.log 2>&1` | Logs de Chrome dans `/tmp/chrome.log` |

## Me connecter au site sur la VM (VNC, quand la session a expiré)

**Sur la VM :**
```bash
bash start_chrome.sh
x11vnc -display :99 -localhost -nopw -forever &   # partage l'écran :99 (seulement via tunnel SSH)
```
**Sur le PC :**
```bash
ssh -L 5900:localhost:5900 pverriere@IP_DE_LA_VM  # tunnel, garder la fenêtre ouverte
vncviewer localhost:5900                          # dans un autre terminal
```
Dans VNC : login + case Cloudflare + Connexion, attendre ~10 s, fermer VNC.
**Sur la VM :**
```bash
pkill x11vnc
bash start_chrome.sh                              # relance proprement : la session est écrite dans le profil
```
Attention : si je relance `start_chrome.sh`, Xvfb redémarre et `x11vnc` meurt avec : il faut le relancer.

## Diagnostic

```bash
curl http://127.0.0.1:9222/json/version   # Chrome répond-il ?
cat /tmp/chrome.log                       # logs de Chrome
pgrep -a Xvfb                             # l'écran virtuel tourne-t-il ?
pgrep -a chrome | head -3                 # Chrome tourne-t-il ?
ss -ltnp | grep 9222                      # qui écoute sur le port 9222 ?
xdpyinfo -display :99 | head -5           # l'écran :99 répond-il ?
pgrep -a x11vnc                           # x11vnc tourne-t-il ?
scp pverriere@162.38.112.157:~/WikiMasterBot/debug_ecran_virtuel.png .  #voir ce que le bot voit
```

## Ménage sur la VM

```bash
cd ~
rm -f google-chrome-stable_current_amd64.deb      # installeur déjà utilisé
rm -f profil_chrome_connecte.tar.gz               # archive d'un ancien profil (contient une session)
rm -rf WikiMasterBot/profil_neuf                  # ancien profil de test
rm -f WikiMasterBot/debug_ecran_virtuel_*.png     # anciennes captures numérotées
```

---

# PARTIE 3 : GIT

```bash
git status                           # fichiers modifiés / non suivis
git check-ignore -v cookies.json     # vérifie que cookies.json est bien ignoré (doit afficher la règle)
git add wikimasterbot.py README.md start_chrome.sh requirements.txt
git commit -m "message"
git push
```
`.gitignore` à avoir : `env/`, `cookies.json`, `debug_ecran_virtuel*.png`, `chrome_bot/`, `profil_*/`, `COMMANDES_PERSO.md`.
Si `cookies.json` a déjà été commité une fois, l'ajouter au `.gitignore` ne suffit pas : il reste dans l'historique, et il faut déconnecter la session côté site.

---

# PARTIE 4 : Pannes déjà rencontrées

| Problème | Cause | Solution |
|---|---|---|
| `Terminated` au lancement de `start_chrome.sh` | `pkill -f chrome` tuait le script lui-même (son nom contient « chrome ») | Utiliser `pkill -x chrome` |
| `curl: (7)` + `Opening in existing browser session` | Verrou `Singleton*` ou ancien Chrome encore vivant | `pkill -x chrome`, `rm -f ...Singleton*`, relancer |
| `Xlib.xauth: warning` | Pas de fichier Xauthority sur la VM | Sans gravité |
| Erreurs `dbus` | Pas de bus de session sur un serveur | Sans gravité |
| `Erreur clic principal : Message:` + stacktrace | Timeout 15 s : le bot était sur la page de login | Se connecter (VNC) |
| `scrot: ... already exists` | `pyautogui.screenshot("fichier")` passe par scrot qui n'écrase pas | `pyautogui.screenshot().save("debug_ecran_virtuel.png")` |
| Cookies copiés du PC refusés | Chrome chiffre les cookies avec une clé liée à la machine | Se connecter directement sur la VM |
| Cookie `www.wiki-masters.com` refusé sur `wiki-masters.com` | Domaine différent (avec/sans `www`) | `c.pop("domain")` avant `add_cookie` |
| Token Supabase invalidé | Refresh tokens qui tournent : PC et VM se les invalident | Une session distincte par machine |
| « L'image n'a jamais été vue » | `input_cible.png` prise sur le PC, rendu différent | La redécouper depuis `debug_ecran_virtuel.png` de la VM |
| Bulle « Restore pages? » / barre `--no-sandbox` | Chrome tué brutalement / flag non supporté | Options `--hide-crash-restore-bubble`, `--test-type` |

## Rappels

- Dans le script : `os.environ.setdefault("DISPLAY", ":99")` avant `import pyautogui` (marche en local ET sur la VM).
- `input_cible.png` est propre à chaque machine : une version pour le PC, une pour la VM.
- Je n'ai pas besoin de VNC tant que la session du profil de la VM reste valide.
