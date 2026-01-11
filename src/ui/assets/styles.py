import streamlit as st

def inject_js_bridge():
    """
    Inietta lo script JS per il bypass dell'hash fragment.
    Gestisce:
    1. Token valido -> Mostra Overlay per login sicuro
    2. Errore (Link scaduto) -> Pulisce URL e nasconde tutto
    3. Navigazione normale -> Nasconde tutto
    """
    st.components.v1.html("""
    <!DOCTYPE html>
    <html>
        <head>
            <style>
                body { 
                    font-family: sans-serif; 
                    text-align: center; 
                    background-color: #0e1117; 
                    color: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }
                .btn {
                    display: inline-block; 
                    padding: 15px 30px;
                    background-color: #FF4B4B; 
                    color: white;
                    text-decoration: none; 
                    border-radius: 8px;
                    font-weight: bold; 
                    font-size: 18px;
                    border: 1px solid #ff6c6c;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                    cursor: pointer;
                }
                .btn:hover { background-color: #D93636; }
                #status-box { display: none; text-align: center; }
            </style>
        </head>
        <body>
            <div id="status-box">
                <h2 style="margin-bottom: 20px;">🔐 Recupero Credenziali</h2>
                <a id="login-link" href="#" target="_blank" class="btn" onclick="handleLinkClick()">
                    🔓 Clicca qui per Resettare la Password
                </a>
                <p style="font-size: 14px; color: #aaa; margin-top: 15px;">
                    La procedura continuerà in una <b>nuova scheda</b>.
                </p>
            </div>
            
            <script>
                function handleLinkClick() {
                    setTimeout(function() {
                        document.body.innerHTML = "<div style='margin-top:20%; color:#aaa;'>✅ Procedura avviata.<br>Puoi chiudere questa scheda.</div>";
                        window.close();
                    }, 500);
                }

                try {
                    // Accesso agli elementi
                    var frame = window.frameElement;
                    var hash = window.parent.location.hash; // Usa window.parent per leggere l'URL principale
                    
                    console.log("FuelPyTracker Auth Bridge - Hash rilevato:", hash);

                    // --- CASO 1: TOKEN TROVATO (Mostra Overlay) ---
                    if (hash && hash.includes('access_token')) {
                        console.log("-> Token trovato. Attivazione Bridge.");
                        document.getElementById("status-box").style.display = "block";
                        
                        var fragment = hash.substring(1);
                        // Costruiamo il nuovo URL sostituendo # con ?
                        var newUrl = window.parent.location.origin + window.parent.location.pathname + '?' + fragment;
                        
                        document.getElementById("login-link").href = newUrl;

                        // Espandiamo l'iframe a tutto schermo
                        if (frame) {
                            frame.style.position = "fixed";
                            frame.style.top = "0";
                            frame.style.left = "0";
                            frame.style.width = "100vw";
                            frame.style.height = "100vh";
                            frame.style.zIndex = "999999";
                            frame.style.backgroundColor = "#0e1117";
                        }
                    } 
                    // --- CASO 2: ERRORE NELL'URL (Pulizia) ---
                    else if (hash && hash.includes('error=')) {
                        console.log("-> Errore rilevato (link scaduto?). Pulizia URL.");
                        
                        // FIX: Usiamo window.parent.history per pulire l'URL del browser principale
                        // Il try-catch serve perché alcuni browser bloccano questa azione per sicurezza
                        try {
                            window.parent.history.replaceState(null, null, window.parent.location.pathname + window.parent.location.search);
                        } catch(err) {
                            console.warn("Impossibile pulire URL (Sandbox restriction):", err);
                        }

                        // Nascondiamo l'iframe
                        if (frame) frame.style.display = "none";
                    } 
                    // --- CASO 3: NORMALE (Nascondi tutto) ---
                    else {
                        if (frame) frame.style.display = "none";
                    }

                } catch (e) {
                    console.error("Errore critico nello script Auth:", e);
                }
            </script>
        </body>
    </html>
    """, height=0)

def apply_custom_css():
    """Applica gli stili CSS globali dell'applicazione."""
    st.markdown("""
        <style>
            div[data-testid="stSidebar"] button[kind="primary"] { background-color: #FF4B4B; border-color: #FF4B4B; color: white; }
            div[data-testid="stSidebar"] button[kind="primary"]:hover { background-color: #D93636; border-color: #D93636; }
            .sidebar-user-card { background-color: #262730; padding: 15px; border-radius: 8px; border: 1px solid #444; display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
            .sidebar-user-avatar { width: 40px; height: 40px; background-color: #FF4B4B; color: white; border-radius: 6px; display: flex; justify-content: center; align-items: center; font-size: 20px; font-weight: bold; }
            .sidebar-user-info { display: flex; flex-direction: column; }
            .sidebar-user-name { font-weight: bold; font-size: 0.95rem; color: white; }
            .sidebar-user-role { font-size: 0.75rem; color: #aaa; }
            .stApp { background-color: #0e1117; }
        </style>
    """, unsafe_allow_html=True)

import streamlit as st

def apply_login_css():
    """
    Applica lo stile CSS avanzato per la pagina di login (Mobile-First).
    """
    st.markdown("""
        <style>
            /* 1. Nascondi Header e Footer di Streamlit */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* 2. Reset dei margini del contenitore principale */
            .block-container {
                margin-top: 0rem !important;    /* Spazio minimo in alto */
                padding-bottom: 0rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                max-width: 100%;
            }
            
            /* 3. Comportamento Mobile Specifico (< 600px) */
            @media only screen and (max-width: 600px) {
                .block-container {
                    margin-top: 10rem !important;
                    /* opzionale: spazio interno per non “attaccare” il bordo */
                    padding: 1rem;
                    margin: 1rem;
                }

                div[data-testid="stVerticalBlock"] {
                    gap: 0.5rem !important; 
                }

                button[data-testid="stBaseButton-secondary"] {
                    font-size: 0.8rem !important;
                    padding: 0px 10px !important;
                    min-height: 40px !important;
                }
            }

            /* 4. Comportamento Desktop (Centrato) */
            @media only screen and (min-width: 601px) {
                div[data-testid="stVerticalBlock"] {
                    max-width: 620px;
                    margin: 0 auto;
                    gap: 0.8rem !important;
                    padding-left: 1rem !important;
                    padding-right: 1rem !important;
                }
            }

            /* 5. Stile link "Password dimenticata" */
            button[kind="tertiary"] {
                color: #78909c !important;
                text-decoration: underline;
                font-size: 0.75rem !important;
                border: none !important;
                background: transparent !important;
                padding: 0 !important;
                margin-top: -5px !important;
                justify-content: center !important;
                height: auto !important;
            }
            button[kind="tertiary"]:hover {
                color: #4a6fa5 !important;
            }
        </style>
    """, unsafe_allow_html=True)

def render_login_header():
    """Renderizza l'header HTML della pagina di login."""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 10px;">
            <h2 style="margin: 0; padding: 0; font-size: 1.8rem;">⛽ FuelPyTracker</h2>
            <p style="margin: 0; padding: 0; color: #888; font-size: 0.85rem;">Il tuo diario di bordo digitale</p>
        </div>
    """, unsafe_allow_html=True)

def apply_sidebar_css():
    """
    Carica CSS personalizzato per migliorare l'estetica della sidebar.
    Nasconde i radio button standard e li trasforma in pulsanti menu.
    """
    st.markdown("""
        <style>
        /* Stile per i Radio Button trasformati in Menu */
        div.row-widget.stRadio > div {
            flex-direction: column;
            gap: 10px;
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            background-color: transparent;
            padding: 10px 15px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
            background-color: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.3);
        }
        /* Nasconde il pallino del radio button */
        div.row-widget.stRadio div[role="radiogroup"] > label > div:first-child {
            display: none;
        }
        
        /* --- NUOVO Stile Profilo Utente (Row Layout) --- */
        .profile-container {
            display: flex;
            align-items: center;
            padding: 12px;
            margin-bottom: 25px;
            margin-top: 10px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .profile-avatar {
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, #00C6FF, #0072FF); /* Gradiente Blu Tech */
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 1.1rem;
            margin-right: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        .profile-info {
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .profile-name {
            font-size: 0.9rem;
            font-weight: 600;
            color: #FFF;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .profile-role {
            font-size: 0.7rem;
            color: #AAA;
            margin-top: 2px;
        }

        /* --- Headers Sezioni --- */
        .nav-header {
            font-size: 1.05rem;
            font-style: oblique;
            font-weight: 700;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 15px;
            margin-bottom: 8px;
        }
        
        .version-footer {
            text-align: center;
            font-size: 0.75rem;
            color: #666;
            margin-top: 10px;
            font-family: monospace;
        }
        </style>
    """, unsafe_allow_html=True)