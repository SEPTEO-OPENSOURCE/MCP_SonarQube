"""Tests unitaires pour les commandes users et rules."""

import pytest
from unittest.mock import Mock
from src.commands.users import UsersCommands
from src.config import SonarQubeConfig
from src.api import SonarQubeAPIError
from src.models import User, Rule


@pytest.fixture
def mock_api():
    """Mock de l'API SonarQube."""
    return Mock()


@pytest.fixture
def config():
    """Configuration SonarQube."""
    return SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test_token"
    )


@pytest.fixture
def users_commands(mock_api, config):
    """Instance UsersCommands avec mocks."""
    return UsersCommands(mock_api, config)


class TestSearchUsersCommand:
    """Tests de la commande search_users()."""
    
    def test_search_users_with_results(self, users_commands, mock_api):
        """Test users avec résultats."""
        mock_users = [
            User(login='user1', name='User One', email='user1@test.com'),
            User(login='user2', name='User Two', email='user2@test.com')
        ]
        mock_api.search_users.return_value = mock_users
        
        result = users_commands.search_users(['john'])
        
        assert result.success is True
        assert result.metadata['total'] == 2
        mock_api.search_users.assert_called_once_with('john')
    
    def test_search_users_no_results(self, users_commands, mock_api):
        """Test users sans résultats."""
        mock_api.search_users.return_value = []
        
        result = users_commands.search_users(['nonexistent'])
        
        assert result.success is True
        assert result.metadata['total'] == 0
    
    def test_search_users_missing_query(self, users_commands):
        """Test users sans terme de recherche."""
        result = users_commands.search_users([])
        
        assert result.success is False
        assert 'Usage' in result.error
    
    def test_search_users_api_error(self, users_commands, mock_api):
        """Test users avec erreur API."""
        mock_api.search_users.side_effect = SonarQubeAPIError(
            status_code=500,
            message="Internal error"
        )
        
        result = users_commands.search_users(['test'])
        
        assert result.success is False


class TestGetRuleCommand:
    """Tests de la commande get_rule()."""
    
    def test_get_rule_existing(self, users_commands, mock_api):
        """Test rule avec règle existante."""
        from src.models import Severity
        mock_rule = Rule(
            key='dart:S1192',
            name='String literals should not be duplicated',
            lang='dart',
            severity=Severity.MAJOR,
            type='CODE_SMELL'
        )
        mock_api.get_rule.return_value = mock_rule
        
        result = users_commands.get_rule(['dart:S1192'])
        
        assert result.success is True
        assert result.data is not None
        mock_api.get_rule.assert_called_once_with('dart:S1192')
    
    def test_get_rule_nonexistent(self, users_commands, mock_api):
        """Test rule avec règle inexistante."""
        mock_api.get_rule.side_effect = SonarQubeAPIError(
            status_code=404,
            message="Rule not found"
        )
        
        result = users_commands.get_rule(['unknown:S999'])
        
        assert result.success is False
    
    def test_get_rule_missing_key(self, users_commands):
        """Test rule sans clé de règle."""
        result = users_commands.get_rule([])
        
        assert result.success is False
        assert 'Usage' in result.error
    
    def test_get_rule_api_error(self, users_commands, mock_api):
        """Test rule avec erreur API."""
        mock_api.get_rule.side_effect = SonarQubeAPIError(
            status_code=500,
            message="Internal error"
        )
        
        result = users_commands.get_rule(['dart:S1192'])
        
        assert result.success is False


class TestSearchRulesCommand:
    """Tests de la commande search_rules()."""
    
    def test_search_rules_with_query(self, users_commands, mock_api):
        """Test rules avec terme de recherche."""
        mock_api.search_rules.return_value = {
            'total': 5,
            'rules': [
                {'key': 'dart:S1', 'name': 'Rule 1'},
                {'key': 'dart:S2', 'name': 'Rule 2'}
            ]
        }
        
        result = users_commands.search_rules(['duplicat'])
        
        assert result.success is True
        assert result.data['total'] == 5
        mock_api.search_rules.assert_called_once_with(q='duplicat')
    
    def test_search_rules_without_query(self, users_commands, mock_api):
        """Test rules sans terme (toutes les règles)."""
        mock_api.search_rules.return_value = {
            'total': 1000,
            'rules': []
        }
        
        result = users_commands.search_rules([])
        
        assert result.success is True
        assert result.data['total'] == 1000
        mock_api.search_rules.assert_called_once_with(q=None)
    
    def test_search_rules_no_results(self, users_commands, mock_api):
        """Test rules sans résultats."""
        mock_api.search_rules.return_value = {
            'total': 0,
            'rules': []
        }
        
        result = users_commands.search_rules(['veryrareterm'])
        
        assert result.success is True
        assert result.data['total'] == 0
    
    def test_search_rules_api_error(self, users_commands, mock_api):
        """Test rules avec erreur API."""
        mock_api.search_rules.side_effect = SonarQubeAPIError(
            status_code=500,
            message="Internal error"
        )
        
        result = users_commands.search_rules(['test'])
        
        assert result.success is False

