"""Tests unitaires pour les commandes issues."""

import pytest
from unittest.mock import Mock, MagicMock
from src.commands.issues import IssuesCommands
from src.config import SonarQubeConfig, ProjectConfig
from src.api import SonarQubeAPIError
from src.models import IssueType, Severity


@pytest.fixture
def mock_api():
    """Mock de l'API SonarQube."""
    return Mock()


@pytest.fixture
def config_with_defaults():
    """Configuration avec projet par défaut."""
    config = SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test_token"
    )
    config.default_project = ProjectConfig(
        key="test-project",
        name="Test Project",
        assignee="test-user"
    )
    return config


@pytest.fixture
def config_without_defaults():
    """Configuration sans projet par défaut."""
    config = SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test_token"
    )
    return config


@pytest.fixture
def issues_commands(mock_api, config_with_defaults):
    """Instance IssuesCommands avec mocks."""
    return IssuesCommands(mock_api, config_with_defaults)


class TestIssuesCommand:
    """Tests de la commande issues()."""
    
    def test_issues_no_args_with_config(self, issues_commands, mock_api):
        """Test issues sans arguments avec config par défaut."""
        mock_api.search_issues.return_value = {
            'total': 5,
            'issues': []
        }
        
        result = issues_commands.issues([])
        
        assert result.success is True
        assert result.data['total'] == 5
        assert result.metadata['project'] == 'test-project'
        assert result.metadata['assignee'] == 'test-user'
        assert result.metadata['mode'] == 'my-issues'
        mock_api.search_issues.assert_called_once_with(
            project_keys=['test-project'],
            assignees=['test-user'],
            resolved=False
        )
    
    def test_issues_no_args_without_project(self, mock_api, config_without_defaults):
        """Test issues sans arguments sans projet configuré."""
        commands = IssuesCommands(mock_api, config_without_defaults)
        
        result = commands.issues([])
        
        assert result.success is False
        assert 'SONARQUBE_PROJECT_KEY' in result.error
    
    def test_issues_no_args_without_user(self, mock_api):
        """Test issues sans arguments sans utilisateur configuré."""
        config = SonarQubeConfig(url="https://test.sonarqube.com", token="test_token")
        config.default_project = ProjectConfig(key="test-project")
        commands = IssuesCommands(mock_api, config)
        
        result = commands.issues([])
        
        assert result.success is False
        assert 'SONARQUBE_USER' in result.error
    
    def test_issues_one_arg_project_only(self, issues_commands, mock_api):
        """Test issues avec project_key uniquement."""
        mock_api.search_issues.return_value = {
            'total': 10,
            'issues': []
        }
        
        result = issues_commands.issues(['other-project'])
        
        assert result.success is True
        assert result.metadata['project'] == 'other-project'
        assert result.metadata['assignee'] is None
        mock_api.search_issues.assert_called_once_with(
            project_keys=['other-project'],
            assignees=None,
            files=None,
            resolved=False
        )
    
    def test_issues_two_args_project_and_assignee(self, issues_commands, mock_api):
        """Test issues avec project_key et assignee."""
        mock_api.search_issues.return_value = {
            'total': 3,
            'issues': []
        }
        
        result = issues_commands.issues(['project-x', 'user-y'])
        
        assert result.success is True
        assert result.metadata['project'] == 'project-x'
        assert result.metadata['assignee'] == 'user-y'
        mock_api.search_issues.assert_called_once_with(
            project_keys=['project-x'],
            assignees=['user-y'],
            files=None,
            resolved=False
        )
    
    def test_issues_three_args_with_file(self, issues_commands, mock_api):
        """Test issues avec project_key, assignee et file_path."""
        mock_api.search_issues.return_value = {
            'total': 1,
            'issues': []
        }
        
        result = issues_commands.issues(['project-x', 'user-y', 'src/main.dart'])
        
        assert result.success is True
        assert result.metadata['file_path'] == 'src/main.dart'
        mock_api.search_issues.assert_called_once_with(
            project_keys=['project-x'],
            assignees=['user-y'],
            files=['src/main.dart'],
            resolved=False
        )
    
    def test_issues_api_error(self, issues_commands, mock_api):
        """Test issues avec erreur API."""
        mock_api.search_issues.side_effect = SonarQubeAPIError(
            status_code=500,
            message="Server error"
        )
        
        result = issues_commands.issues(['project-x'])
        
        assert result.success is False
        assert 'erreur' in result.error.lower()


class TestMyIssuesCommand:
    """Tests de la commande my_issues()."""
    
    def test_my_issues_no_args_with_config(self, issues_commands, mock_api):
        """Test my-issues sans arguments avec config."""
        mock_api.search_issues.return_value = {
            'total': 7,
            'issues': []
        }
        
        result = issues_commands.my_issues([])
        
        assert result.success is True
        assert result.data['total'] == 7
        assert result.metadata['project'] == 'test-project'
        assert result.metadata['assignee'] == 'test-user'
    
    def test_my_issues_with_project_override(self, issues_commands, mock_api):
        """Test my-issues avec override de projet."""
        mock_api.search_issues.return_value = {'total': 2, 'issues': []}
        
        result = issues_commands.my_issues(['custom-project'])
        
        assert result.success is True
        assert result.metadata['project'] == 'custom-project'
        assert result.metadata['assignee'] == 'test-user'
    
    def test_my_issues_with_both_overrides(self, issues_commands, mock_api):
        """Test my-issues avec override projet et user."""
        mock_api.search_issues.return_value = {'total': 0, 'issues': []}
        
        result = issues_commands.my_issues(['custom-project', 'custom-user'])
        
        assert result.success is True
        assert result.metadata['project'] == 'custom-project'
        assert result.metadata['assignee'] == 'custom-user'
    
    def test_my_issues_without_config(self, mock_api, config_without_defaults):
        """Test my-issues sans configuration."""
        commands = IssuesCommands(mock_api, config_without_defaults)
        
        result = commands.my_issues([])
        
        assert result.success is False
        assert 'SONARQUBE_PROJECT_KEY' in result.error


class TestChangelogCommand:
    """Tests de la commande changelog()."""
    
    def test_changelog_success(self, issues_commands, mock_api):
        """Test changelog avec succès."""
        mock_api.get_issue_changelog.return_value = {
            'changelog': [{'date': '2024-01-01', 'changes': []}]
        }
        
        result = issues_commands.changelog(['ISSUE-123'])
        
        assert result.success is True
        assert 'changelog' in result.data
        mock_api.get_issue_changelog.assert_called_once_with('ISSUE-123')
    
    def test_changelog_no_args(self, issues_commands):
        """Test changelog sans arguments."""
        result = issues_commands.changelog([])
        
        assert result.success is False
        assert 'Usage' in result.error
    
    def test_changelog_api_error(self, issues_commands, mock_api):
        """Test changelog avec erreur API."""
        mock_api.get_issue_changelog.side_effect = SonarQubeAPIError(
            status_code=404,
            message="Issue not found"
        )
        
        result = issues_commands.changelog(['ISSUE-999'])
        
        assert result.success is False


class TestByTypeCommand:
    """Tests de la commande by_type()."""
    
    def test_by_type_bug(self, issues_commands, mock_api):
        """Test filtrage par type BUG."""
        mock_api.search_issues.return_value = {'total': 5, 'issues': []}
        
        result = issues_commands.by_type(['project-x', 'BUG'])
        
        assert result.success is True
        assert result.metadata['type'] == 'BUG'
        mock_api.search_issues.assert_called_once_with(
            project_keys=['project-x'],
            types=[IssueType.BUG],
            assignees=None,
            resolved=False
        )
    
    def test_by_type_with_assignee(self, issues_commands, mock_api):
        """Test filtrage par type avec assignee."""
        mock_api.search_issues.return_value = {'total': 2, 'issues': []}
        
        result = issues_commands.by_type(['project-x', 'VULNERABILITY', 'user-y'])
        
        assert result.success is True
        assert result.metadata['type'] == 'VULNERABILITY'
        mock_api.search_issues.assert_called_once()
        call_kwargs = mock_api.search_issues.call_args[1]
        assert call_kwargs['assignees'] == ['user-y']
    
    def test_by_type_invalid(self, issues_commands):
        """Test filtrage avec type invalide."""
        result = issues_commands.by_type(['project-x', 'INVALID_TYPE'])
        
        assert result.success is False
    
    def test_by_type_missing_args(self, issues_commands):
        """Test by_type avec arguments manquants."""
        result = issues_commands.by_type(['project-x'])
        
        assert result.success is False
        assert 'Usage' in result.error


class TestBySeverityCommand:
    """Tests de la commande by_severity()."""
    
    def test_by_severity_critical(self, issues_commands, mock_api):
        """Test filtrage par sévérité CRITICAL."""
        mock_api.search_issues.return_value = {'total': 3, 'issues': []}
        
        result = issues_commands.by_severity(['project-x', 'CRITICAL'])
        
        assert result.success is True
        assert result.metadata['severity'] == 'CRITICAL'
        mock_api.search_issues.assert_called_once_with(
            project_keys=['project-x'],
            severities=[Severity.CRITICAL],
            assignees=None,
            resolved=False
        )
    
    def test_by_severity_with_assignee(self, issues_commands, mock_api):
        """Test filtrage par sévérité avec assignee."""
        mock_api.search_issues.return_value = {'total': 1, 'issues': []}
        
        result = issues_commands.by_severity(['project-x', 'MAJOR', 'user-y'])
        
        assert result.success is True
        call_kwargs = mock_api.search_issues.call_args[1]
        assert call_kwargs['assignees'] == ['user-y']
    
    def test_by_severity_invalid(self, issues_commands):
        """Test filtrage avec sévérité invalide."""
        result = issues_commands.by_severity(['project-x', 'SUPER_CRITICAL'])
        
        assert result.success is False


class TestShortcutCommands:
    """Tests des commandes raccourcies."""
    
    def test_bugs_with_project(self, issues_commands, mock_api):
        """Test raccourci bugs avec projet."""
        mock_api.search_issues.return_value = {'total': 10, 'issues': []}
        
        result = issues_commands.bugs(['project-x'])
        
        assert result.success is True
        assert result.metadata['type'] == 'BUG'
    
    def test_bugs_without_project(self, issues_commands, mock_api):
        """Test raccourci bugs sans projet (utilise config)."""
        mock_api.search_issues.return_value = {'total': 5, 'issues': []}
        
        result = issues_commands.bugs([])
        
        assert result.success is True
        assert result.metadata['project'] == 'test-project'
    
    def test_bugs_without_config(self, mock_api, config_without_defaults):
        """Test raccourci bugs sans config."""
        commands = IssuesCommands(mock_api, config_without_defaults)
        
        result = commands.bugs([])
        
        assert result.success is False
    
    def test_vulnerabilities(self, issues_commands, mock_api):
        """Test raccourci vulnerabilities."""
        mock_api.search_issues.return_value = {'total': 0, 'issues': []}
        
        result = issues_commands.vulnerabilities(['project-x'])
        
        assert result.success is True
        assert result.metadata['type'] == 'VULNERABILITY'
    
    def test_code_smells(self, issues_commands, mock_api):
        """Test raccourci code-smells."""
        mock_api.search_issues.return_value = {'total': 20, 'issues': []}
        
        result = issues_commands.code_smells(['project-x'])
        
        assert result.success is True
        assert result.metadata['type'] == 'CODE_SMELL'


class TestSearchIssuesCommand:
    """Tests de la commande search_issues()."""
    
    def test_search_issues_all_issues(self, issues_commands, mock_api):
        """Test recherche de toutes les issues d'un projet."""
        mock_api.search_issues.return_value = {
            'total': 42,
            'issues': []
        }
        
        result = issues_commands.search_issues(['project-x'])
        
        assert result.success is True
        assert result.data['total'] == 42
        assert result.metadata['project'] == 'project-x'
        assert result.metadata['filter'] == 'all'
        mock_api.search_issues.assert_called_once_with(
            project_keys=['project-x'],
            assignees=None,
            statuses=None
        )
    
    def test_search_issues_with_assignee(self, issues_commands, mock_api):
        """Test recherche des issues assignées à un utilisateur spécifique."""
        mock_api.search_issues.return_value = {
            'total': 15,
            'issues': []
        }
        
        result = issues_commands.search_issues(['project-x', 'john.doe'])
        
        assert result.success is True
        assert result.data['total'] == 15
        assert result.metadata['project'] == 'project-x'
        assert result.metadata['assignee'] == 'john.doe'
        assert 'filter' not in result.metadata or result.metadata.get('filter') != 'all'
        mock_api.search_issues.assert_called_once_with(
            project_keys=['project-x'],
            assignees=['john.doe'],
            statuses=None
        )
    
    def test_search_issues_unassigned(self, issues_commands, mock_api):
        """Test recherche des issues non assignées (assignee vide)."""
        mock_api.search_issues.return_value = {
            'total': 8,
            'issues': []
        }
        
        result = issues_commands.search_issues(['project-x', ''])
        
        assert result.success is True
        assert result.data['total'] == 8
        assert result.metadata['project'] == 'project-x'
        assert result.metadata['filter'] == 'unassigned'
        mock_api.search_issues.assert_called_once_with(
            project_keys=['project-x'],
            assignees=[''],
            statuses=None
        )
    
    def test_search_issues_no_args(self, issues_commands):
        """Test search_issues sans arguments."""
        result = issues_commands.search_issues([])
        
        assert result.success is False
        assert 'Usage' in result.error
    
    def test_search_issues_api_error(self, issues_commands, mock_api):
        """Test gestion d'erreur API lors de la recherche."""
        mock_api.search_issues.side_effect = SonarQubeAPIError(404, "Project not found")
        
        result = issues_commands.search_issues(['nonexistent-project'])
        
        assert result.success is False
        assert 'Project not found' in result.error
    
    def test_search_issues_with_status(self, issues_commands, mock_api):
        """Test recherche des issues par statut."""
        mock_api.search_issues.return_value = {
            'total': 10,
            'issues': []
        }
        
        result = issues_commands.search_issues(['project-x', '', 'OPEN'])
        
        assert result.success is True
        assert result.data['total'] == 10
        assert result.metadata['project'] == 'project-x'
        assert result.metadata['status'] == 'OPEN'
        mock_api.search_issues.assert_called_once()
        call_kwargs = mock_api.search_issues.call_args[1]
        assert call_kwargs['statuses'] is not None
        assert len(call_kwargs['statuses']) == 1
        assert call_kwargs['statuses'][0].value == 'OPEN'
    
    def test_search_issues_with_assignee_and_status(self, issues_commands, mock_api):
        """Test recherche des issues avec assignee et statut."""
        mock_api.search_issues.return_value = {
            'total': 5,
            'issues': []
        }
        
        result = issues_commands.search_issues(['project-x', 'john.doe', 'FIXED'])
        
        assert result.success is True
        assert result.data['total'] == 5
        assert result.metadata['project'] == 'project-x'
        assert result.metadata['assignee'] == 'john.doe'
        assert result.metadata['status'] == 'FIXED'
        mock_api.search_issues.assert_called_once()
        call_kwargs = mock_api.search_issues.call_args[1]
        assert call_kwargs['assignees'] == ['john.doe']
        assert call_kwargs['statuses'] is not None
        assert len(call_kwargs['statuses']) == 1
        assert call_kwargs['statuses'][0].value == 'FIXED'
    
    def test_search_issues_with_invalid_status(self, issues_commands, mock_api):
        """Test recherche avec un statut invalide."""
        result = issues_commands.search_issues(['project-x', '', 'INVALID_STATUS'])
        
        assert result.success is False
        assert 'Statut invalide' in result.error
        assert 'INVALID_STATUS' in result.error
    
    def test_search_issues_with_multiple_statuses(self, issues_commands, mock_api):
        """Test recherche des issues par plusieurs statuts."""
        mock_api.search_issues.return_value = {
            'total': 20,
            'issues': []
        }
        
        result = issues_commands.search_issues(['project-x', '', 'OPEN,CONFIRMED'])
        
        assert result.success is True
        assert result.data['total'] == 20
        assert result.metadata['project'] == 'project-x'
        assert 'statuses' in result.metadata
        assert result.metadata['statuses'] == ['OPEN', 'CONFIRMED']
        mock_api.search_issues.assert_called_once()
        call_kwargs = mock_api.search_issues.call_args[1]
        assert call_kwargs['statuses'] is not None
        assert len(call_kwargs['statuses']) == 2
        assert call_kwargs['statuses'][0].value == 'OPEN'
        assert call_kwargs['statuses'][1].value == 'CONFIRMED'
    
    def test_search_issues_with_multiple_statuses_and_assignee(self, issues_commands, mock_api):
        """Test recherche des issues par plusieurs statuts avec assignee."""
        mock_api.search_issues.return_value = {
            'total': 12,
            'issues': []
        }
        
        result = issues_commands.search_issues(['project-x', 'john.doe', 'OPEN,CONFIRMED,FIXED'])
        
        assert result.success is True
        assert result.data['total'] == 12
        assert result.metadata['project'] == 'project-x'
        assert result.metadata['assignee'] == 'john.doe'
        assert 'statuses' in result.metadata
        assert result.metadata['statuses'] == ['OPEN', 'CONFIRMED', 'FIXED']
        mock_api.search_issues.assert_called_once()
        call_kwargs = mock_api.search_issues.call_args[1]
        assert call_kwargs['assignees'] == ['john.doe']
        assert call_kwargs['statuses'] is not None
        assert len(call_kwargs['statuses']) == 3
    
    def test_search_issues_with_multiple_statuses_with_spaces(self, issues_commands, mock_api):
        """Test recherche avec statuts séparés par virgules et espaces."""
        mock_api.search_issues.return_value = {
            'total': 15,
            'issues': []
        }
        
        result = issues_commands.search_issues(['project-x', '', 'OPEN, CONFIRMED, FIXED'])
        
        assert result.success is True
        assert result.metadata['statuses'] == ['OPEN', 'CONFIRMED', 'FIXED']
        call_kwargs = mock_api.search_issues.call_args[1]
        assert len(call_kwargs['statuses']) == 3
    
    def test_search_issues_with_multiple_statuses_one_invalid(self, issues_commands, mock_api):
        """Test recherche avec plusieurs statuts dont un invalide."""
        result = issues_commands.search_issues(['project-x', '', 'OPEN,INVALID,CONFIRMED'])
        
        assert result.success is False
        assert 'Statut invalide' in result.error
        assert 'INVALID' in result.error

