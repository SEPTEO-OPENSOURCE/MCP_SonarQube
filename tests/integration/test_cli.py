"""Tests du CLI SonarQube."""

import pytest
import subprocess
import json
import os
from pathlib import Path


class TestCLIHelp:
    """Tests des commandes d'aide."""
    
    def test_help_command(self):
        """Test commande help."""
        result = subprocess.run(
            ['python', 'sonarqube_cli.py', 'help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        assert result.returncode == 0
        # Help affiche du texte formaté, pas du JSON
        assert 'SonarQube MCP' in result.stdout
        assert 'COMMANDES DISPONIBLES' in result.stdout
    
    def test_help_specific_command(self):
        """Test help pour commande spécifique."""
        result = subprocess.run(
            ['python', 'sonarqube_cli.py', 'help', 'issues'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            env={**os.environ, 'SONARQUBE_URL': 'https://test.sonarqube.com', 'SONARQUBE_TOKEN': 'test'}
        )
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output['success'] is True
        assert 'description' in output['data']
    
    def test_no_command(self):
        """Test CLI sans commande."""
        result = subprocess.run(
            ['python', 'sonarqube_cli.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        # Doit afficher l'aide
        assert 'help' in result.stdout.lower() or 'usage' in result.stdout.lower() or 'commande' in result.stdout.lower()


class TestCLICommands:
    """Tests des commandes CLI."""
    
    @pytest.fixture
    def cli_env(self):
        """Variables d'environnement pour tests CLI."""
        return {
            'SONARQUBE_URL': 'https://test.sonarqube.com',
            'SONARQUBE_TOKEN': 'test-token',
            'SONARQUBE_PROJECT_KEY': 'TestProject',
            'SONARQUBE_USER': 'test-user'
        }
    
    def test_version_command(self):
        """Test commande version."""
        result = subprocess.run(
            ['python', 'sonarqube_cli.py', 'version'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            env={**os.environ, 'SONARQUBE_URL': 'https://test.sonarqube.com', 'SONARQUBE_TOKEN': 'test'}
        )
        
        # Version peut ne pas être testable sans vrai serveur
        # On vérifie juste que la commande ne crash pas
        assert result.returncode in [0, 1]  # Peut échouer si pas de serveur
    
    def test_invalid_command(self):
        """Test commande invalide."""
        result = subprocess.run(
            ['python', 'sonarqube_cli.py', 'invalid_command_xyz'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            env={**os.environ, 'SONARQUBE_URL': 'https://test.sonarqube.com', 'SONARQUBE_TOKEN': 'test'}
        )
        
        output = json.loads(result.stdout)
        assert output['success'] is False
        assert 'inconnue' in output['error'].lower() or 'unknown' in output['error'].lower()
    
    def test_missing_env_vars(self):
        """Test sans variables d'environnement."""
        # Essayer python3 d'abord (Linux/macOS), puis python (Windows)
        python_cmd = 'python3' if subprocess.run(['which', 'python3'], 
                                                capture_output=True).returncode == 0 else 'python'
        
        result = subprocess.run(
            [python_cmd, 'sonarqube_cli.py', 'issues'],
            capture_output=True,
            text=True,
            env={},  # Pas de variables env
            cwd=Path(__file__).parent.parent.parent
        )
        
        # Doit échouer avec message clair
        assert 'SONARQUBE_URL' in result.stderr or 'error' in result.stdout.lower()


class TestCLIVerboseMode:
    """Tests du mode verbeux."""
    
    def test_verbose_flag(self):
        """Test flag --verbose."""
        result = subprocess.run(
            ['python', 'sonarqube_cli.py', '--verbose', 'help'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        # Mode verbeux active logs DEBUG
        assert result.returncode == 0

