import os
os.environ["DISPLAY"] = ":99"

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, InvalidSessionIdException, WebDriverException
import pyautogui
import time
import random

## On nettoie tout par sécurité
#pkill -9 -f chrome

## On configure l'écran virtuel
#export DISPLAY=:99
#export XDG_SESSION_TYPE=x11

## On lance avec votre ancien profil
#google-chrome --ozone-platform=x11 --remote-debugging-port=9222 --user-data-dir="/home/pverriere/Documents/chrome_bot" --disable-gpu --window-size=1920,1080

# python wikimasterbot.py

## pour avoir un accés graphique quand même : 
# google-chrome --user-data-dir="/home/pverriere/Documents/chrome_bot"

# POUR DANS LA VM AVOIR LE DEBUG SCREEN : 
#  scp pverriere@IP_DE_LA_VM:~/WikiMasterBot/debug_ecran_virtuel.png .

def cliquer_element_visuel_organique(chemin_image="input_cible.png", confiance=0.8, timeout=20):
    """
    Cherche l'image pendant 20s, prend UNE SEULE capture d'écran à la fin, puis agit.
    """
    print(f"\n-> DÉBOGAGE : Lancement de la recherche visuelle de '{chemin_image}' (max {timeout}s)...")
    
    coordonnees = None
    temps_debut = time.time()
    
    # 1. BOUCLE DE RECHERCHE PENDANT 20 SECONDES
    while time.time() - temps_debut < timeout:
        try:
            coordonnees = pyautogui.locateCenterOnScreen(chemin_image, confidence=confiance)
            if coordonnees:
                print("   [SUCCÈS] Image trouvée ! Arrêt de la recherche.")
                break 
        except pyautogui.ImageNotFoundException:
            pass
        
        time.sleep(0.5)
    
    # 2. PRISE DE LA CAPTURE D'ÉCRAN UNIQUE (au bout des 20s, ou dès qu'il a trouvé)
    pyautogui.screenshot("debug_ecran_virtuel.png")
    print("-> DÉBOGAGE : Capture 'debug_ecran_virtuel.png' enregistrée. Regardez cette image !")
    
    # 3. ACTION OU ABANDON
    if coordonnees:
        cible_x, cible_y = coordonnees
        print(f"-> Déplacement physique vers X={cible_x}, Y={cible_y}")
        
        depart_x, depart_y = pyautogui.position()
        nb_pas = random.randint(30, 50)
        
        for i in range(1, nb_pas + 1):
            progression = i / nb_pas
            point_x = depart_x + (cible_x - depart_x) * progression
            point_y = depart_y + (cible_y - depart_y) * progression
            
            marge = 5 if progression < 0.8 else 1 
            bruit_x = random.randint(-marge, marge)
            bruit_y = random.randint(-marge, marge)
            
            pyautogui.moveTo(point_x + bruit_x, point_y + bruit_y)
            time.sleep(random.uniform(0.001, 0.005))
        
        pyautogui.moveTo(cible_x, cible_y, duration=random.uniform(0.1, 0.2))
        time.sleep(random.uniform(0.2, 0.7))
        
        pyautogui.click()
        print("   Clic physique humain effectué !")
        
    else:
        print(f"-> DÉBOGAGE : Fin du temps imparti ({timeout}s). L'image n'a jamais été vue.")


# fonction pour simuler un mouvement de souris fluide
def simuler_mouvement_souris_organique(driver, actions, duree_secondes):
    """Mouvements fluides avec protection contre les sorties d'écran."""
    print(f"   [Attente active] {duree_secondes:.0f} secondes de mouvements...")
    
    # On recentre la souris de manière sûre en ciblant le corps de la page
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        actions.move_to_element(body).perform()
    except Exception:
        pass
    
    heure_debut = time.time()
    
    while time.time() - heure_debut < duree_secondes:
        # Sortie de sécurité
        if time.time() - heure_debut >= duree_secondes:
            break
            
        # Mouvements relatifs plus petits pour éviter les bords
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        
        try:
            actions.move_by_offset(offset_x, offset_y).perform()
        except Exception:
            # Si on touche le bord de l'écran, on se recentre sur le corps de la page
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                actions.move_to_element(body).perform()
            except Exception:
                pass
        
        # Gestion du temps de pause
        temps_pause = random.uniform(0.1, 0.5)
        temps_restant = duree_secondes - (time.time() - heure_debut)
        
        if temps_pause > temps_restant > 0:
            time.sleep(temps_restant)
        elif temps_restant > 0:
            time.sleep(temps_pause)

# ==========================================
# 1. DÉFINITION DES ACTIONS (FONCTIONS)
# ==========================================

def calculer_temps_aleatoire(temps_base, variation):
    """Renvoie un temps en secondes avec une marge d'erreur (gère les décimales)."""
    return temps_base + random.uniform(-variation, variation)

def faire_une_pause(secondes):
    """Gère l'attente et affiche le temps restant dans la console."""
    minutes = int(secondes // 60)
    sec = int(secondes % 60)
    print(f"Pause démarrée pour {secondes:.0f} secondes (soit {minutes}m et {sec}s)...")
    time.sleep(secondes)

def cliquer_sur_bouton_principal(driver):
    print("-> Recherche du bouton principal...")
    try:
        bouton = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='hover:scale-105']"))
        )
        bouton.click()
        print("-> Clic principal effectué.")
    except Exception as e:
        print(f"-> Erreur clic principal : {e}")

def cliquer_fleche_4_fois(driver):
    """Clique 4 fois sur le bouton flèche de droite avec des pauses animées."""
    print("-> Début des 4 clics sur la flèche de droite...")
    try:
        # L'ajout des parenthèses et du [2] à la fin cible STRICTEMENT la 2ème flèche (celle de droite)
        selecteur_xpath = "(//button[contains(@class, 'w-12') and contains(@class, 'rounded-full')])[2]"
        
        for i in range(4):
            pause = calculer_temps_aleatoire(4, 2.5)
            actions = ActionChains(driver)
            simuler_mouvement_souris_organique(driver, actions, pause)
            
            fleche = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, selecteur_xpath))
            )
            fleche.click()
            print(f"   Clic flèche {i+1}/4 effectué.")
            
    except Exception as e:
        print(f"-> Erreur sur les clics flèche : {e}")

def cliquer_bouton_continuez(driver):
    """Clique sur le bouton Continuer après une pause animée."""
    print("-> Recherche du bouton Continuer...")
    try:
        pause = calculer_temps_aleatoire(4, 2.5)
        # On remplace time.sleep par la fonction de mouvement
        actions = ActionChains(driver)
        simuler_mouvement_souris_organique(driver, actions, pause)
        
        selecteur_xpath = "//button[text()='Continuer']"
        
        bouton = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, selecteur_xpath))
        )
        bouton.click()
        print("-> Clic 'Continuer' effectué !")
    except Exception as e:
        print(f"-> Erreur clic Continuer : {e}")


# ==========================================
# 2. ORCHESTRATION DU PROGRAMME
# ==========================================

def lancer_bot():
    print("Démarrage du programme d'orchestration...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    driver = None # Initialisation vide

    while True:
        try:
            # 1. On vérifie si on doit (re)connecter le navigateur
            if driver is None:
                print("Connexion au navigateur Chrome en arrière-plan...")
                driver = webdriver.Chrome(options=options) 
                driver.get("https://www.wiki-masters.com/pulls") # Remplacez par votre URL
                print("Page chargée.")
                
                temps_initial = calculer_temps_aleatoire(11, 1)
                print("\nPause de démarrage...")
                actions = ActionChains(driver)
                simuler_mouvement_souris_organique(driver, actions, temps_initial)

            # 2. Début du cycle normal
            print("\n" + "="*40)
            print(f"NOUVEAU CYCLE DÉMARRÉ À {time.strftime('%H:%M:%S')}")
            duree_totale_visee = calculer_temps_aleatoire(660, 30)
            chrono_debut = time.time()

            # Exécution des actions
            cliquer_sur_bouton_principal(driver)
            cliquer_element_visuel_organique("input_cible.png")
            cliquer_fleche_4_fois(driver)
            cliquer_bouton_continuez(driver)

            # Calcul du temps d'attente
            temps_ecoule = time.time() - chrono_debut
            temps_restant = duree_totale_visee - temps_ecoule

            if temps_restant > 0:
                minutes = int(temps_restant // 60)
                secondes = int(temps_restant % 60)
                print(f"\nLes actions ont pris {temps_ecoule:.0f}s.")
                print(f"Attente du temps restant ({minutes}m {secondes}s)...")
                
                actions = ActionChains(driver)
                simuler_mouvement_souris_organique(driver, actions, temps_restant)
            else:
                print("\nLes actions ont pris plus de temps que prévu. Enchaînement direct !")

        # 3. LE FILET DE SÉCURITÉ EN CAS DE COUPURE
        except (InvalidSessionIdException, WebDriverException) as e:
            print(f"\n[ALERTE] Connexion avec Chrome perdue ({e}).")
            print("Tentative de reconnexion dans 10 secondes...")
            time.sleep(10)
            driver = None # Force le script à recréer la connexion au prochain tour de boucle
            
        except KeyboardInterrupt:
            print("\nInterruption demandée. Arrêt du bot.")
            break
            
        except Exception as e:
            print(f"\n[ERREUR INATTENDUE] {e}")
            time.sleep(5) # Petite pause avant de réessayer

if __name__ == "__main__":
    lancer_bot()