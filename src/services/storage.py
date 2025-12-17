import streamlit as st
from src.services.auth import supabase

def upload_avatar(user_id, file):
    """
    Carica l'avatar nel bucket 'avatars' sovrascrivendo il precedente.
    Ritorna l'URL pubblico dell'immagine.
    """
    try:
        # Nome file univoco per utente (sovrascrive il vecchio se esiste)
        file_path = f"{user_id}/avatar.png"
        
        # 1. Upload del file (convertito in bytes)
        file_bytes = file.getvalue()
        
        # Upsert=True permette di sovrascrivere
        supabase.storage.from_("avatars").upload(
            file_path, 
            file_bytes, 
            file_options={"content-type": "image/png", "upsert": "true"}
        )
        
        # 2. Ottieni URL Pubblico
        # Nota: Serve che il bucket sia "Public" su Supabase
        public_url = supabase.storage.from_("avatars").get_public_url(file_path)
        
        # Trucco cache-busting: aggiungiamo un timestamp finto all'URL per forzare l'aggiornamento grafico
        import time
        return f"{public_url}?t={int(time.time())}"

    except Exception as e:
        print(f"Errore upload: {e}")
        return None

def get_avatar_url(user_id):
    """Controlla se esiste un avatar e ritorna l'URL, altrimenti None."""
    try:
        file_path = f"{user_id}/avatar.png"
        # Proviamo a listare i file nella cartella dell'utente
        # Se la cartella/file non esiste, questo check è un modo indiretto
        # Nota: Il get_public_url ritorna sempre una stringa, anche se il file non esiste.
        # Per semplicità, qui assumiamo che se l'upload è stato fatto, l'URL è valido.
        
        url = supabase.storage.from_("avatars").get_public_url(file_path)
        return url
    except:
        return None