import streamlit as st
from . import config_tab, export_tab, import_tab, pdf_tab


@st.fragment
def render():
    st.header("⚙️ Gestione Dati e Configurazioni")

    user = st.session_state["user"]

    tab_config, tab_export, tab_import, tab_pdf = st.tabs([
        "🔧 Configurazioni",
        "📤 Esportazione Dati",
        "📥 Importazione Dati",
        "📄 Libretto Service",
    ])

    with tab_config:
        config_tab.render(user)

    with tab_export:
        export_tab.render(user)

    with tab_import:
        import_tab.render(user)

    with tab_pdf:
        pdf_tab.render(user)
