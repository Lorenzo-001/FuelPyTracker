import time
import logging

from src.services.auth.auth_service import get_client

logger = logging.getLogger(__name__)

# =============================================================================
# GESTIONE STORAGE UTENTE (AVATAR)
# =============================================================================

def upload_avatar(user_id: str, file) -> str | None:
    """
    Carica o sovrascrive l'avatar dell'utente nel bucket 'avatars'.
    
    Args:
        user_id (str): UUID dell'utente autenticato.
        file: Oggetto file-like o bytes.

    Returns:
        str | None: URL pubblico con timestamp per cache-busting, o None in caso di errore.
    """
    try:
        file_path = f"{user_id}/avatar.png"
        
        # Estrai bytes dal file o buffer
        if hasattr(file, "getvalue"):
            file_bytes = file.getvalue()
        elif hasattr(file, "read"):
            file_bytes = file.read()
        elif isinstance(file, (bytes, bytearray)):
            file_bytes = bytes(file)
        else:
            raise ValueError("Formato file non supportato per l'upload dell'avatar.")
        
        client = get_client()
        if not client:
            return None

        # 'upsert': 'true' forza la sovrascrittura del file esistente
        client.storage.from_("avatars").upload(
            file_path, 
            file_bytes, 
            file_options={"content-type": "image/png", "upsert": "true"}
        )
        
        # Recupero URL Pubblico (il bucket 'avatars' deve essere impostato come "Public" su Supabase)
        public_url = client.storage.from_("avatars").get_public_url(file_path)
        
        # Cache Busting dinamico
        return f"{public_url}?t={int(time.time())}"

    except Exception as e:
        logger.warning("[Storage Error] Upload avatar fallito per user %s: %s", user_id, e)
        return None


def get_avatar_url(user_id: str) -> str | None:
    """
    Recupera l'URL dell'avatar utente se esistente.
    """
    try:
        file_path = f"{user_id}/avatar.png"
        client = get_client()
        if not client:
            return None
        return client.storage.from_("avatars").get_public_url(file_path)
    except Exception:
        return None