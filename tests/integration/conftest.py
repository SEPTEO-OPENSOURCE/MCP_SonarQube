"""Fixtures pour tests d'intégration MCP."""

import pytest
from unittest.mock import Mock, patch
from src.config import SonarQubeConfig, ProjectConfig
from src.mcp.server import MCPServer


@pytest.fixture
def mock_config():
    """Configuration de test."""
    return SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test-token",
        default_project=ProjectConfig(
            key="TestProject",
            assignee="test-user"
        )
    )


@pytest.fixture
def mcp_server(mock_config):
    """Serveur MCP de test avec API mockée."""
    with patch('src.mcp.server.SonarQubeAPI'), \
         patch('src.mcp.server.CommandHandler'):
        server = MCPServer(mock_config)
        return server


@pytest.fixture
def mock_api_responses():
    """Réponses API mockées."""
    return {
        'issues': {'issues': [], 'total': 0},
        'measures': {'component': {'key': 'test', 'measures': []}},
        'hotspots': {'hotspots': []},
        'rule': {'rule': {'key': 'dart:S100', 'name': 'Test Rule'}},
        'users': {'users': []},
        'quality_gate': {'projectStatus': {'status': 'OK'}}
    }



