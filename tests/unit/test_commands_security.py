"""Tests unitaires pour les commandes security."""

import pytest
from unittest.mock import Mock
from src.commands.security import SecurityCommands
from src.config import SonarQubeConfig
from src.api import SonarQubeAPIError
from src.models import HotspotStatus


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
def security_commands(mock_api, config):
    """Instance SecurityCommands avec mocks."""
    return SecurityCommands(mock_api, config)


class TestGetHotspotsCommand:
    """Tests de la commande get_hotspots()."""
    
    def test_get_hotspots_all(self, security_commands, mock_api):
        """Test hotspots sans filtre de statut (défaut TO_REVIEW)."""
        mock_api.search_hotspots.return_value = {
            'hotspots': [
                {'key': 'hs1', 'status': 'TO_REVIEW'}
            ],
            'paging': {'total': 1}
        }
        
        result = security_commands.get_hotspots(['test-project'])
        
        assert result.success is True
        assert result.metadata['total'] == 1
        assert result.metadata['status'] == 'TO_REVIEW'
        mock_api.search_hotspots.assert_called_once_with(
            'test-project',
            status=HotspotStatus.TO_REVIEW
        )
    
    def test_get_hotspots_to_review(self, security_commands, mock_api):
        """Test hotspots avec statut TO_REVIEW."""
        mock_api.search_hotspots.return_value = {
            'hotspots': [{'key': 'hs1', 'status': 'TO_REVIEW'}],
            'paging': {'total': 1}
        }
        
        result = security_commands.get_hotspots(['test-project', 'TO_REVIEW'])
        
        assert result.success is True
        assert result.metadata['status'] == 'TO_REVIEW'
        mock_api.search_hotspots.assert_called_once_with(
            'test-project',
            status=HotspotStatus.TO_REVIEW
        )
    
    def test_get_hotspots_reviewed(self, security_commands, mock_api):
        """Test hotspots avec statut REVIEWED."""
        mock_api.search_hotspots.return_value = {
            'hotspots': [],
            'paging': {'total': 0}
        }
        
        result = security_commands.get_hotspots(['test-project', 'REVIEWED'])
        
        assert result.success is True
        assert result.metadata['status'] == 'REVIEWED'
        mock_api.search_hotspots.assert_called_once_with(
            'test-project',
            status=HotspotStatus.REVIEWED
        )
    
    def test_get_hotspots_safe(self, security_commands, mock_api):
        """Test hotspots avec statut SAFE."""
        mock_api.search_hotspots.return_value = {
            'hotspots': [],
            'paging': {'total': 0}
        }
        
        result = security_commands.get_hotspots(['test-project', 'SAFE'])
        
        assert result.success is True
        assert result.metadata['status'] == 'SAFE'
        mock_api.search_hotspots.assert_called_once_with(
            'test-project',
            status=HotspotStatus.SAFE
        )
    
    def test_get_hotspots_invalid_status(self, security_commands):
        """Test hotspots avec statut invalide."""
        result = security_commands.get_hotspots(['test-project', 'INVALID'])
        
        assert result.success is False
    
    def test_get_hotspots_missing_project(self, security_commands):
        """Test hotspots sans projet."""
        result = security_commands.get_hotspots([])
        
        assert result.success is False
        assert 'Usage' in result.error
    
    def test_get_hotspots_api_error(self, security_commands, mock_api):
        """Test hotspots avec erreur API."""
        mock_api.search_hotspots.side_effect = SonarQubeAPIError(
            status_code=404,
            message="Project not found"
        )
        
        result = security_commands.get_hotspots(['unknown-project'])
        
        assert result.success is False
        assert 'erreur' in result.error.lower()
    
    def test_get_hotspots_empty_results(self, security_commands, mock_api):
        """Test hotspots sans résultats."""
        mock_api.search_hotspots.return_value = {
            'hotspots': [],
            'paging': {'total': 0}
        }
        
        result = security_commands.get_hotspots(['clean-project'])
        
        assert result.success is True
        assert result.metadata['total'] == 0

