"""
Module de gestion de la configuration SonarQube.

Gère les variables d'environnement, les fichiers de configuration,
et les paramètres multi-projets.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
    """Configuration spécifique à un projet SonarQube."""
    
    key: str
    name: Optional[str] = None
    branch: Optional[str] = "main"
    assignee: Optional[str] = None
    
    def __post_init__(self):
        if self.name is None:
            self.name = self.key


@dataclass
class SonarQubeConfig:
    """
    Gestionnaire de configuration centralisé pour SonarQube MCP.
    
    Supporte plusieurs sources de configuration :
    - Variables d'environnement
    - Fichier config.yaml
    - Fichier .env.local
    - Paramètres par défaut
    """
    
    url: str
    token: str
    default_project: Optional[ProjectConfig] = None
    projects: Dict[str, ProjectConfig] = field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
    page_size: int = 500
    verify_ssl: bool = True
    
    # Métadonnées MCP
    quality_audience: str = "assistant"
    quality_priority: float = 0.8
    security_audience: str = "assistant"
    security_priority: float = 0.9
    metadata_enabled: bool = True
    
    def __post_init__(self):
        # Normaliser l'URL (enlever le slash final)
        self.url = self.url.rstrip('/')
        
        # Valider la configuration
        self._validate()
    
    def _validate(self):
        """Valide la configuration minimale requise."""
        if not self.url:
            raise ValueError("SONARQUBE_URL est requis")
        if not self.token:
            raise ValueError("SONARQUBE_TOKEN est requis")
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("SONARQUBE_URL doit commencer par http:// ou https://")
    
    @classmethod
    def from_env(cls, config_file: Optional[str] = None) -> "SonarQubeConfig":
        """
        Crée une configuration à partir des variables d'environnement
        et optionnellement d'un fichier de configuration.
        
        Args:
            config_file: Chemin vers un fichier config.yaml (optionnel)
        
        Returns:
            Instance de SonarQubeConfig configurée
        
        Raises:
            ValueError: Si la configuration est invalide
            FileNotFoundError: Si le fichier de config spécifié n'existe pas
        """
        # Charger depuis les variables d'environnement
        url = os.getenv('SONARQUBE_URL')
        if not url:
            raise ValueError(
                "SONARQUBE_URL est requis dans l'environnement. "
                "Définissez-le avec: export SONARQUBE_URL='https://votre-sonarqube.com'"
            )
        
        token = os.getenv('SONARQUBE_TOKEN', '')
        
        config_data = {
            'url': url,
            'token': token,
            'timeout': int(os.getenv('SONARQUBE_TIMEOUT', '30')),
            'max_retries': int(os.getenv('SONARQUBE_MAX_RETRIES', '3')),
            'page_size': int(os.getenv('SONARQUBE_PAGE_SIZE', '500')),
            'verify_ssl': os.getenv('SONARQUBE_VERIFY_SSL', 'true').lower() == 'true',
            'quality_audience': os.getenv('SONARQUBE_QUALITY_AUDIENCE', 'assistant'),
            'quality_priority': float(os.getenv('SONARQUBE_QUALITY_PRIORITY', '0.8')),
            'security_audience': os.getenv('SONARQUBE_SECURITY_AUDIENCE', 'assistant'),
            'security_priority': float(os.getenv('SONARQUBE_SECURITY_PRIORITY', '0.9')),
            'metadata_enabled': os.getenv('SONARQUBE_METADATA_ENABLED', 'true').lower() == 'true',
        }
        
        # Charger le projet par défaut depuis l'environnement
        default_project_key = os.getenv('SONARQUBE_PROJECT_KEY')
        if default_project_key:
            config_data['default_project'] = ProjectConfig(
                key=default_project_key,
                name=os.getenv('SONARQUBE_PROJECT_NAME'),
                branch=os.getenv('SONARQUBE_PROJECT_BRANCH', 'main'),
                assignee=os.getenv('SONARQUBE_USER'),
            )
        
        # Charger depuis le fichier de configuration si fourni
        if config_file:
            file_config = cls._load_config_file(config_file)
            config_data.update(file_config)
        
        return cls(**config_data)
    
    @staticmethod
    def _load_config_file(config_file: str) -> Dict[str, Any]:
        """
        Charge la configuration depuis un fichier YAML.
        
        Args:
            config_file: Chemin vers le fichier de configuration
        
        Returns:
            Dictionnaire de configuration
        
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            yaml.YAMLError: Si le fichier YAML est invalide
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Fichier de configuration non trouvé : {config_file}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Convertir les projets en objets ProjectConfig
        if 'projects' in config and isinstance(config['projects'], list):
            projects_dict = {}
            for proj in config['projects']:
                proj_config = ProjectConfig(**proj)
                projects_dict[proj_config.key] = proj_config
            config['projects'] = projects_dict
        
        # Convertir le projet par défaut
        if 'default_project' in config and isinstance(config['default_project'], dict):
            config['default_project'] = ProjectConfig(**config['default_project'])
        
        return config
    
    def get_project(self, project_key: Optional[str] = None) -> Optional[ProjectConfig]:
        """
        Récupère la configuration d'un projet.
        
        Args:
            project_key: Clé du projet (utilise le projet par défaut si None)
        
        Returns:
            Configuration du projet ou None si non trouvé
        """
        if project_key is None:
            return self.default_project
        
        return self.projects.get(project_key, ProjectConfig(key=project_key))
    
    def add_project(self, project: ProjectConfig):
        """
        Ajoute un projet à la configuration.
        
        Args:
            project: Configuration du projet à ajouter
        """
        self.projects[project.key] = project
        if self.default_project is None:
            self.default_project = project
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire."""
        return {
            'url': self.url,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'page_size': self.page_size,
            'verify_ssl': self.verify_ssl,
            'default_project': self.default_project.__dict__ if self.default_project else None,
            'projects': {k: v.__dict__ for k, v in self.projects.items()},
        }




