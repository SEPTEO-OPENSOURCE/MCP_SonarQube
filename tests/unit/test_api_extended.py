"""Tests unitaires étendus pour les APIs."""

import pytest
from unittest.mock import Mock, patch
from src.api.issues import IssuesAPI
from src.api.measures import MeasuresAPI
from src.api.projects import ProjectsAPI
from src.api.security import SecurityAPI
from src.api.rules import RulesAPI
from src.api.users import UsersAPI
from src.config import SonarQubeConfig
from src.models import IssueType, Severity, HotspotStatus


@pytest.fixture
def config():
    """Configuration test."""
    return SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test_token"
    )


class TestIssuesAPIExtended:
    """Tests étendus pour IssuesAPI."""
    
    def test_search_with_all_filters(self, config):
        """Test search avec tous les filtres."""
        api = IssuesAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'issues': [], 'total': 0}
            
            api.search(
                project_keys=['proj1', 'proj2'],
                assignees=['user1'],
                types=[IssueType.BUG],
                severities=[Severity.CRITICAL],
                resolved=True,
                files=['file1.dart'],
                rules=['dart:S1192'],
                tags=['security'],
                page=2,
                page_size=100
            )
            
            # Vérifier que tous les paramètres sont passés
            call_args = mock_get.call_args
            params = call_args[0][1]
            assert params['componentKeys'] == 'proj1,proj2'
            assert params['assignees'] == 'user1'
            assert params['types'] == 'BUG'
            assert params['severities'] == 'CRITICAL'
            assert params['resolved'] == 'true'
            assert params['files'] == 'file1.dart'
            assert params['rules'] == 'dart:S1192'
            assert params['tags'] == 'security'
            assert params['p'] == 2
            assert params['ps'] == 100
    
    def test_assign(self, config):
        """Test assign issue."""
        api = IssuesAPI(config)
        
        with patch.object(api, '_post') as mock_post:
            mock_post.return_value = {'issue': {}}
            
            result = api.assign('ISSUE-123', 'user1')
            
            assert result is not None
            mock_post.assert_called_once()
            # _post est appelé avec endpoint et params comme args positionnels
            call_args = mock_post.call_args[0]
            assert 'assign' in call_args[0]  # endpoint
            assert call_args[1]['issue'] == 'ISSUE-123'  # params
            assert call_args[1]['assignee'] == 'user1'
    
    def test_add_comment(self, config):
        """Test add_comment."""
        api = IssuesAPI(config)
        
        with patch.object(api, '_post') as mock_post:
            mock_post.return_value = {'issue': {}}
            
            result = api.add_comment('ISSUE-123', 'Test comment')
            
            assert result is not None
            mock_post.assert_called_once()
            call_args = mock_post.call_args[0]
            assert 'add_comment' in call_args[0]
            assert call_args[1]['issue'] == 'ISSUE-123'
            assert call_args[1]['text'] == 'Test comment'
    
    def test_set_severity(self, config):
        """Test set_severity."""
        api = IssuesAPI(config)
        
        with patch.object(api, '_post') as mock_post:
            mock_post.return_value = {'issue': {}}
            
            result = api.set_severity('ISSUE-123', Severity.BLOCKER)
            
            assert result is not None
            mock_post.assert_called_once()
            call_args = mock_post.call_args[0]
            assert 'set_severity' in call_args[0]
            assert call_args[1]['severity'] == 'BLOCKER'
    
    def test_set_type(self, config):
        """Test set_type."""
        api = IssuesAPI(config)
        
        with patch.object(api, '_post') as mock_post:
            mock_post.return_value = {'issue': {}}
            
            result = api.set_type('ISSUE-123', IssueType.VULNERABILITY)
            
            assert result is not None
            mock_post.assert_called_once()
            call_args = mock_post.call_args[0]
            assert 'set_type' in call_args[0]
            assert call_args[1]['type'] == 'VULNERABILITY'


class TestMeasuresAPIExtended:
    """Tests étendus pour MeasuresAPI."""
    
    def test_get_component_with_custom_metrics(self, config):
        """Test get_component avec métriques personnalisées."""
        api = MeasuresAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {
                'component': {
                    'key': 'test-proj',
                    'name': 'Test',
                    'qualifier': 'TRK',
                    'measures': []
                }
            }
            
            result = api.get_component('test-proj', ['ncloc', 'bugs'])
            
            assert result is not None
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[0][1]
            assert params['metricKeys'] == 'ncloc,bugs'


class TestProjectsAPIExtended:
    """Tests étendus pour ProjectsAPI."""
    
    def test_search_with_pagination(self, config):
        """Test search avec pagination."""
        api = ProjectsAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'components': []}
            
            api.search(query='test', page=3, page_size=50)
            
            call_args = mock_get.call_args
            params = call_args[0][1]
            assert params['p'] == 3
            assert params['ps'] == 50
            assert params['q'] == 'test'
    
    def test_get_component_tree(self, config):
        """Test get_component_tree."""
        api = ProjectsAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'components': []}
            
            api.get_component_tree('proj1', qualifiers=['FIL', 'DIR'])
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[0][1]
            assert params['qualifiers'] == 'FIL,DIR'
    
    def test_get_component_sources(self, config):
        """Test get_component_sources."""
        api = ProjectsAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'sources': []}
            
            api.get_component_sources('proj1:file.dart', from_line=10, to_line=20)
            
            mock_get.assert_called_once()
    
    def test_health_check(self, config):
        """Test health_check."""
        api = ProjectsAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'health': 'GREEN'}
            
            result = api.health_check()
            
            assert result['health'] == 'GREEN'
            mock_get.assert_called_once()


class TestSecurityAPIExtended:
    """Tests étendus pour SecurityAPI."""
    
    def test_search_hotspots_with_status(self, config):
        """Test search_hotspots avec statut."""
        api = SecurityAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'hotspots': []}
            
            api.search_hotspots('proj1', status=HotspotStatus.REVIEWED)
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[0][1]
            assert params['status'] == 'REVIEWED'
    
    def test_search_hotspots_without_status(self, config):
        """Test search_hotspots sans statut."""
        api = SecurityAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'hotspots': []}
            
            result = api.search_hotspots('proj1')
            
            assert result is not None
            mock_get.assert_called_once()


class TestRulesAPIExtended:
    """Tests étendus pour RulesAPI."""
    
    def test_get(self, config):
        """Test get rule."""
        api = RulesAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {
                'rule': {
                    'key': 'dart:S1192',
                    'name': 'Test',
                    'lang': 'dart',
                    'type': 'CODE_SMELL',
                    'severity': 'MAJOR'
                }
            }
            
            result = api.get('dart:S1192')
            
            assert result is not None
            assert result.key == 'dart:S1192'
    
    def test_search(self, config):
        """Test search rules."""
        api = RulesAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'rules': [], 'total': 0}
            
            api.search(q='duplicate', languages=['dart'], types=['CODE_SMELL'])
            
            mock_get.assert_called_once()


class TestUsersAPIExtended:
    """Tests étendus pour UsersAPI."""
    
    def test_search(self, config):
        """Test search users."""
        api = UsersAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'users': []}
            
            api.search('john')
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[0][1]
            assert params['q'] == 'john'

