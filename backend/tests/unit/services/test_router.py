import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Aggiungiamo la root al path per importare i moduli src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importiamo la funzione da testare
from src.services.auth.router import handle_auth_redirects 

class TestRouterService(unittest.TestCase):

    def setUp(self):
        """Prepara l'ambiente prima di ogni test"""
        self.mock_session_state = {}

    def _configure_query_params(self, mock_st, params_dict):
        """
        Helper magico: Configura query_params per comportarsi come un dizionario
        (leggere valori) ma rimanere un Mock (per verificare .clear())
        """
        # Creiamo un nuovo Mock per query_params
        qp_mock = MagicMock()
        
        # Gli insegniamo a rispondere come il dizionario passato
        qp_mock.__getitem__.side_effect = params_dict.__getitem__
        qp_mock.get.side_effect = params_dict.get
        qp_mock.__contains__.side_effect = params_dict.__contains__
        
        # Assegniamo questo mock speciale a st.query_params
        mock_st.query_params = qp_mock

    @patch('src.services.auth.router.st')
    @patch('src.services.auth.router.exchange_code_for_session')
    def test_handle_pkce_flow_success(self, mock_exchange, mock_st):
        """Testa il caso in cui l'URL contiene ?code=... (PKCE Flow)"""
        
        # 1. SETUP: Usiamo l'helper invece di assegnare un dict brutale
        self._configure_query_params(mock_st, {"code": "fake_auth_code"})
        
        mock_st.session_state = self.mock_session_state
        
        fake_user = MagicMock(email="test@example.com")
        mock_exchange.return_value = (True, fake_user)

        # 2. ESECUZIONE
        handle_auth_redirects()

        # 3. ASSERZIONI
        mock_exchange.assert_called_once_with("fake_auth_code")
        self.assertEqual(self.mock_session_state['user'], fake_user)
        mock_st.toast.assert_called()
        
        # ORA FUNZIONA: Perché query_params è un Mock configurato, non un dict vero
        mock_st.query_params.clear.assert_called()
        mock_st.rerun.assert_called()

    @patch('src.services.auth.router.st')
    @patch('src.services.auth.router.set_session_from_url')
    def test_handle_implicit_flow_recovery_success(self, mock_set_session, mock_st):
        """Testa il caso ?access_token=...&type=recovery (Reset Password)"""
        
        # 1. SETUP
        self._configure_query_params(mock_st, {
            "access_token": "token123",
            "refresh_token": "refresh123",
            "type": "recovery"
        })
        
        mock_st.session_state = self.mock_session_state
        fake_user = MagicMock(email="test@example.com")
        mock_set_session.return_value = (True, fake_user)

        # 2. ESECUZIONE
        handle_auth_redirects()

        # 3. VERIFICHE
        mock_set_session.assert_called_once_with("token123", "refresh123")
        self.assertEqual(self.mock_session_state['user'], fake_user)
        self.assertTrue(self.mock_session_state['reset_password_mode'])
        mock_st.rerun.assert_called()

    @patch('src.services.auth.router.st')
    @patch('src.services.auth.router.exchange_code_for_session')
    def test_handle_error_case(self, mock_exchange, mock_st):
        """Testa il caso in cui il codice non è valido"""
        
        # 1. SETUP
        self._configure_query_params(mock_st, {"code": "invalid_code"})
        
        mock_exchange.return_value = (False, "Invalid Grant")
        mock_st.button.return_value = True # Simula click su "Torna al login"

        # 2. ESECUZIONE (Catturiamo lo StopIteration di st.stop se presente, o lasciamo scorrere)
        try:
            handle_auth_redirects()
        except StopIteration:
            pass

        # 3. VERIFICHE
        mock_st.error.assert_called() # Verifica che sia stato mostrato un errore
        mock_st.query_params.clear.assert_called()
        mock_st.rerun.assert_called()

if __name__ == '__main__':
    unittest.main()