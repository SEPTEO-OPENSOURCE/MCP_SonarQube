"""Tests de compatibilité Windows pour le fix signal.SIGALRM."""

import os
import pytest


class TestWindowsCompatibility:
    """Tests pour vérifier la compatibilité Windows."""
    
    def test_mcp_server_import(self):
        """Test que MCPServer peut être importé sans erreur SIGALRM."""
        try:
            from src.mcp.server import MCPServer
            # Si l'import réussit, le test passe
            assert MCPServer is not None
        except AttributeError as e:
            if 'SIGALRM' in str(e):
                pytest.fail(f"SIGALRM AttributeError détecté: {e}")
            else:
                raise
    
    def test_no_signal_sigalrm_in_code(self):
        """Test que signal.SIGALRM a été retiré du code source."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        server_path = os.path.join(project_root, "src", "mcp", "server.py")
        
        with open(server_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "signal.SIGALRM" not in content, "signal.SIGALRM trouvé dans server.py"
        assert "signal.alarm" not in content, "signal.alarm trouvé dans server.py"
    
    def test_threading_used_for_timeout(self):
        """Test que threading.Thread est utilisé pour gérer les timeouts."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        server_path = os.path.join(project_root, "src", "mcp", "server.py")
        
        with open(server_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "threading.Thread" in content, "threading.Thread non trouvé dans server.py"
