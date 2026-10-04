# WikiMasterBot

Petit bot d'automatisation en Python (**Selenium + PyAutoGUI**) pour mon site WikiMasters.
Il se branche sur un Chrome déjà ouvert, clique sur des boutons, simule des mouvements de souris
et répète un cycle d'environ 11 minutes.

> **Avertissement** : à utiliser uniquement sur un site qui t'appartient ou pour lequel tu as
> l'autorisation d'automatiser des actions. Respecte les conditions d'utilisation des sites visés.

---

## Comment ça marche

1. Tu lances **Chrome à la main** avec un port de debug (`9222`) et un profil dédié.
2. **Selenium** se connecte à ce Chrome (`debuggerAddress`) et clique sur les éléments de la page
   (bouton principal, flèche de droite, bouton « Continuer »).
3. **PyAutoGUI** cherche l'image `input_cible.png` sur l'écran et clique dessus avec un déplacement
   de souris « humain ».
4. À chaque recherche visuelle, une capture `debug_ecran_virtuel.png` est enregistrée (elle est
   écrasée à chaque fois) pour voir ce que le bot voit.

Le bot a donc besoin d'un **écran** : un vrai écran sur ton PC, ou un **écran virtuel (Xvfb)** sur
une VM sans interface graphique.

## Contenu du dépôt

| Fichier | Rôle |
|---|---|
| `wikimasterbot.py` | Le bot (boucle principale, clics, mouvements de souris) |
| `input_cible.png` | Image à repérer à l'écran (capture recadrée de l'élément à cliquer) |
| `start_chrome.sh` | **VM uniquement** : lance Xvfb puis Chrome avec le port de debug |
| `export_cookies.py` | Optionnel : exporte les cookies d'un Chrome connecté vers `cookies.json` |
| `requirements.txt` | Dépendances Python |
| `debug_ecran_virtuel.png` | Capture générée par le bot (ne pas versionner) |
| `cookies.json` | Cookies de session (**ne jamais versionner**) |

## Configuration avant de lancer

Dans `wikimasterbot.py` :

- **URL du site** : remplace `https://monSiteWEB` dans `driver.get(...)`.
- **Sélecteurs** : les boutons sont repérés par leurs classes CSS / texte (`hover:scale-105`,
  `w-12 rounded-full`, `Continuer`). Adapte-les si ton site change.
- **Durée d'un cycle** : `calculer_temps_aleatoire(660, 30)` = 660 s ± 30 s.
- **`input_cible.png`** : fais-la **sur la machine qui exécute le bot** (même résolution, même
  zoom, même thème). Une image prise ailleurs ne sera pas reconnue (`confidence=0.8`).
- **Écran** : en haut du script, la ligne suivante fonctionne en local comme sur la VM :

  ```python
  import os
  os.environ.setdefault("DISPLAY", ":99")   # n'écrase pas le DISPLAY d'un vrai bureau
  ```

---

# Version A : en local (sur ton PC)

### Prérequis
- Linux avec une session **X11** (PyAutoGUI ne fonctionne pas correctement sous Wayland)
- Google Chrome, Python 3

### Installation
```bash
sudo apt install -y scrot python3-tk python3-dev
git clone <url-du-depot> && cd WikiMasterBot
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
Si `requirements.txt` est incomplet : `pip install selenium pyautogui python3-xlib opencv-python pillow`.

### Lancement
**1. Ouvre Chrome avec le port de debug** (un profil dédié est obligatoire pour le debug) :
```bash
pkill -x chrome
google-chrome --ozone-platform=x11 --remote-debugging-port=9222 \
  --remote-allow-origins=* --user-data-dir="$HOME/chrome_bot" \
  --window-size=1920,1080 &
```

**2. Connecte-toi une fois au site** dans cette fenêtre. Le profil `chrome_bot` garde la session.

**3. Vérifie que le port répond :**
```bash
curl http://127.0.0.1:9222/json/version
```

**4. Lance le bot :**
```bash
source env/bin/activate
python wikimasterbot.py
```
Arrêt avec `Ctrl+C`.

---

# Version B : sur une VM Debian sans interface graphique

### Prérequis
- Debian (ou Ubuntu) en SSH, sans bureau
- Google Chrome installé (`.deb` officiel)
- Un client VNC sur ton PC (TigerVNC, RealVNC...) pour la première connexion

### Installation
```bash
sudo apt update
sudo apt install -y xvfb scrot python3-tk python3-dev x11-utils tmux x11vnc
git clone <url-du-depot> && cd WikiMasterBot
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Première connexion au site (une seule fois)
Le site demande un login avec un widget anti-bot : on se connecte donc à la main, via VNC, dans
l'écran virtuel. **Ne copie pas un profil Chrome d'un autre PC** : les cookies y sont chiffrés avec
une clé propre à la machine d'origine, la VM ne pourra pas les lire.

**Sur la VM :**
```bash
bash start_chrome.sh
x11vnc -display :99 -localhost -nopw -forever &
```

**Sur ton PC** (tunnel SSH, garde cette fenêtre ouverte) :
```bash
ssh -L 5900:localhost:5900 utilisateur@IP_DE_LA_VM
```
Puis dans un autre terminal : `vncviewer localhost:5900`.

Dans la fenêtre VNC : connecte-toi au site, attends ~10 secondes, puis ferme VNC. Sur la VM :
```bash
pkill x11vnc
bash start_chrome.sh      # relance Chrome proprement, la session est lue depuis le profil
```

### Lancement du bot
```bash
tmux new -s bot            # le bot survit à la fermeture du SSH
bash start_chrome.sh       # doit afficher : OK : Chrome écoute sur 9222
source env/bin/activate
python wikimasterbot.py
```
Détacher tmux sans arrêter le bot : `Ctrl+B` puis `D`. Revenir : `tmux attach -t bot`.

### Voir ce que voit le bot
```bash
scp utilisateur@IP_DE_LA_VM:~/WikiMasterBot/debug_ecran_virtuel.png .
```
Ouvre l'image, puis redécoupe `input_cible.png` à partir de cette capture si l'élément n'est pas reconnu.

---

## Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `curl: (7) Failed to connect ... 9222` | Chrome n'écoute pas | Vérifier `/tmp/chrome.log`, relancer `start_chrome.sh` |
| `Opening in existing browser session.` | Verrou de profil ou ancien Chrome encore vivant | `pkill -x chrome`, supprimer `Singleton*` dans le profil, relancer |
| `Erreur clic principal : Message:` + stacktrace | Timeout : bouton introuvable (page de login, page non chargée) | Regarder `debug_ecran_virtuel.png` |
| « L'image n'a jamais été vue » | `input_cible.png` ne correspond pas au rendu de la machine | La redécouper depuis une capture de cette machine |
| `Xlib.xauth: warning, no xauthority details` | Avertissement sans gravité | Ignorer |
| Erreurs `dbus` dans les logs Chrome | Pas de bus de session sur un serveur | Ignorer |
| `import pyautogui` plante (`DISPLAY`) | Pas d'écran défini | Vérifier `os.environ.setdefault("DISPLAY", ":99")` et que Xvfb tourne |
| Redirigé vers `/login` | Session absente ou expirée | Se reconnecter (VNC sur la VM) |

## Sécurité

Ajoute ceci à ton `.gitignore` :
```
env/
cookies.json
debug_ecran_virtuel*.png
chrome_bot/
profil_*/
COMMANDES_PERSO.md
```
`cookies.json` et le dossier de profil Chrome donnent accès à ton compte : traite-les comme un mot
de passe. Si l'un d'eux a fuité, déconnecte la session côté site.
