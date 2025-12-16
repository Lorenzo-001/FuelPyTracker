import sys
import os
import tomllib
import time
import random
from unittest.mock import MagicMock

# --- 1. CONFIGURAZIONE PATH DINAMICA ---
# Calcoliamo la root del progetto partendo da dove si trova questo file.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))

# Aggiungiamo la root al System Path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- 2. CARICAMENTO MANUALE SECRETS ---
secrets_path = os.path.join(project_root, ".streamlit", "secrets.toml")

if not os.path.exists(secrets_path):
    print(f"❌ ERRORE CRITICO: Non trovo il file secrets in: {secrets_path}")
    sys.exit(1)

try:
    with open(secrets_path, "rb") as f:
        real_secrets = tomllib.load(f)
except Exception as e:
    print(f"❌ Errore lettura TOML: {e}")
    sys.exit(1)

# --- 3. MOCKING DI STREAMLIT ---
mock_st = MagicMock()
mock_st.secrets = real_secrets

def pass_through_decorator(func):
    return func

mock_st.cache_resource = pass_through_decorator
sys.modules["streamlit"] = mock_st

# --- 4. IMPORT DEL SERVIZIO ---
from src.services.auth import sign_in, sign_up, sign_out, get_current_user

def run_cli_test():
    print(f"\n🧪  AVVIO UNIT TEST: AUTH SERVICE")
    print("--------------------------------------------------")
    
    # MODIFICA: Generiamo una email realistica e univoca
    # Usa un timestamp + numero random per evitare "User already registered"
    random_id = int(time.time()) + random.randint(1, 1000)
    test_email = f"fuel.tester.{random_id}@gmail.com"
    test_password = "PasswordSicura123!" 

    print(f"📧 Email generata per il test: {test_email}")

    # TEST A: REGISTRAZIONE
    print(f"\n1. [Sign Up] Tentativo registrazione...")
    try:
        res = sign_up(test_email, test_password)
        # Controllo robusto della risposta
        user_created = getattr(res, 'user', None) or (res if hasattr(res, 'id') else None)
        
        if user_created: 
            print(f"   ✅ Registrazione OK. ID: {user_created.id}")
        else:
            print("   ⚠️  Warning: Utente creato ma oggetto vuoto (Controlla 'Confirm Email' su Supabase).")
    except Exception as e:
        print(f"   ❌ Errore Registrazione: {e}")
        # Se fallisce la registrazione, proviamo comunque il login (magari esisteva già)

    # TEST B: LOGIN
    print(f"\n2. [Sign In] Tentativo Login...")
    try:
        res_login = sign_in(test_email, test_password)
        if res_login.user:
            print(f"   ✅ Login OK! Token ricevuto.")
        else:
            print(f"   ❌ Login Fallito (Nessun User object).")
            return
    except Exception as e:
        print(f"   ❌ Errore Login Exception: {e}")
        print("      (Controlla che l'utente esista e la password sia corretta)")
        return 

    # TEST C: SESSIONE
    print(f"\n3. [Session] Verifica sessione attiva...")
    try:
        curr = get_current_user()
        if curr:
            print(f"   ✅ Sessione Attiva confermata per: {curr.email}")
        else:
            print(f"   ❌ Nessuna sessione trovata.")
    except Exception as e:
        print(f"   ❌ Errore check sessione: {e}")

    # TEST D: LOGOUT
    print(f"\n4. [Sign Out] Logout...")
    sign_out()
    if get_current_user() is None:
        print("   ✅ Logout effettuato con successo.")
    else:
        print("   ❌ Logout fallito (Utente ancora attivo).")

if __name__ == "__main__":
    run_cli_test()