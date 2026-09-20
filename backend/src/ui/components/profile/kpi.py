import streamlit as st

# ==========================================
# SEZIONE: PROFILO UTENTE
# ==========================================

def _inject_custom_css():
    """
    Inietta CSS personalizzato per la UI del profilo.
    Modifiche: Avatar quadrato arrotondato e Nome utente in evidenza.
    """
    st.markdown("""
    <style>
        /* --- Container Principale Card (Glassmorphism) --- */
        .profile-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02));
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5);
            margin-bottom: 25px;
            display: flex;
            flex-direction: row;
            align-items: center;
            gap: 35px;
            transition: transform 0.2s ease-in-out;
        }

        /* --- Avatar Styling (Quadrato Arrotondato) --- */
        .avatar-container {
            flex-shrink: 0;
            position: relative;
            /* Definiamo le dimensioni anche sul container per stabilità */
            width: 150px;
            height: 150px;
        }
        
        .avatar-img {
            width: 100%;   /* Occupa tutto il container */
            height: 100%;  /* Occupa tutto il container */
            
            /* FIX: 'cover' taglia l'immagine per riempire il box (zoom) eliminando bande grigie */
            object-fit: cover !important; 
            object-position: center !important; /* Centra l'immagine se viene tagliata */
            
            display: block; /* Rimuove spazi fantasma inline */
            border-radius: 28px; 
            
            /* Stile Bordo "Fluo" */
            border: 3px solid #FF4B4B; 
            box-shadow: 0 0 25px rgba(255, 75, 75, 0.4);
            
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .avatar-img:hover {
            transform: scale(1.03) rotate(2deg);
            box-shadow: 0 0 35px rgba(255, 75, 75, 0.6);
            border-color: #FF8F8F;
        }

        /* --- User Info Styling --- */
        .user-info {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow: hidden; /* Previene overflow orizzontale su mobile */
        }

        /* Nome/Email in Grande Evidenza */
        .user-email-title {
            font-family: 'Helvetica Neue', sans-serif;
            margin: 0 0 10px 0;
            line-height: 1.1;
            
            background: -webkit-linear-gradient(45deg, #FFFFFF, #FF4B4B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            
            filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5));
        }

        .stats-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .stat-badge {
            display: inline-flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.08);
            padding: 6px 14px;
            border-radius: 12px;
            font-size: 0.9rem;
            color: #e0e0e0;
            border: 1px solid rgba(255, 255, 255, 0.05);
            font-weight: 500;
        }

        /* --- Mobile Responsiveness --- */
        @media only screen and (max-width: 600px) {
            .profile-card {
                flex-direction: column;
                text-align: center;
                padding: 25px 15px;
                gap: 20px;
            }
            
            .avatar-container {
                width: 130px;
                height: 130px;
            }
            
            /* L'immagine eredita 100% dal container modificato sopra */
            .avatar-img {
                border-radius: 24px;
            }

            .user-info {
                width: 100%;
                align-items: center;
            }

            .user-email-title {
                font-size: 1.6rem; 
            }

            .stats-container {
                justify-content: center;
            }
            
            .stat-badge {
                width: 100%; 
                justify-content: center;
            }
        }
    </style>
    """, unsafe_allow_html=True)