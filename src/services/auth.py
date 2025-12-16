import streamlit as st
from supabase import create_client, Client

# 1. Inizializzazione Client Supabase
# Legge URL e KEY direttamente dai secrets di Streamlit
# Usa @st.cache_resource per non riconnettersi a ogni click
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = get_supabase_client()

# 2. Funzioni di Autenticazione

def sign_in(email, password):
    """Esegue il Login. Ritorna l'oggetto sessione o lancia errore."""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email, 
            "password": password
        })
        return response
    except Exception as e:
        # Ritorna l'errore puro per gestirlo nella UI
        raise e

def sign_up(email, password):
    """Registra un nuovo utente."""
    try:
        response = supabase.auth.sign_up({
            "email": email, 
            "password": password
        })
        return response
    except Exception as e:
        raise e

def sign_out():
    """Effettua il Logout."""
    supabase.auth.sign_out()

def get_current_user():
    """
    Recupera l'utente dalla sessione attiva.
    Utile per verificare se il token è ancora valido.
    """
    session = supabase.auth.get_session()
    if session:
        return session.user
    return None