"""Tests pour le module de configuration."""

import os
import pytest
import tempfile
from pathlib import Path

from src.config import SonarQubeConfig, ProjectConfig


class TestProjectConfig:
    """Tests pour ProjectConfig."""
    
    def test_project_config_creation(self):
        """Test la création d'un ProjectConfig."""
        project = ProjectConfig(
            key="test-project",
            name="Test Project",
            branch="main",
            assignee="test-user"
        )
        
        assert project.key == "test-project"
        assert project.name == "Test Project"
        assert project.branch == "main"
        assert project.assignee == "test-user"
    
    def test_project_config_default_name(self):
        """Test que le nom par défaut est la clé."""
        project = ProjectConfig(key="test-project")
        assert project.name == "test-project"


class TestSonarQubeConfig:
    """Tests pour SonarQubeConfig."""
    
    def test_config_validation(self):
        """Test la validation de la configuration."""
        # Configuration valide
        config = SonarQubeConfig(
            url="https://sonarqube.example.com",
            token="test-token"
        )
        assert config.url == "https://sonarqube.example.com"
        assert config.token == "test-token"
    
    def test_config_url_normalization(self):
        """Test la normalisation de l'URL."""
        config = SonarQubeConfig(
            url="https://sonarqube.example.com/",
            token="test-token"
        )
        assert config.url == "https://sonarqube.example.com"
    
    def test_config_validation_missing_url(self):
        """Test la validation avec URL manquante."""
        with pytest.raises(ValueError, match="SONARQUBE_URL est requis"):
            SonarQubeConfig(url="", token="test-token")
    
    def test_config_validation_missing_token(self):
        """Test la validation avec token manquant."""
        with pytest.raises(ValueError, match="SONARQUBE_TOKEN est requis"):
            SonarQubeConfig(
                url="https://sonarqube.example.com",
                token=""
            )
    
    def test_config_validation_invalid_url(self):
        """Test la validation avec URL invalide."""
        with pytest.raises(ValueError, match="doit commencer par http"):
            SonarQubeConfig(
                url="sonarqube.example.com",
                token="test-token"
            )
    
    def test_config_from_env(self, monkeypatch):
        """Test la création depuis les variables d'environnement."""
        monkeypatch.setenv('SONARQUBE_URL', 'https://test.com')
        monkeypatch.setenv('SONARQUBE_TOKEN', 'test-token')
        monkeypatch.setenv('SONARQUBE_TIMEOUT', '60')
        monkeypatch.setenv('SONARQUBE_PROJECT_KEY', 'test-project')
        
        config = SonarQubeConfig.from_env()
        
        assert config.url == "https://test.com"
        assert config.token == "test-token"
        assert config.timeout == 60
        assert config.default_project is not None
        assert config.default_project.key == "test-project"
    
    def test_config_from_yaml_file(self, monkeypatch):
        """Test la création depuis un fichier YAML."""
        monkeypatch.setenv('SONARQUBE_URL', 'https://test.com')
        monkeypatch.setenv('SONARQUBE_TOKEN', 'test-token')
        
        # Créer un fichier YAML temporaire
        yaml_content = """
url: "https://yaml.com"
timeout: 45
projects:
  - key: "project1"
    name: "Project 1"
  - key: "project2"
    name: "Project 2"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            config = SonarQubeConfig.from_env(config_file=temp_file)
            
            assert config.url == "https://yaml.com"
            assert config.timeout == 45
            assert len(config.projects) == 2
            assert "project1" in config.projects
            assert "project2" in config.projects
        finally:
            os.unlink(temp_file)
    
    def test_get_project(self):
        """Test la récupération d'un projet."""
        default_project = ProjectConfig(key="default")
        other_project = ProjectConfig(key="other")
        
        config = SonarQubeConfig(
            url="https://test.com",
            token="test-token",
            default_project=default_project
        )
        config.add_project(other_project)
        
        # Récupérer le projet par défaut
        assert config.get_project() == default_project
        
        # Récupérer un projet spécifique
        assert config.get_project("other") == other_project
        
        # Récupérer un projet inconnu
        unknown = config.get_project("unknown")
        assert unknown.key == "unknown"
    
    def test_add_project(self):
        """Test l'ajout d'un projet."""
        config = SonarQubeConfig(
            url="https://test.com",
            token="test-token"
        )
        
        project = ProjectConfig(key="test")
        config.add_project(project)
        
        assert "test" in config.projects
        assert config.default_project == project
    
    def test_to_dict(self):
        """Test la conversion en dictionnaire."""
        config = SonarQubeConfig(
            url="https://test.com",
            token="test-token",
            timeout=45
        )
        
        data = config.to_dict()
        
        assert data['url'] == "https://test.com"
        assert data['timeout'] == 45
        assert 'token' not in data  # Le token ne doit pas être dans to_dict




