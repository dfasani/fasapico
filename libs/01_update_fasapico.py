# update_fasapico.py
# MicroPython pour Raspberry Pi Pico W/W2
# Télécharge le package fasapico complet depuis GitHub et le place dans /lib du Pico W/W2.

import network
import time
import os

try:
    import urequests as requests
except Exception as e:
    raise ImportError("Le module urequests est requis. Installer une build MicroPython avec urequests.") from e

GITHUB_API = "https://api.github.com/repos/dfasani/fasapico/contents/fasapico"
SSID = "icam_iot"
PASSWORD = "Summ3#C@mp2022"
# Optional: set a GitHub Personal Access Token here to avoid API rate limits (if empty, we'll use unauthenticated requests)
# Create a token at https://github.com/settings/tokens with at least `repo` or `public_repo` scope for public repos.
GITHUB_TOKEN = ""  # e.g. "ghp_xxx..." or leave empty for unauthenticated

# Headers to send to the GitHub API. User-Agent is recommended by GitHub and helps avoid some rejections.
HEADERS = {
    "User-Agent": "MicroPython-Downloader",
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = "token {}".format(GITHUB_TOKEN)

# Retry configuration
MAX_RETRIES = 4
BACKOFF_FACTOR = 1.0  # seconds, multiplied by 2**attempt
# If True, the downloader will compare remote content with local file and skip
# writing if they are identical (saves flash writes and time).
SKIP_IF_IDENTICAL = True

def request_with_retries(url, headers=None, max_retries=MAX_RETRIES, backoff_factor=BACKOFF_FACTOR):
    """Perform a GET with simple exponential backoff retry for transient errors.

    Retries on network exceptions and on status codes 429 and 5xx.
    Does NOT retry on 403 (likely rate-limit or auth) to avoid repeated useless attempts.
    Returns the response object on success, or None on final failure.
    """
    attempt = 0
    while True:
        try:
            if headers is None:
                r = requests.get(url)
            else:
                r = requests.get(url, headers=headers)
        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                print("Requête échouée pour", url, ":", e)
                return None
            backoff = backoff_factor * (2 ** (attempt - 1))
            print("Erreur réseau pour", url, ", tentative", attempt, "/", max_retries, ", nouvelle tentative dans", backoff, "s")
            time.sleep(backoff)
            continue

        # If success, return response
        code = getattr(r, "status_code", None)
        if code == 200:
            return r

        # For 403, don't retry automatically: print message and return the response for caller to inspect
        if code == 403:
            return r

        # Retry on 429 or 5xx
        if code == 429 or (code is not None and 500 <= code < 600):
            attempt += 1
            try:
                info = r.json()
                msg = info.get("message")
            except Exception:
                msg = None
            r.close()
            if attempt > max_retries:
                print("Erreur API", code, "pour", url)
                if msg:
                    print("Message API:", msg)
                return None
            backoff = backoff_factor * (2 ** (attempt - 1))
            print("API temporairement indisponible (code", code, ") pour", url, ", tentative", attempt, "/", max_retries, ", nouvelle tentative dans", backoff, "s")
            time.sleep(backoff)
            continue

        # Other non-200 responses — return the response for the caller to handle
        return r

def connect_wifi(ssid, password, timeout=20):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    if not wlan.isconnected():
        print("Connexion au WiFi", ssid)
        wlan.connect(ssid, password)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                raise RuntimeError("Impossible de se connecter au WiFi (timeout).")
            time.sleep(0.5)
    print("Connecté, IP =", wlan.ifconfig()[0])

def makedirs(path):
    # crée récursivement les répertoires si inexistants
    parts = path.strip("/").split("/")
    cur = ""
    for p in parts:
        cur += "/" + p
        try:
            os.mkdir(cur)
        except OSError:
            # existe déjà ou impossible de créer -> on continue
            pass

def download_file(url, dest_path):
    print("Téléchargement:", url, "->", dest_path)
    r = request_with_retries(url, headers=HEADERS)
    if not r:
        return False
    if r.status_code != 200:
        try:
            msg = r.json().get("message")
        except Exception:
            msg = None
        print("Erreur HTTP", r.status_code, "pour", url)
        if msg:
            print("Message API:", msg)
        r.close()
        return False
    data = r.content
    r.close()

    # si le fichier local existe et que son contenu est identique, on saute l'écriture
    if SKIP_IF_IDENTICAL:
        try:
            with open(dest_path, "rb") as f:
                existing = f.read()
        except Exception:
            existing = None
        if existing is not None and existing == data:
            print("Fichier existant identique, saut:", dest_path)
            return True

    # écrire en binaire de façon plus sûre: écrire dans un fichier temporaire puis renommer
    tmp_path = dest_path + ".tmp"
    try:
        with open(tmp_path, "wb") as f:
            f.write(data)
        # remplacer l'ancien fichier de façon atomique si possible
        try:
            # supprimer l'ancien fichier si présent (rename may overwrite on some ports)
            os.remove(dest_path)
        except Exception:
            pass
        os.rename(tmp_path, dest_path)
    except Exception as e:
        print("Erreur écriture fichier:", e)
        # tenter de supprimer le tmp en échec
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        return False
    return True

def download_directory_recursive(api_url, local_dir):
    """Télécharge récursivement un répertoire depuis l'API GitHub.
    
    Args:
        api_url: URL de l'API GitHub pour le contenu du répertoire
        local_dir: Chemin local où sauvegarder les fichiers
    """
    print("Listing:", api_url)
    r = request_with_retries(api_url, headers=HEADERS)
    if not r:
        return False
    if r.status_code != 200:
        try:
            info = r.json()
            msg = info.get("message")
        except Exception:
            msg = None
        print("Erreur API", r.status_code)
        if msg:
            print("Message API:", msg)
            if r.status_code == 403:
                print("Si c'est une limitation d'API, créez un Personal Access Token et assignez la variable GITHUB_TOKEN dans ce script.")
        r.close()
        return False
    items = r.json()
    r.close()
    
    # s'assurer que le répertoire local existe
    makedirs(local_dir)
    
    success = True
    for item in items:
        itype = item.get("type")
        name = item.get("name")
        if not name:
            continue
        
        if itype == "file":
            download_url = item.get("download_url")
            if not download_url:
                print("Pas d'URL de téléchargement pour", name)
                continue
            dest = local_dir.rstrip("/") + "/" + name
            if not download_file(download_url, dest):
                success = False
        elif itype == "dir":
            # Récursion dans le sous-répertoire
            sub_api_url = item.get("url")
            if not sub_api_url:
                print("Pas d'URL API pour le sous-répertoire", name)
                continue
            sub_local_dir = local_dir.rstrip("/") + "/" + name
            if not download_directory_recursive(sub_api_url, sub_local_dir):
                success = False
    
    return success

def download_single_file_from_repo(repo_path, dest_path):
    print(f"Récupération des infos pour {repo_path}...")
    api_url = f"https://api.github.com/repos/dfasani/fasapico/contents/{repo_path}"
    r = request_with_retries(api_url, headers=HEADERS)
    if not r:
        return
    
    if r.status_code != 200:
        print(f"Impossible de récupérer les infos du fichier {repo_path} (Code {r.status_code})")
        r.close()
        return

    try:
        data = r.json()
        download_url = data.get("download_url")
    except Exception as e:
        print("Erreur parsing JSON:", e)
        r.close()
        return
    r.close()

    if not download_url:
        print(f"Pas de download_url pour {repo_path}")
        return

    download_file(download_url, dest_path)

def main():
    ssid = SSID
    password = PASSWORD
    
    # Try to load from secrets.py (locally existing)
    try:
        import secrets
        ssid = getattr(secrets, 'ssid', SSID)
        password = getattr(secrets, 'password', PASSWORD)
        print("Paramètres WiFi chargés depuis secrets.py local")
    except ImportError:
        print("secrets.py non trouvé localement, utilisation des paramètres par défaut")

    if ssid == "VOTRE_SSID" or password == "VOTRE_MOT_DE_PASSE":
        raise SystemExit("Remplir SSID et PASSWORD dans le script avant exécution.")
    
    connect_wifi(ssid, password)
    
    # 1. Télécharger le package fasapico complet -> /lib/fasapico/
    print("\n=== Téléchargement du package fasapico ===")
    download_directory_recursive(GITHUB_API, "/lib/fasapico")
    
    # 2. Récupérer secrets.py -> /secrets.py
    # On suppose que secrets.py est à la racine du repo
    print("\n=== Téléchargement de secrets.py ===")
    download_single_file_from_repo("secrets.py", "/secrets.py")

    print("\n=== Mise à jour terminée. ===")

if __name__ == "__main__":
    main()
