"""Tests pour la couche API."""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock

from src.config import SonarQubeConfig
from src.api import SonarQubeAPI, SonarQubeAPIError
from src.models import IssueType, Severity


@pytest.fixture
def config():
    """Fixture pour la configuration."""
    return SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test-token",
        timeout=30,
        max_retries=3,
        page_size=100
    )


@pytest.fixture
def api(config):
    """Fixture pour l'API."""
    return SonarQubeAPI(config)


class TestSonarQubeAPI:
    """Tests pour SonarQubeAPI."""
    
    def test_init(self, api, config):
        """Test l'initialisation de l'API."""
        assert api.config == config
        assert api.issues is not None
        assert api.measures is not None
        assert api.security is not None
        assert api.projects is not None
        assert api.users is not None
        assert api.rules is not None
    
    @patch('requests.Session.request')
    def test_request_success(self, mock_request, api):
        """Test une requête réussie via issues API."""
        mock_response = Mock()
        mock_response.json.return_value = {'test': 'data'}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = api.issues._request('GET', '/api/test', params={'param': 'value'})
        
        assert result == {'test': 'data'}
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_request_http_error(self, mock_request, api):
        """Test une requête avec erreur HTTP."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_request.return_value = mock_response
        
        with pytest.raises(SonarQubeAPIError) as exc_info:
            api.issues._request('GET', '/api/test')
        
        assert exc_info.value.status_code == 404
    
    @patch('requests.Session.request')
    def test_search_issues(self, mock_request, api):
        """Test la recherche d'issues."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'total': 1,
            'issues': [{
                'key': 'issue-1',
                'rule': 'dart:S1192',
                'severity': 'MAJOR',
                'component': 'project:file.dart',
                'message': 'Test',
                'type': 'CODE_SMELL',
                'status': 'OPEN'
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = api.issues.search(
            project_keys=['test-project'],
            types=[IssueType.CODE_SMELL]
        )
        
        assert result['total'] == 1
        assert len(result['issues']) == 1
        assert result['issues'][0].key == 'issue-1'
    
    @patch('requests.Session.request')
    def test_get_component_measures(self, mock_request, api):
        """Test la récupération de métriques."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'component': {
                'key': 'project-key',
                'name': 'Project',
                'qualifier': 'TRK',
                'measures': [
                    {'metric': 'ncloc', 'value': '1000'},
                    {'metric': 'coverage', 'value': '80.5'}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        component = api.measures.get_component('project-key')
        
        assert component.key == 'project-key'
        assert len(component.measures) == 2
    
    @patch('requests.Session.request')
    def test_search_hotspots(self, mock_request, api):
        """Test la recherche de hotspots."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'hotspots': [{
                'key': 'hotspot-1',
                'component': 'project:file.dart',
                'securityCategory': 'sql-injection',
                'vulnerabilityProbability': 'HIGH',
                'status': 'TO_REVIEW'
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = api.security.search_hotspots('project-key')
        
        assert len(result['hotspots']) == 1
        assert result['hotspots'][0].key == 'hotspot-1'
    
    @patch('requests.Session.request')
    def test_get_rule(self, mock_request, api):
        """Test la récupération d'une règle."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'rule': {
                'key': 'dart:S1192',
                'name': 'Test Rule',
                'lang': 'dart',
                'type': 'CODE_SMELL',
                'severity': 'MAJOR',
                'tags': []
            }
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        rule = api.rules.get('dart:S1192')
        
        assert rule.key == 'dart:S1192'
        assert rule.name == 'Test Rule'
        assert rule.lang == 'dart'
    
    @patch('requests.Session.request')
    def test_search_users(self, mock_request, api):
        """Test la recherche d'utilisateurs."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'users': [{
                'login': 'user1',
                'name': 'User One',
                'email': 'user1@example.com',
                'active': True
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        users = api.users.search('user')
        
        assert len(users) == 1
        assert users[0].login == 'user1'




