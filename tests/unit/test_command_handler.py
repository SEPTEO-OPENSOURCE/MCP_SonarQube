"""Tests unitaires pour CommandHandler."""

import pytest
from unittest.mock import Mock
from src.commands import CommandHandler
from src.config import SonarQubeConfig, ProjectConfig


@pytest.fixture
def mock_api():
    """Mock de l'API."""
    return Mock()


@pytest.fixture
def config():
    """Configuration test."""
    config = SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test_token"
    )
    config.default_project = ProjectConfig(key="test-project")
    return config


@pytest.fixture
def handler(mock_api, config):
    """Handler avec mocks."""
    return CommandHandler(mock_api, config)


class TestCommandHandler:
    """Tests du CommandHandler."""
    
    def test_init(self, handler):
        """Test initialisation."""
        assert handler.api is not None
        assert handler.config is not None
        assert handler.issues is not None
        assert handler.measures is not None
        assert handler.security is not None
        assert handler.projects is not None
        assert handler.users is not None
        assert len(handler.commands) > 0
    
    def test_execute_valid_command(self, handler):
        """Test execute avec commande valide."""
        # Mock la commande version
        handler.projects.get_version = Mock(return_value=Mock(
            success=True,
            data={'version': '1.0.0'}
        ))
        
        result = handler.execute('version', [])
        
        assert result.success is True
    
    def test_execute_invalid_command(self, handler):
        """Test execute avec commande invalide."""
        result = handler.execute('invalid-command', [])
        
        assert result.success is False
        assert 'inconnue' in result.error.lower()
    
    def test_execute_command_alias(self, handler):
        """Test execute_command (alias)."""
        handler.projects.get_version = Mock(return_value=Mock(
            success=True,
            data={'version': '1.0.0'}
        ))
        
        result = handler.execute_command('version', [])
        
        assert result.success is True
    
    def test_help_general(self, handler):
        """Test aide générale."""
        result = handler._help([])
        
        assert result.success is True
        assert 'commands' in result.data
        assert 'usage' in result.data
    
    def test_help_specific_command(self, handler):
        """Test aide commande spécifique."""
        result = handler._help(['version'])
        
        assert result.success is True
        assert 'command' in result.data
        assert result.data['command'] == 'version'
    
    def test_help_unknown_command(self, handler):
        """Test aide commande inconnue."""
        result = handler._help(['unknown'])
        
        assert result.success is False
    
    def test_all_commands_registered(self, handler):
        """Test que toutes les commandes sont enregistrées."""
        # Issues
        assert 'issues' in handler.commands
        assert 'my-issues' in handler.commands
        assert 'mine' in handler.commands
        assert 'issue-changelog' in handler.commands
        assert 'issues-by-type' in handler.commands
        assert 'issues-by-severity' in handler.commands
        assert 'bugs' in handler.commands
        assert 'vulnerabilities' in handler.commands
        assert 'code-smells' in handler.commands
        
        # Measures
        assert 'measures' in handler.commands
        assert 'metrics' in handler.commands
        
        # Security
        assert 'hotspots' in handler.commands
        assert 'security-hotspots' in handler.commands
        
        # Projects
        assert 'project-info' in handler.commands
        assert 'projects' in handler.commands
        assert 'quality-gate' in handler.commands
        assert 'health' in handler.commands
        assert 'version' in handler.commands
        
        # Users & Rules
        assert 'users' in handler.commands
        assert 'search-users' in handler.commands
        assert 'rule' in handler.commands
        assert 'rules' in handler.commands
        
        # Help
        assert 'help' in handler.commands
        assert 'commands' in handler.commands
    
    def test_aliases_point_to_same_function(self, handler):
        """Test que les alias pointent vers les bonnes fonctions."""
        # Les alias sont des références à la même fonction
        assert handler.commands['mine'] == handler.commands['my-issues']
        assert handler.commands['metrics'] == handler.commands['measures']
        assert handler.commands['security-hotspots'] == handler.commands['hotspots']
        assert handler.commands['search-users'] == handler.commands['users']
        assert handler.commands['commands'] == handler.commands['help']
    
    def test_execute_with_exception(self, handler):
        """Test execute quand commande lève exception."""
        # Mock pour que la commande retourne une fonction qui lève une exception
        def raise_exception(args):
            raise Exception("Test error")
        
        handler.commands['version'] = raise_exception
        
        result = handler.execute('version', [])
        
        assert result.success is False
        assert 'erreur' in result.error.lower()

