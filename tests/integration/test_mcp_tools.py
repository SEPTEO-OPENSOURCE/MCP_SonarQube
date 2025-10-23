"""Tests des appels d'outils MCP."""

import json
import pytest
from unittest.mock import Mock
from src.commands.base import CommandResult


class TestMCPTools:
    """Tests des appels d'outils."""
    
    def test_sonarqube_issues_no_params(self, mcp_server):
        """Test outil issues sans paramètres."""
        # Mock command_handler
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=True,
            data={'issues': [], 'total': 0},
            metadata={'mode': 'my-issues'}
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_issues',
                'arguments': {}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert response is not None
        assert 'result' in response
        assert 'content' in response['result']
        assert len(response['result']['content']) > 0
        
        # Vérifier que command_handler a été appelé
        mcp_server.command_handler.execute.assert_called_once()
        args = mcp_server.command_handler.execute.call_args[0]
        assert args[0] == 'issues'
    
    def test_sonarqube_issues_with_file_path(self, mcp_server):
        """Test outil issues avec file_path."""
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=True,
            data={'issues': []},
            metadata={'file_path': 'lib/main.dart'}
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_issues',
                'arguments': {'file_path': 'lib/main.dart'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        # Vérifier que file_path a été passé
        call_args = mcp_server.command_handler.execute.call_args[0][1]
        assert 'lib/main.dart' in call_args
    
    def test_sonarqube_issues_path_traversal(self, mcp_server):
        """Test outil issues avec path traversal (doit échouer)."""
        request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_issues',
                'arguments': {'file_path': '../../../etc/passwd'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        # Doit retourner une erreur
        assert 'error' in response
        assert response['error']['code'] == -32603
    
    def test_sonarqube_measures(self, mcp_server):
        """Test outil measures."""
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=True,
            data={'component': {'measures': []}}
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_measures',
                'arguments': {'project_key': 'TestProject'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        mcp_server.command_handler.execute.assert_called_once()
        args = mcp_server.command_handler.execute.call_args[0]
        assert args[0] == 'measures'
        assert 'TestProject' in args[1]
    
    def test_sonarqube_measures_invalid_project_key(self, mcp_server):
        """Test measures avec clé de projet invalide."""
        request = {
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_measures',
                'arguments': {'project_key': 'Invalid Key!'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        # Doit retourner une erreur
        assert 'error' in response
        assert response['error']['code'] == -32603
    
    def test_sonarqube_hotspots(self, mcp_server):
        """Test outil hotspots."""
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=True,
            data={'hotspots': []}
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 6,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_hotspots',
                'arguments': {'project_key': 'TestProject', 'status': 'TO_REVIEW'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        mcp_server.command_handler.execute.assert_called_once()
        args = mcp_server.command_handler.execute.call_args[0]
        assert args[0] == 'hotspots'
        assert 'TestProject' in args[1]
        assert 'TO_REVIEW' in args[1]
    
    def test_sonarqube_rule(self, mcp_server):
        """Test outil rule."""
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=True,
            data={'rule': {'key': 'dart:S100', 'name': 'Test Rule'}}
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 7,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_rule',
                'arguments': {'rule_key': 'dart:S100'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        mcp_server.command_handler.execute.assert_called_once()
        args = mcp_server.command_handler.execute.call_args[0]
        assert args[0] == 'rule'
        assert 'dart:S100' in args[1]
    
    def test_sonarqube_users(self, mcp_server):
        """Test outil users."""
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=True,
            data={'users': []}
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 8,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_users',
                'arguments': {'query': 'john'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        mcp_server.command_handler.execute.assert_called_once()
        args = mcp_server.command_handler.execute.call_args[0]
        assert args[0] == 'users'
        assert 'john' in args[1]
    
    def test_sonarqube_quality_gate(self, mcp_server):
        """Test outil quality_gate."""
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=True,
            data={'projectStatus': {'status': 'OK'}}
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 9,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_quality_gate',
                'arguments': {'project_key': 'TestProject'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        mcp_server.command_handler.execute.assert_called_once()
    
    def test_sonarqube_ping(self, mcp_server):
        """Test outil ping."""
        request = {
            'jsonrpc': '2.0',
            'id': 10,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_ping',
                'arguments': {}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        content = response['result']['content'][0]['text']
        data = json.loads(content)
        assert data['success'] is True
        assert data['message'] == 'pong'
        assert 'config' in data
    
    def test_unknown_tool(self, mcp_server):
        """Test outil inconnu."""
        request = {
            'jsonrpc': '2.0',
            'id': 11,
            'method': 'tools/call',
            'params': {
                'name': 'unknown_tool',
                'arguments': {}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'error' in response
        assert response['error']['code'] == -32602
    
    def test_tool_call_command_error(self, mcp_server):
        """Test appel outil avec erreur de commande."""
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=False,
            data=None,
            error="Erreur de test"
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 12,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_measures',
                'arguments': {'project_key': 'TestProject'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'error' in response
        assert response['error']['code'] == -32603
        assert 'Erreur de test' in response['error']['message']
    
    def test_sonarqube_projects_no_search(self, mcp_server):
        """Test outil projects sans recherche."""
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=True,
            data={'projects': [
                {'key': 'project1', 'name': 'Project 1'},
                {'key': 'project2', 'name': 'Project 2'}
            ]},
            metadata={'total': 2}
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 13,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_projects',
                'arguments': {}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        mcp_server.command_handler.execute.assert_called_once()
        args = mcp_server.command_handler.execute.call_args[0]
        assert args[0] == 'projects'
        assert args[1] == []
    
    def test_sonarqube_projects_with_search(self, mcp_server):
        """Test outil projects avec recherche."""
        mcp_server.command_handler.execute = Mock(return_value=CommandResult(
            success=True,
            data={'projects': [
                {'key': 'mobile-app', 'name': 'Mobile App'}
            ]},
            metadata={'total': 1}
        ))
        
        request = {
            'jsonrpc': '2.0',
            'id': 14,
            'method': 'tools/call',
            'params': {
                'name': 'sonarqube_projects',
                'arguments': {'search': 'mobile'}
            }
        }
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        mcp_server.command_handler.execute.assert_called_once()
        args = mcp_server.command_handler.execute.call_args[0]
        assert args[0] == 'projects'
        assert 'mobile' in args[1]
    
    def test_projects_tool_registration(self):
        """Test que l'outil sonarqube_projects est enregistré dans le registre."""
        from src.mcp.tools_registry import MCPToolsRegistry
        
        registry = MCPToolsRegistry()
        tool_names = registry.get_tool_names()
        
        assert 'sonarqube_projects' in tool_names
        
        # Vérifier le schéma
        schema = registry.get_tool_schema('sonarqube_projects')
        assert schema['name'] == 'sonarqube_projects'
        assert 'description' in schema
        assert 'inputSchema' in schema
        assert 'properties' in schema['inputSchema']
        assert 'search' in schema['inputSchema']['properties']
        assert schema['inputSchema']['required'] == []
    
    def test_projects_command_mapping(self, mcp_server):
        """Test que le serveur MCP a la méthode _convert_arguments."""
        assert hasattr(mcp_server, '_convert_arguments')
    
    def test_projects_command_handler_registration(self):
        """Test que la commande 'projects' est enregistrée dans CommandHandler."""
        from src.commands import CommandHandler
        from src.api import SonarQubeAPI
        from src.config import SonarQubeConfig
        
        config = SonarQubeConfig(
            url='http://localhost:9000',
            token='test-token'
        )
        api = SonarQubeAPI(config)
        handler = CommandHandler(api, config)
        
        assert 'projects' in handler.commands
        assert handler.commands['projects'] == handler.projects.list_projects



