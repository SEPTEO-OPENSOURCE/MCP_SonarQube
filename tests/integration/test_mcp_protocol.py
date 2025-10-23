"""Tests du protocole MCP."""

import json
import pytest


class TestMCPProtocol:
    """Tests du protocole MCP de base."""
    
    def test_initialize_request(self, mcp_server):
        """Test requête initialize."""
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {}
        }
        
        response = mcp_server.handle_request(request)
        
        assert response is not None
        assert 'result' in response
        assert response['result']['protocolVersion'] == '2024-11-05'
        assert 'capabilities' in response['result']
        assert 'tools' in response['result']['capabilities']
        assert 'serverInfo' in response['result']
        assert response['result']['serverInfo']['name'] == 'sonarqube-mcp'
        assert response['result']['serverInfo']['version'] == '4.0.0'
    
    def test_initialized_notification(self, mcp_server):
        """Test notification initialized."""
        request = {
            'jsonrpc': '2.0',
            'method': 'initialized'
        }
        
        response = mcp_server.handle_request(request)
        
        # Initialized retourne un result vide
        assert response is not None
        assert response == {'result': {}}
    
    def test_notifications_initialized(self, mcp_server):
        """Test notification notifications/initialized."""
        request = {
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        }
        
        response = mcp_server.handle_request(request)
        
        # Notifications ne retournent rien
        assert response is None
    
    def test_tools_list(self, mcp_server):
        """Test requête tools/list."""
        request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/list'
        }
        
        response = mcp_server.handle_request(request)
        
        assert response is not None
        assert 'result' in response
        tools = response['result']['tools']
        assert len(tools) == 14
        
        # Vérifier présence de tous les outils de base
        tool_names = [t['name'] for t in tools]
        assert 'sonarqube_issues' in tool_names
        assert 'sonarqube_search_issues' in tool_names
        assert 'sonarqube_measures' in tool_names
        assert 'sonarqube_hotspots' in tool_names
        assert 'sonarqube_rule' in tool_names
        assert 'sonarqube_users' in tool_names
        assert 'sonarqube_quality_gate' in tool_names
        assert 'sonarqube_ping' in tool_names
        
        # Vérifier présence des nouveaux outils
        assert 'sonarqube_analyses_history' in tool_names
        assert 'sonarqube_duplications' in tool_names
        assert 'sonarqube_source_lines' in tool_names
        assert 'sonarqube_metrics_list' in tool_names
        assert 'sonarqube_languages' in tool_names
        assert 'sonarqube_projects' in tool_names
        
        # Vérifier qu'un outil a un schéma inputSchema valide
        issues_tool = next(t for t in tools if t['name'] == 'sonarqube_issues')
        assert 'inputSchema' in issues_tool
        assert 'properties' in issues_tool['inputSchema']
        assert 'file_path' in issues_tool['inputSchema']['properties']
    
    def test_ping(self, mcp_server):
        """Test requête ping."""
        request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'ping'
        }
        
        response = mcp_server.handle_request(request)
        
        assert response is not None
        assert response == {'result': {'status': 'pong'}}
    
    def test_unknown_method(self, mcp_server):
        """Test méthode inconnue."""
        request = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'unknown/method'
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'error' in response
        assert response['error']['code'] == -32601
        assert 'inconnue' in response['error']['message'].lower()
    
    def test_resources_list(self, mcp_server):
        """Test requête resources/list."""
        request = {
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'resources/list'
        }
        
        response = mcp_server.handle_request(request)
        
        assert response is not None
        assert 'result' in response
        assert 'resources' in response['result']
        
        # Vérifier que le projet par défaut est une ressource
        resources = response['result']['resources']
        assert len(resources) >= 1
        assert 'uri' in resources[0]
        assert resources[0]['uri'].startswith('sonarqube://project/')
    
    def test_resources_read(self, mcp_server):
        """Test requête resources/read."""
        request = {
            'jsonrpc': '2.0',
            'id': 6,
            'method': 'resources/read',
            'params': {
                'uri': 'sonarqube://project/TestProject'
            }
        }
        
        # Mock des méthodes API nécessaires avec des objets serializables
        from unittest.mock import Mock
        from src.models import Project, Component, Measure
        
        mock_project = Project(
            key='TestProject',
            name='Test Project',
            qualifier='TRK',
            visibility='public',
            last_analysis_date=None
        )
        
        mock_component = Component(
            key='TestProject',
            name='Test Project',
            qualifier='TRK',
            measures=[
                Measure(metric='ncloc', value='1000', best_value=False),
                Measure(metric='coverage', value='80', best_value=False)
            ]
        )
        
        mcp_server.api.projects.get_project = Mock(return_value=mock_project)
        mcp_server.api.measures.get_component_measures = Mock(return_value=mock_component)
        
        response = mcp_server.handle_request(request)
        
        assert response is not None
        assert 'result' in response
        assert 'contents' in response['result']
        assert len(response['result']['contents']) > 0
        
        content = response['result']['contents'][0]
        assert content['uri'] == 'sonarqube://project/TestProject'
        assert content['mimeType'] == 'application/json'
        assert 'text' in content
        
        # Vérifier que c'est du JSON valide
        data = json.loads(content['text'])
        assert 'project' in data
        assert data['project']['key'] == 'TestProject'
        assert 'measures' in data
        assert len(data['measures']) == 2
    
    def test_resources_read_unknown_uri(self, mcp_server):
        """Test lecture d'une ressource inconnue."""
        request = {
            'jsonrpc': '2.0',
            'id': 7,
            'method': 'resources/read',
            'params': {
                'uri': 'unknown://resource'
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'error' in response
        assert response['error']['code'] == -32602

