"""Tests unitaires pour les commandes projects."""

import pytest
from unittest.mock import Mock
from src.commands.projects import ProjectsCommands
from src.config import SonarQubeConfig, ProjectConfig
from src.api import SonarQubeAPIError
from src.models import Project


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
def projects_commands(mock_api, config):
    """Instance ProjectsCommands avec mocks."""
    return ProjectsCommands(mock_api, config)


class TestGetInfoCommand:
    """Tests de la commande get_info()."""
    
    def test_get_info_existing_project(self, projects_commands, mock_api):
        """Test project-info avec projet existant."""
        mock_project = Project(
            key='test-project',
            name='Test Project',
            qualifier='TRK',
            visibility='public'
        )
        mock_api.get_project.return_value = mock_project
        
        result = projects_commands.get_info(['test-project'])
        
        assert result.success is True
        assert result.data is not None
        mock_api.get_project.assert_called_once_with('test-project')
    
    def test_get_info_nonexistent_project(self, projects_commands, mock_api):
        """Test project-info avec projet inexistant."""
        mock_api.get_project.return_value = None
        
        result = projects_commands.get_info(['unknown-project'])
        
        assert result.success is False
        assert 'non trouvé' in result.error.lower()
    
    def test_get_info_missing_args(self, projects_commands):
        """Test project-info sans arguments."""
        result = projects_commands.get_info([])
        
        assert result.success is False
        assert 'Usage' in result.error
    
    def test_get_info_api_error(self, projects_commands, mock_api):
        """Test project-info avec erreur API."""
        mock_api.get_project.side_effect = SonarQubeAPIError(
            status_code=403,
            message="Forbidden"
        )
        
        result = projects_commands.get_info(['test-project'])
        
        assert result.success is False


class TestListProjectsCommand:
    """Tests de la commande list_projects()."""
    
    def test_list_projects_all(self, projects_commands, mock_api):
        """Test projects sans recherche (tous)."""
        mock_projects = [
            Project(key='proj1', name='Project 1', qualifier='TRK', visibility='public'),
            Project(key='proj2', name='Project 2', qualifier='TRK', visibility='private')
        ]
        mock_api.search_projects.return_value = mock_projects
        
        result = projects_commands.list_projects([])
        
        assert result.success is True
        assert result.metadata['total'] == 2
        mock_api.search_projects.assert_called_once_with(query=None)
    
    def test_list_projects_with_search(self, projects_commands, mock_api):
        """Test projects avec terme de recherche."""
        mock_projects = [
            Project(key='proj1', name='Project 1', qualifier='TRK', visibility='public')
        ]
        mock_api.search_projects.return_value = mock_projects
        
        result = projects_commands.list_projects(['test'])
        
        assert result.success is True
        assert result.metadata['total'] == 1
        mock_api.search_projects.assert_called_once_with(query='test')
    
    def test_list_projects_empty_results(self, projects_commands, mock_api):
        """Test projects sans résultats."""
        mock_api.search_projects.return_value = []
        
        result = projects_commands.list_projects(['nonexistent'])
        
        assert result.success is True
        assert result.metadata['total'] == 0
    
    def test_list_projects_api_error(self, projects_commands, mock_api):
        """Test projects avec erreur API."""
        mock_api.search_projects.side_effect = SonarQubeAPIError(
            status_code=403,
            message="Forbidden"
        )
        
        result = projects_commands.list_projects([])
        
        assert result.success is False


class TestGetQualityGateCommand:
    """Tests de la commande get_quality_gate()."""
    
    def test_quality_gate_passed(self, projects_commands, mock_api):
        """Test quality-gate avec statut OK."""
        mock_api.get_quality_gate_status.return_value = {
            'projectStatus': {
                'status': 'OK',
                'conditions': []
            }
        }
        
        result = projects_commands.get_quality_gate(['test-project'])
        
        assert result.success is True
        assert result.data['projectStatus']['status'] == 'OK'
        mock_api.get_quality_gate_status.assert_called_once_with('test-project')
    
    def test_quality_gate_failed(self, projects_commands, mock_api):
        """Test quality-gate avec statut ERROR."""
        mock_api.get_quality_gate_status.return_value = {
            'projectStatus': {
                'status': 'ERROR',
                'conditions': [
                    {'status': 'ERROR', 'metricKey': 'coverage', 'actualValue': '50'}
                ]
            }
        }
        
        result = projects_commands.get_quality_gate(['test-project'])
        
        assert result.success is True
        assert result.data['projectStatus']['status'] == 'ERROR'
    
    def test_quality_gate_missing_args(self, projects_commands):
        """Test quality-gate sans arguments."""
        result = projects_commands.get_quality_gate([])
        
        assert result.success is False
        assert 'Usage' in result.error
    
    def test_quality_gate_api_error(self, projects_commands, mock_api):
        """Test quality-gate avec erreur API."""
        mock_api.get_quality_gate_status.side_effect = SonarQubeAPIError(
            status_code=404,
            message="Not found"
        )
        
        result = projects_commands.get_quality_gate(['unknown-project'])
        
        assert result.success is False


class TestHealthCheckCommand:
    """Tests de la commande health_check()."""
    
    def test_health_check_success(self, projects_commands, mock_api):
        """Test health avec succès."""
        mock_api.health_check.return_value = {
            'health': 'GREEN',
            'causes': []
        }
        
        result = projects_commands.health_check([])
        
        assert result.success is True
        assert result.data['health'] == 'GREEN'
        mock_api.health_check.assert_called_once()
    
    def test_health_check_degraded(self, projects_commands, mock_api):
        """Test health avec statut dégradé."""
        mock_api.health_check.return_value = {
            'health': 'YELLOW',
            'causes': ['Database slow']
        }
        
        result = projects_commands.health_check([])
        
        assert result.success is True
        assert result.data['health'] == 'YELLOW'
    
    def test_health_check_api_error(self, projects_commands, mock_api):
        """Test health avec erreur API (403 typiquement)."""
        mock_api.health_check.side_effect = SonarQubeAPIError(
            status_code=403,
            message="Forbidden - admin only"
        )
        
        result = projects_commands.health_check([])
        
        assert result.success is False
        assert 'erreur' in result.error.lower()


class TestGetVersionCommand:
    """Tests de la commande get_version()."""
    
    def test_get_version_success(self, projects_commands, mock_api):
        """Test version avec succès."""
        mock_api.get_server_version.return_value = "9.9.0.65466"
        
        result = projects_commands.get_version([])
        
        assert result.success is True
        assert result.data['version'] == "9.9.0.65466"
        mock_api.get_server_version.assert_called_once()
    
    def test_get_version_api_error(self, projects_commands, mock_api):
        """Test version avec erreur API."""
        mock_api.get_server_version.side_effect = SonarQubeAPIError(
            status_code=500,
            message="Internal error"
        )
        
        result = projects_commands.get_version([])
        
        assert result.success is False


class TestAnalysesHistoryCommand:
    """Tests de la commande get_analyses_history()."""
    
    def test_analyses_with_project_key(self, projects_commands, mock_api):
        """Test analyses avec project_key."""
        mock_api.projects.get_analyses_history.return_value = {
            'analyses': [{'key': 'A1', 'date': '2025-01-01'}]
        }
        
        result = projects_commands.get_analyses_history(['test-project'])
        
        assert result.success is True
        assert 'analyses' in result.data
        mock_api.projects.get_analyses_history.assert_called_once_with(
            'test-project', None, None
        )
    
    def test_analyses_without_project_key(self, mock_api):
        """Test analyses sans project_key (utilise défaut)."""
        config = SonarQubeConfig(
            url="https://test.sonarqube.com",
            token="test_token",
            default_project=ProjectConfig(key='default-project', assignee='user1')
        )
        projects_commands = ProjectsCommands(mock_api, config)
        mock_api.projects.get_analyses_history.return_value = {'analyses': []}
        
        result = projects_commands.get_analyses_history([])
        
        assert result.success is True
        mock_api.projects.get_analyses_history.assert_called_once_with(
            'default-project', None, None
        )
    
    def test_analyses_with_dates(self, projects_commands, mock_api):
        """Test analyses avec dates."""
        mock_api.projects.get_analyses_history.return_value = {'analyses': []}
        
        result = projects_commands.get_analyses_history([
            'test-project', '2025-01-01', '2025-01-31'
        ])
        
        assert result.success is True
        mock_api.projects.get_analyses_history.assert_called_once_with(
            'test-project', '2025-01-01', '2025-01-31'
        )
    
    def test_analyses_api_error(self, projects_commands, mock_api):
        """Test erreur API."""
        mock_api.projects.get_analyses_history.side_effect = SonarQubeAPIError(
            status_code=403,
            message="Forbidden"
        )
        
        result = projects_commands.get_analyses_history(['test-project'])
        
        assert result.success is False
        assert 'historique des analyses' in result.error.lower()
    
    def test_analyses_empty_result(self, projects_commands, mock_api):
        """Test avec aucune analyse."""
        mock_api.projects.get_analyses_history.return_value = {'analyses': []}
        
        result = projects_commands.get_analyses_history(['test-project'])
        
        assert result.success is True
        assert result.data['analyses'] == []


class TestDuplicationsCommand:
    """Tests de la commande get_duplications()."""
    
    def test_duplications_success(self, projects_commands, mock_api):
        """Test duplications avec succès."""
        mock_api.projects.get_duplications.return_value = {
            'duplications': [{'from': {'line': 10}, 'size': 5}]
        }
        
        result = projects_commands.get_duplications(['project:src/main.dart'])
        
        assert result.success is True
        assert 'duplications' in result.data
        mock_api.projects.get_duplications.assert_called_once_with('project:src/main.dart')
    
    def test_duplications_missing_args(self, projects_commands):
        """Test sans file_key."""
        result = projects_commands.get_duplications([])
        
        assert result.success is False
        assert 'usage' in result.error.lower()
    
    def test_duplications_no_duplications(self, projects_commands, mock_api):
        """Test sans duplications."""
        mock_api.projects.get_duplications.return_value = {'duplications': []}
        
        result = projects_commands.get_duplications(['project:src/main.dart'])
        
        assert result.success is True
        assert result.data['duplications'] == []
    
    def test_duplications_api_error(self, projects_commands, mock_api):
        """Test erreur API."""
        mock_api.projects.get_duplications.side_effect = SonarQubeAPIError(
            status_code=404,
            message="File not found"
        )
        
        result = projects_commands.get_duplications(['project:src/unknown.dart'])
        
        assert result.success is False
        assert 'duplications' in result.error.lower()
    
    def test_duplications_with_blocks(self, projects_commands, mock_api):
        """Test avec plusieurs blocs dupliqués."""
        mock_api.projects.get_duplications.return_value = {
            'duplications': [
                {'from': {'line': 10}, 'size': 5},
                {'from': {'line': 50}, 'size': 10}
            ]
        }
        
        result = projects_commands.get_duplications(['project:src/util.dart'])
        
        assert result.success is True
        assert len(result.data['duplications']) == 2


class TestSourceLinesCommand:
    """Tests de la commande get_source_lines()."""
    
    def test_source_lines_success(self, projects_commands, mock_api):
        """Test code source avec succès."""
        mock_api.projects.get_source_lines.return_value = {
            'sources': [{'line': 1, 'code': 'import foo;'}]
        }
        
        result = projects_commands.get_source_lines(['project:src/main.dart'])
        
        assert result.success is True
        assert 'sources' in result.data
        mock_api.projects.get_source_lines.assert_called_once_with(
            'project:src/main.dart', 1, None
        )
    
    def test_source_lines_missing_args(self, projects_commands):
        """Test sans file_key."""
        result = projects_commands.get_source_lines([])
        
        assert result.success is False
        assert 'usage' in result.error.lower()
    
    def test_source_lines_with_range(self, projects_commands, mock_api):
        """Test avec range de lignes."""
        mock_api.projects.get_source_lines.return_value = {'sources': []}
        
        result = projects_commands.get_source_lines([
            'project:src/main.dart', '10', '20'
        ])
        
        assert result.success is True
        mock_api.projects.get_source_lines.assert_called_once_with(
            'project:src/main.dart', 10, 20
        )
    
    def test_source_lines_invalid_line_number(self, projects_commands):
        """Test avec numéro de ligne invalide."""
        result = projects_commands.get_source_lines([
            'project:src/main.dart', 'abc'
        ])
        
        assert result.success is False
        assert 'entiers' in result.error.lower()
    
    def test_source_lines_api_error(self, projects_commands, mock_api):
        """Test erreur API."""
        mock_api.projects.get_source_lines.side_effect = SonarQubeAPIError(
            status_code=404,
            message="File not found"
        )
        
        result = projects_commands.get_source_lines(['project:src/unknown.dart'])
        
        assert result.success is False
        assert 'code source' in result.error.lower()

