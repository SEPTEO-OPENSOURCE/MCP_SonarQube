"""Tests unitaires pour les nouvelles méthodes de MeasuresAPI."""

import pytest
from unittest.mock import Mock, patch
from src.api.measures import MeasuresAPI
from src.api.base import SonarQubeAPIError
from src.config import SonarQubeConfig


@pytest.fixture
def config():
    """Configuration de test."""
    return SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test_token"
    )


@pytest.fixture
def api(config):
    """API de test."""
    return MeasuresAPI(config)


class TestMetricsList:
    """Tests pour get_metrics_list()."""
    
    def test_get_metrics_list_success(self, api):
        """Test succès récupération liste métriques."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {
                'metrics': [
                    {'key': 'ncloc', 'name': 'Lines of Code'},
                    {'key': 'coverage', 'name': 'Coverage'}
                ],
                'total': 2
            }
            
            result = api.get_metrics_list()
            
            assert 'metrics' in result
            assert len(result['metrics']) == 2
            mock_get.assert_called_once_with(
                '/api/metrics/search',
                {'p': 1, 'ps': 500}
            )
    
    def test_get_metrics_list_with_pagination(self, api):
        """Test avec pagination personnalisée."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'metrics': [], 'total': 0}
            
            api.get_metrics_list(page=2, page_size=50)
            
            mock_get.assert_called_once_with(
                '/api/metrics/search',
                {'p': 2, 'ps': 50}
            )
    
    def test_get_metrics_list_empty(self, api):
        """Test liste vide."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'metrics': [], 'total': 0}
            
            result = api.get_metrics_list()
            
            assert result['metrics'] == []
    
    def test_get_metrics_list_api_error(self, api):
        """Test erreur API."""
        with patch.object(api, '_get') as mock_get:
            mock_get.side_effect = SonarQubeAPIError(500, "Server error")
            
            with pytest.raises(SonarQubeAPIError):
                api.get_metrics_list()
    
    def test_get_metrics_list_default_page_size(self, api):
        """Test page_size par défaut depuis config."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'metrics': []}
            
            api.get_metrics_list()
            
            call_args = mock_get.call_args[0][1]
            assert call_args['ps'] == api.config.page_size


class TestLanguages:
    """Tests pour get_languages()."""
    
    def test_get_languages_success(self, api):
        """Test succès récupération langages."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {
                'languages': [
                    {'key': 'py', 'name': 'Python'},
                    {'key': 'java', 'name': 'Java'},
                    {'key': 'dart', 'name': 'Dart'}
                ]
            }
            
            result = api.get_languages()
            
            assert 'languages' in result
            assert len(result['languages']) == 3
            mock_get.assert_called_once_with('/api/languages/list', {})
    
    def test_get_languages_empty(self, api):
        """Test aucun langage."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'languages': []}
            
            result = api.get_languages()
            
            assert result['languages'] == []
    
    def test_get_languages_api_error(self, api):
        """Test erreur API."""
        with patch.object(api, '_get') as mock_get:
            mock_get.side_effect = SonarQubeAPIError(403, "Forbidden")
            
            with pytest.raises(SonarQubeAPIError) as exc_info:
                api.get_languages()
            
            assert exc_info.value.status_code == 403
    
    def test_get_languages_no_params(self, api):
        """Test appel sans paramètres."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'languages': []}
            
            api.get_languages()
            
            # Vérifier que {} est passé comme paramètres
            assert mock_get.call_args[0][1] == {}
    
    def test_get_languages_returns_dict(self, api):
        """Test que le retour est un dictionnaire."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'languages': [{'key': 'py'}]}
            
            result = api.get_languages()
            
            assert isinstance(result, dict)

