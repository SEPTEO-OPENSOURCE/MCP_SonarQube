"""Tests unitaires pour les commandes measures."""

import pytest
from unittest.mock import Mock
from src.commands.measures import MeasuresCommands
from src.config import SonarQubeConfig, ProjectConfig
from src.api import SonarQubeAPIError


@pytest.fixture
def mock_api():
    """Mock de l'API SonarQube."""
    return Mock()


@pytest.fixture
def config():
    """Configuration SonarQube."""
    config = SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test_token"
    )
    config.default_project = ProjectConfig(key="test-project")
    return config


@pytest.fixture
def measures_commands(mock_api, config):
    """Instance MeasuresCommands avec mocks."""
    return MeasuresCommands(mock_api, config)


class TestGetMeasuresCommand:
    """Tests de la commande get_measures()."""
    
    def test_get_measures_default_metrics(self, measures_commands, mock_api):
        """Test measures avec métriques par défaut."""
        from src.models import Component
        mock_component = Component(
            key='test-project',
            name='Test Project',
            qualifier='TRK',
            measures={}
        )
        mock_api.get_component_measures.return_value = mock_component
        
        result = measures_commands.get_measures(['test-project'])
        
        assert result.success is True
        assert result.data is not None
        mock_api.get_component_measures.assert_called_once_with(
            'test-project',
            None
        )
    
    def test_get_measures_custom_metrics(self, measures_commands, mock_api):
        """Test measures avec métriques personnalisées."""
        from src.models import Component, Measure
        mock_component = Component(
            key='test-project',
            name='Test Project',
            qualifier='TRK',
            measures=[
                Measure(metric='ncloc', value='1000', best_value=False),
                Measure(metric='bugs', value='5', best_value=False)
            ]
        )
        mock_api.get_component_measures.return_value = mock_component
        
        result = measures_commands.get_measures(['test-project', 'ncloc,bugs,coverage'])
        
        assert result.success is True
        mock_api.get_component_measures.assert_called_once_with(
            'test-project',
            ['ncloc', 'bugs', 'coverage']
        )
    
    def test_get_measures_missing_project(self, measures_commands):
        """Test measures sans projet."""
        result = measures_commands.get_measures([])
        
        assert result.success is False
        assert 'Usage' in result.error
    
    def test_get_measures_api_error(self, measures_commands, mock_api):
        """Test measures avec erreur API."""
        mock_api.get_component_measures.side_effect = SonarQubeAPIError(
            status_code=404,
            message="Component not found"
        )
        
        result = measures_commands.get_measures(['unknown-project'])
        
        assert result.success is False
        assert 'erreur' in result.error.lower()
    
    def test_get_measures_empty_metrics_string(self, measures_commands, mock_api):
        """Test measures avec chaîne de métriques vide."""
        from src.models import Component
        mock_component = Component(
            key='test-project',
            name='Test Project',
            qualifier='TRK',
            measures=[]
        )
        mock_api.get_component_measures.return_value = mock_component
        
        result = measures_commands.get_measures(['test-project', ''])
        
        assert result.success is True
        # Devrait split la chaîne vide en liste vide
        mock_api.get_component_measures.assert_called_once_with(
            'test-project',
            ['']
        )


class TestMetricsListCommand:
    """Tests de la commande get_metrics_list()."""
    
    def test_metrics_list_success(self, measures_commands, mock_api):
        """Test metrics-list avec succès."""
        mock_api.measures.get_metrics_list.return_value = {
            'metrics': [
                {'key': 'ncloc', 'name': 'Lines of Code'},
                {'key': 'coverage', 'name': 'Coverage'}
            ]
        }
        
        result = measures_commands.get_metrics_list([])
        
        assert result.success is True
        assert 'metrics' in result.data
        mock_api.measures.get_metrics_list.assert_called_once()
    
    def test_metrics_list_empty(self, measures_commands, mock_api):
        """Test metrics-list avec liste vide."""
        mock_api.measures.get_metrics_list.return_value = {'metrics': []}
        
        result = measures_commands.get_metrics_list([])
        
        assert result.success is True
        assert result.data['metrics'] == []
    
    def test_metrics_list_api_error(self, measures_commands, mock_api):
        """Test metrics-list avec erreur API."""
        mock_api.measures.get_metrics_list.side_effect = SonarQubeAPIError(
            status_code=500,
            message="Server error"
        )
        
        result = measures_commands.get_metrics_list([])
        
        assert result.success is False
        assert 'métriques' in result.error.lower()
    
    def test_metrics_list_with_total(self, measures_commands, mock_api):
        """Test metrics-list avec total."""
        mock_api.measures.get_metrics_list.return_value = {
            'metrics': [{'key': 'ncloc'}],
            'total': 50
        }
        
        result = measures_commands.get_metrics_list([])
        
        assert result.success is True
        assert result.data['total'] == 50
    
    def test_metrics_list_ignores_args(self, measures_commands, mock_api):
        """Test que metrics-list ignore les arguments."""
        mock_api.measures.get_metrics_list.return_value = {'metrics': []}
        
        result = measures_commands.get_metrics_list(['ignored', 'args'])
        
        assert result.success is True
        mock_api.measures.get_metrics_list.assert_called_once()


class TestLanguagesCommand:
    """Tests de la commande get_languages()."""
    
    def test_languages_success(self, measures_commands, mock_api):
        """Test languages avec succès."""
        mock_api.measures.get_languages.return_value = {
            'languages': [
                {'key': 'py', 'name': 'Python'},
                {'key': 'java', 'name': 'Java'}
            ]
        }
        
        result = measures_commands.get_languages([])
        
        assert result.success is True
        assert 'languages' in result.data
        mock_api.measures.get_languages.assert_called_once()
    
    def test_languages_empty(self, measures_commands, mock_api):
        """Test languages avec liste vide."""
        mock_api.measures.get_languages.return_value = {'languages': []}
        
        result = measures_commands.get_languages([])
        
        assert result.success is True
        assert result.data['languages'] == []
    
    def test_languages_api_error(self, measures_commands, mock_api):
        """Test languages avec erreur API."""
        mock_api.measures.get_languages.side_effect = SonarQubeAPIError(
            status_code=403,
            message="Forbidden"
        )
        
        result = measures_commands.get_languages([])
        
        assert result.success is False
        assert 'langages' in result.error.lower()
    
    def test_languages_with_many_languages(self, measures_commands, mock_api):
        """Test languages avec beaucoup de langages."""
        languages = [{'key': f'lang{i}', 'name': f'Language {i}'} for i in range(50)]
        mock_api.measures.get_languages.return_value = {'languages': languages}
        
        result = measures_commands.get_languages([])
        
        assert result.success is True
        assert len(result.data['languages']) == 50
    
    def test_languages_ignores_args(self, measures_commands, mock_api):
        """Test que languages ignore les arguments."""
        mock_api.measures.get_languages.return_value = {'languages': []}
        
        result = measures_commands.get_languages(['ignored', 'args'])
        
        assert result.success is True
        mock_api.measures.get_languages.assert_called_once()

