import time

import streamlit as st

from src.services.auth.auth_service import supabase

# =============================================================================
# GESTIONE STORAGE UTENTE (AVATAR)
# =============================================================================

def upload_avatar(user_id: str, file) -> str | None:
    """
    Carica o sovrascrive l'avatar dell'utente nel bucket 'avatars'.
    
    Args:
        user_id (str): UUID dell'utente autenticato.
        file: Oggetto UploadedFile di Streamlit (bytes).

    Returns:
        str | None: URL pubblico con timestamp per cache-busting, o None in caso di errore.
    """
    try:
        # 1. Definizione Percorso
        # Nome file statico per utente per facilitare sovrascrittura
        file_path = f"{user_id}/avatar.png"
        
        # 2. Upload su Supabase Storage
        file_bytes = file.getvalue()
        
        # 'upsert': 'true' forza la sovrascrittura del file esistente
        supabase.storage.from_("avatars").upload(
            file_path, 
            file_bytes, 
            file_options={"content-type": "image/png", "upsert": "true"}
        )
        
        # 3. Recupero URL Pubblico
        # Prerequisito: Il bucket 'avatars' deve essere impostato come "Public" su Supabase
        public_url = supabase.storage.from_("avatars").get_public_url(file_path)
        
        # 4. Cache Busting
        # Aggiungiamo un query param dinamico per forzare il browser a ricaricare l'immagine
        return f"{public_url}?t={int(time.time())}"

    except Exception as e:
        print(f"[Storage Error] Upload fallito: {e}")
        return None


def get_avatar_url(user_id: str) -> str | None:
    """
    Recupera l'URL dell'avatar utente se esistente.
    
    Nota: Supabase get_public_url non verifica l'esistenza fisica del file,
    restituisce solo la stringa formattata.
    """
    try:
        file_path = f"{user_id}/avatar.png"
        
        # 1. Generazione URL
        # Assumiamo che se l'utente ha fatto l'upload, il path sia valido.
        url = supabase.storage.from_("avatars").get_public_url(file_path)
        return url
    except Exception:
        # Fallback silenzioso in caso di errori di connessione o config
        return None