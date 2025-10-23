"""Tests unitaires pour les nouvelles méthodes de ProjectsAPI."""

import pytest
from unittest.mock import Mock, patch
from src.api.projects import ProjectsAPI
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
    return ProjectsAPI(config)


class TestAnalysesHistory:
    """Tests pour get_analyses_history()."""
    
    def test_get_analyses_history_success(self, api):
        """Test succès récupération historique analyses."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {
                'analyses': [
                    {'key': 'A1', 'date': '2025-01-01'},
                    {'key': 'A2', 'date': '2025-01-02'}
                ]
            }
            
            result = api.get_analyses_history('test-project')
            
            assert 'analyses' in result
            assert len(result['analyses']) == 2
            mock_get.assert_called_once_with(
                '/api/project_analyses/search',
                {'project': 'test-project', 'p': 1, 'ps': 500}
            )
    
    def test_get_analyses_history_with_dates(self, api):
        """Test avec dates de début et fin."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'analyses': []}
            
            api.get_analyses_history('test-project', '2025-01-01', '2025-01-31')
            
            mock_get.assert_called_once_with(
                '/api/project_analyses/search',
                {
                    'project': 'test-project',
                    'p': 1,
                    'ps': 500,
                    'from': '2025-01-01',
                    'to': '2025-01-31'
                }
            )
    
    def test_get_analyses_history_with_from_date_only(self, api):
        """Test avec seulement date de début."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'analyses': []}
            
            api.get_analyses_history('test-project', from_date='2025-01-01')
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args[0][1]
            assert 'from' in call_args
            assert 'to' not in call_args
    
    def test_get_analyses_history_with_pagination(self, api):
        """Test avec pagination personnalisée."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'analyses': []}
            
            api.get_analyses_history('test-project', page=2, page_size=50)
            
            call_args = mock_get.call_args[0][1]
            assert call_args['p'] == 2
            assert call_args['ps'] == 50
    
    def test_get_analyses_history_empty_result(self, api):
        """Test avec aucune analyse."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'analyses': []}
            
            result = api.get_analyses_history('test-project')
            
            assert result['analyses'] == []
    
    def test_get_analyses_history_api_error(self, api):
        """Test erreur API."""
        with patch.object(api, '_get') as mock_get:
            mock_get.side_effect = SonarQubeAPIError(403, "Forbidden")
            
            with pytest.raises(SonarQubeAPIError) as exc_info:
                api.get_analyses_history('test-project')
            
            assert exc_info.value.status_code == 403


class TestDuplications:
    """Tests pour get_duplications()."""
    
    def test_get_duplications_success(self, api):
        """Test succès récupération duplications."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {
                'duplications': [
                    {'from': {'line': 10}, 'size': 5}
                ]
            }
            
            result = api.get_duplications('project:src/main.dart')
            
            assert 'duplications' in result
            mock_get.assert_called_once_with(
                '/api/duplications/show',
                {'key': 'project:src/main.dart'}
            )
    
    def test_get_duplications_no_duplications(self, api):
        """Test sans duplications."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'duplications': []}
            
            result = api.get_duplications('project:src/main.dart')
            
            assert result['duplications'] == []
    
    def test_get_duplications_with_blocks(self, api):
        """Test avec plusieurs blocs dupliqués."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {
                'duplications': [
                    {'from': {'line': 10}, 'size': 5, 'duplicated': True},
                    {'from': {'line': 50}, 'size': 10, 'duplicated': True}
                ]
            }
            
            result = api.get_duplications('project:src/util.dart')
            
            assert len(result['duplications']) == 2
    
    def test_get_duplications_file_not_found(self, api):
        """Test fichier inexistant."""
        with patch.object(api, '_get') as mock_get:
            mock_get.side_effect = SonarQubeAPIError(404, "File not found")
            
            with pytest.raises(SonarQubeAPIError) as exc_info:
                api.get_duplications('project:src/unknown.dart')
            
            assert exc_info.value.status_code == 404
    
    def test_get_duplications_api_error(self, api):
        """Test erreur API générique."""
        with patch.object(api, '_get') as mock_get:
            mock_get.side_effect = SonarQubeAPIError(500, "Server error")
            
            with pytest.raises(SonarQubeAPIError):
                api.get_duplications('project:src/main.dart')


class TestSourceLines:
    """Tests pour get_source_lines()."""
    
    def test_get_source_lines_success(self, api):
        """Test succès récupération code source."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {
                'sources': [
                    {'line': 1, 'code': 'import foo;'}
                ]
            }
            
            result = api.get_source_lines('project:src/main.dart')
            
            assert 'sources' in result
            mock_get.assert_called_once_with(
                '/api/sources/lines',
                {'key': 'project:src/main.dart', 'from': 1}
            )
    
    def test_get_source_lines_with_range(self, api):
        """Test avec range de lignes."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'sources': []}
            
            api.get_source_lines('project:src/main.dart', from_line=10, to_line=20)
            
            mock_get.assert_called_once_with(
                '/api/sources/lines',
                {'key': 'project:src/main.dart', 'from': 10, 'to': 20}
            )
    
    def test_get_source_lines_from_line_only(self, api):
        """Test avec seulement from_line."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'sources': []}
            
            api.get_source_lines('project:src/main.dart', from_line=50)
            
            call_args = mock_get.call_args[0][1]
            assert call_args['from'] == 50
            assert 'to' not in call_args
    
    def test_get_source_lines_default_from_line(self, api):
        """Test valeur par défaut from_line=1."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'sources': []}
            
            api.get_source_lines('project:src/main.dart')
            
            call_args = mock_get.call_args[0][1]
            assert call_args['from'] == 1
    
    def test_get_source_lines_with_issues(self, api):
        """Test code source avec issues annotées."""
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {
                'sources': [
                    {'line': 10, 'code': 'var x = 1;', 'issues': ['issue-1']}
                ]
            }
            
            result = api.get_source_lines('project:src/main.dart', 10, 10)
            
            assert len(result['sources']) == 1
            assert 'issues' in result['sources'][0]
    
    def test_get_source_lines_file_not_found(self, api):
        """Test fichier inexistant."""
        with patch.object(api, '_get') as mock_get:
            mock_get.side_effect = SonarQubeAPIError(404, "File not found")
            
            with pytest.raises(SonarQubeAPIError) as exc_info:
                api.get_source_lines('project:src/unknown.dart')
            
            assert exc_info.value.status_code == 404
    
    def test_get_source_lines_invalid_range(self, api):
        """Test range invalide."""
        with patch.object(api, '_get') as mock_get:
            mock_get.side_effect = SonarQubeAPIError(400, "Invalid range")
            
            with pytest.raises(SonarQubeAPIError):
                api.get_source_lines('project:src/main.dart', 100, 50)

