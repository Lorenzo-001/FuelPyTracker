"""
Unit test per la sincronizzazione dello stato di navigazione nel dialog Check-Up Salute Auto.
"""
from unittest.mock import patch
import importlib
import pytest
import streamlit as st

def test_health_dialog_navigates_and_syncs_sidebar_state():
    with patch("streamlit.dialog", lambda *args, **kwargs: (lambda func: func)):
        from src.ui.components.dashboard import dashboard
        importlib.reload(dashboard)

        st.session_state.current_page = "Dashboard"
        st.session_state.nav_radio_main = "Dashboard"
        st.session_state.nav_radio_account = None

        with patch.object(dashboard.st, "button", return_value=True), \
             patch.object(dashboard.st, "rerun") as mock_rerun, \
             patch.object(dashboard.st, "markdown"), \
             patch.object(dashboard.st, "warning"), \
             patch.object(dashboard.st, "error"), \
             patch.object(dashboard.st, "divider"), \
             patch.object(dashboard.st, "info"), \
             patch.object(dashboard.st, "balloons"):

            dashboard._render_health_dialog(score=60, issues=["Scadenza bollo"])

            assert st.session_state.current_page == "Manutenzione"
            assert st.session_state.nav_radio_main == "Manutenzione"
            assert st.session_state.nav_radio_account is None
            mock_rerun.assert_called_once()
