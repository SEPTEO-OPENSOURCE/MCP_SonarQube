"""Tests unitaires pour la validation des inputs."""

import pytest
from src.utils import (
    validate_file_path, 
    validate_project_key, 
    validate_rule_key,
    validate_user_login,
    ValidationError
)


class TestValidateFilePath:
    """Tests de validation des chemins de fichiers."""
    
    def test_valid_file_path(self):
        """Teste des chemins de fichiers valides."""
        assert validate_file_path("lib/main.dart") == "lib/main.dart"
        assert validate_file_path("src/app.py") == "src/app.py"
        assert validate_file_path("folder/subfolder/file.txt") == "folder/subfolder/file.txt"
    
    def test_path_traversal_rejected(self):
        """Teste que le path traversal est rejeté."""
        with pytest.raises(ValidationError, match="Path traversal"):
            validate_file_path("../etc/passwd")
        
        with pytest.raises(ValidationError, match="Path traversal"):
            validate_file_path("folder/../../../secret")
        
        with pytest.raises(ValidationError, match="Path traversal"):
            validate_file_path("src/../../etc/shadow")
    
    def test_absolute_path_rejected(self):
        """Teste que les chemins absolus sont rejetés."""
        with pytest.raises(ValidationError, match="absolus interdits"):
            validate_file_path("/etc/passwd")
        
        with pytest.raises(ValidationError, match="absolus interdits"):
            validate_file_path("\\Windows\\System32")
    
    def test_empty_path_rejected(self):
        """Teste que les chemins vides sont rejetés."""
        with pytest.raises(ValidationError, match="vide"):
            validate_file_path("")
    
    def test_invalid_characters_rejected(self):
        """Teste que les caractères invalides sont rejetés."""
        with pytest.raises(ValidationError, match="invalides"):
            validate_file_path("file<test>.txt")
        
        with pytest.raises(ValidationError, match="invalides"):
            validate_file_path('file"test".txt')
        
        with pytest.raises(ValidationError, match="invalides"):
            validate_file_path("file|test.txt")


class TestValidateProjectKey:
    """Tests de validation des clés de projet."""
    
    def test_valid_project_key(self):
        """Teste des clés de projet valides."""
        assert validate_project_key("My.Project-Key_123") == "My.Project-Key_123"
        assert validate_project_key("simple") == "simple"
        assert validate_project_key("Project-1.2.3") == "Project-1.2.3"
        assert validate_project_key("MyProject.Mobile.App") == "MyProject.Mobile.App"
    
    def test_invalid_characters_rejected(self):
        """Teste que les caractères invalides sont rejetés."""
        with pytest.raises(ValidationError, match="invalide"):
            validate_project_key("My Project!")
        
        with pytest.raises(ValidationError, match="invalide"):
            validate_project_key("project@test")
        
        with pytest.raises(ValidationError, match="invalide"):
            validate_project_key("project#123")
        
        with pytest.raises(ValidationError, match="invalide"):
            validate_project_key("project/path")
    
    def test_empty_key_rejected(self):
        """Teste que les clés vides sont rejetées."""
        with pytest.raises(ValidationError, match="vide"):
            validate_project_key("")
    
    def test_too_long_key_rejected(self):
        """Teste que les clés trop longues sont rejetées."""
        long_key = "a" * 401
        with pytest.raises(ValidationError, match="trop longue"):
            validate_project_key(long_key)


class TestValidateRuleKey:
    """Tests de validation des clés de règle."""
    
    def test_valid_rule_key(self):
        """Teste des clés de règle valides."""
        assert validate_rule_key("dart:S1192") == "dart:S1192"
        assert validate_rule_key("python:S100") == "python:S100"
        assert validate_rule_key("javascript:NOSONAR") == "javascript:NOSONAR"
    
    def test_invalid_format_rejected(self):
        """Teste que les formats invalides sont rejetés."""
        with pytest.raises(ValidationError, match="Format.*invalide"):
            validate_rule_key("invalid")
        
        with pytest.raises(ValidationError, match="Format.*invalide"):
            validate_rule_key("nocolon")
    
    def test_empty_key_rejected(self):
        """Teste que les clés vides sont rejetées."""
        with pytest.raises(ValidationError, match="vide"):
            validate_rule_key("")
    
    def test_empty_parts_rejected(self):
        """Teste que les parties vides sont rejetées."""
        with pytest.raises(ValidationError, match="vide"):
            validate_rule_key(":S100")
        
        with pytest.raises(ValidationError, match="vide"):
            validate_rule_key("dart:")


class TestValidateUserLogin:
    """Tests de validation des logins utilisateur."""
    
    def test_valid_login(self):
        """Teste des logins valides."""
        assert validate_user_login("john.doe") == "john.doe"
        assert validate_user_login("user123") == "user123"
        assert validate_user_login("user_name") == "user_name"
        assert validate_user_login("user-name") == "user-name"
        assert validate_user_login("user@example.com") == "user@example.com"
        assert validate_user_login("developer-user12345") == "developer-user12345"
    
    def test_invalid_characters_rejected(self):
        """Teste que les caractères invalides sont rejetés."""
        with pytest.raises(ValidationError, match="invalide"):
            validate_user_login("user name")  # Espace
        
        with pytest.raises(ValidationError, match="invalide"):
            validate_user_login("user#name")  # Hash
        
        with pytest.raises(ValidationError, match="invalide"):
            validate_user_login("user/name")  # Slash
        
        with pytest.raises(ValidationError, match="invalide"):
            validate_user_login("<script>alert('xss')</script>")  # XSS
    
    def test_empty_login_rejected(self):
        """Teste que les logins vides sont rejetés."""
        with pytest.raises(ValidationError, match="vide"):
            validate_user_login("")
    
    def test_too_long_login_rejected(self):
        """Teste que les logins trop longs sont rejetés."""
        long_login = "a" * 256
        with pytest.raises(ValidationError, match="trop long"):
            validate_user_login(long_login)


class TestValidationIntegration:
    """Tests d'intégration des validations."""
    
    def test_multiple_validations_in_sequence(self):
        """Teste plusieurs validations à la suite."""
        # Toutes valides
        assert validate_file_path("lib/main.dart") == "lib/main.dart"
        assert validate_project_key("MyProject") == "MyProject"
        assert validate_rule_key("dart:S100") == "dart:S100"
        assert validate_user_login("john.doe") == "john.doe"
    
    def test_validation_errors_are_distinct(self):
        """Teste que les erreurs de validation sont distinctes."""
        # Path traversal
        try:
            validate_file_path("../passwd")
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "traversal" in str(e).lower()
        
        # Invalid project key
        try:
            validate_project_key("bad!key")
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "invalide" in str(e).lower()
        
        # Invalid rule format
        try:
            validate_rule_key("nocolon")
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "format" in str(e).lower()





