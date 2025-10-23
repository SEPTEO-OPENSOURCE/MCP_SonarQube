"""Tests unitaires pour la sécurité du logging."""

import logging
import pytest
from sonarqube_mcp_server import TokenSanitizingFilter


class TestTokenSanitizingFilter:
    """Tests du filtre de sanitization des tokens."""
    
    def setup_method(self):
        """Initialise le filtre pour chaque test."""
        self.filter = TokenSanitizingFilter()
    
    def test_token_sonarqube_masked(self):
        """Vérifie que les tokens SonarQube sont masqués."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Authenticating with token=squ_abc123def456789012345678901234567890",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        assert "squ_abc" not in record.msg
        assert "***MASKED***" in record.msg
    
    def test_bearer_token_masked(self):
        """Vérifie que les tokens Bearer sont masqués."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        assert "eyJhbG" not in record.msg
        assert "***MASKED***" in record.msg
    
    def test_password_masked(self):
        """Vérifie que les mots de passe sont masqués."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='Connecting with password="MySuperSecretPassword123"',
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        assert "MySuperSecretPassword123" not in record.msg
        assert "***MASKED***" in record.msg
    
    def test_api_key_masked(self):
        """Vérifie que les API keys sont masqués."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="api_key: 1234567890abcdef",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        assert "1234567890abcdef" not in record.msg
        assert "***MASKED***" in record.msg
    
    def test_authorization_header_masked(self):
        """Vérifie que les headers d'autorisation sont masqués."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Authorization: Basic dXNlcjpwYXNzd29yZA==",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        # Pattern 4 remplace tout après "Authorization: " par ***MASKED***
        assert "dXNlcjpwYXNzd29yZA==" not in record.msg
        assert "Basic" not in record.msg
        assert "Authorization: ***MASKED***" in record.msg
    
    def test_multiple_tokens_masked(self):
        """Vérifie que plusieurs tokens dans le même message sont masqués."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="token=squ_abc123def456789012345678901234567890 and api_key=xyz789012345",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        # Les deux tokens ont plus de 10 caractères, donc devraient être masqués
        assert "squ_abc" not in record.msg
        assert "xyz789012345" not in record.msg
        assert record.msg.count("***MASKED***") >= 2
    
    def test_case_insensitive_matching(self):
        """Vérifie que le matching est insensible à la casse."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="TOKEN=mysecrettoken123 PASSWORD=mylongpassword",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        # Les deux ont plus de 10 caractères, donc devraient être masqués
        assert "mysecrettoken123" not in record.msg
        assert "mylongpassword" not in record.msg
    
    def test_args_sanitized(self):
        """Vérifie que les arguments de logging sont également sanitizés."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request: %s",
            args=("token=squ_secret123456789012345678901234567890",),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        assert "squ_secret" not in record.args[0]
        assert "***MASKED***" in record.args[0]
    
    def test_normal_text_not_affected(self):
        """Vérifie que le texte normal n'est pas affecté."""
        normal_msg = "This is a normal log message without any secrets"
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=normal_msg,
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        assert record.msg == normal_msg
    
    def test_short_tokens_not_masked(self):
        """Vérifie que les tokens courts (<10 caractères) ne sont pas masqués."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="token=short",
            args=(),
            exc_info=None
        )
        
        self.filter.filter(record)
        
        # Les tokens très courts ne devraient pas être masqués
        assert "short" in record.msg or "***MASKED***" in record.msg





