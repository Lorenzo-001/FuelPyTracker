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