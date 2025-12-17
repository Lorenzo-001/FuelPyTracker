import sys
import os
import tomllib
import time
import random
from unittest.mock import MagicMock

# --- 1. CONFIGURAZIONE PATH DINAMICA ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))

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
from src.services.auth import (
    sign_in, sign_up, sign_out, get_current_user, 
    update_user_password_secure, update_user_email
)

def run_cli_test():
    print(f"\n🧪  AVVIO UNIT TEST: AUTH SERVICE")
    print("--------------------------------------------------")
    
    # FIX: Usiamo @example.com per evitare che Supabase invii mail reali e vada in errore
    random_id = int(time.time()) + random.randint(1, 1000)
    test_email = f"fuel.tester.{random_id}@example.com"
    test_password = "PasswordSicura123!" 

    print(f"📧 Email generata per il test: {test_email}")

    # TEST A: REGISTRAZIONE
    print(f"\n1. [Sign Up] Tentativo registrazione...")
    try:
        res = sign_up(test_email, test_password)
        user_created = getattr(res, 'user', None) or (res if hasattr(res, 'id') else None)
        
        if user_created: 
            print(f"   ✅ Registrazione OK. ID: {user_created.id}")
        else:
            print("   ⚠️  Warning: Utente creato ma oggetto vuoto.")
    except Exception as e:
        print(f"   ❌ Errore Registrazione: {e}")

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

    # TEST EXTRA: CAMBIO PASSWORD
    print(f"\n3b. [Security] Test Cambio Password...")
    new_password = "NuovaPasswordSicura456!"
    
    # Tentativo 1: Vecchia password errata (Deve fallire)
    res_fail, msg_fail = update_user_password_secure(test_email, "PasswordSbagliata", new_password)
    if not res_fail:
        print("   ✅ Blocco sicurezza OK: Cambio rifiutato con vecchia password errata.")
    else:
        print("   ❌ ERRORE: Password cambiata senza verifica della vecchia!")

    # Tentativo 2: Vecchia password corretta (Deve riuscire)
    res_ok, msg_ok = update_user_password_secure(test_email, test_password, new_password)
    if res_ok:
        print(f"   ✅ Cambio Password richiesto con successo: {msg_ok}")
        
        # VERIFICA REALE: Logout e Login con la NUOVA password
        print("      🔄 Verifica accesso con NUOVA password...")
        sign_out()
        try:
            res_new_login = sign_in(test_email, new_password)
            if res_new_login.user:
                print("      ✅ Login con NUOVA password riuscito!")
            else:
                print("      ❌ Login con nuova password fallito.")
        except Exception as e:
             print(f"      ❌ Eccezione login nuova pass: {e}")
             return
    else:
        print(f"   ❌ Errore cambio password: {msg_ok}")

    # TEST D: LOGOUT
    print(f"\n4. [Sign Out] Logout...")
    sign_out()
    if get_current_user() is None:
        print("   ✅ Logout effettuato con successo.")
    else:
        print("   ❌ Logout fallito (Utente ancora attivo).")

if __name__ == "__main__":
    run_cli_test()