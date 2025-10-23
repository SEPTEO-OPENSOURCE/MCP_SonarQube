"""API SonarQube - Point d'entrée unifié."""

from .base import SonarQubeAPIBase, SonarQubeAPIError
from .issues import IssuesAPI
from .measures import MeasuresAPI
from .security import SecurityAPI
from .projects import ProjectsAPI
from .users import UsersAPI
from .rules import RulesAPI

from ..config import SonarQubeConfig
from typing import Optional, List, Dict, Any
from ..models import IssueType, Severity, HotspotStatus


class SonarQubeAPI:
    """
    Client API SonarQube unifié.
    
    Fournit un point d'accès unique à toutes les fonctionnalités de l'API SonarQube,
    organisées par domaine (issues, measures, security, etc.).
    
    Usage:
        >>> api = SonarQubeAPI(config)
        >>> # Nouvelle API (recommandée)
        >>> issues = api.issues.search(project_keys=['X'])
        >>> measures = api.measures.get_component('X')
        >>> # Ancienne API (compatibilité)
        >>> issues = api.search_issues(project_keys=['X'])
    """
    
    def __init__(self, config: SonarQubeConfig):
        self.config = config
        self.issues = IssuesAPI(config)
        self.measures = MeasuresAPI(config)
        self.security = SecurityAPI(config)
        self.projects = ProjectsAPI(config)
        self.users = UsersAPI(config)
        self.rules = RulesAPI(config)
    
    # Méthodes de compatibilité (déléguent aux nouveaux modules)
    
    def search_issues(self, **kwargs) -> Dict[str, Any]:
        """[Compatibility] Recherche des issues."""
        return self.issues.search(**kwargs)
    
    def get_issue_changelog(self, issue_key: str) -> Dict[str, Any]:
        """[Compatibility] Récupère l'historique d'une issue."""
        return self.issues.get_changelog(issue_key)
    
    def get_component_measures(self, component_key: str, metrics: Optional[List[str]] = None):
        """[Compatibility] Récupère les métriques d'un composant."""
        return self.measures.get_component(component_key, metrics)
    
    def search_hotspots(self, project_key: str, **kwargs) -> Dict[str, Any]:
        """[Compatibility] Recherche les hotspots de sécurité."""
        return self.security.search_hotspots(project_key, **kwargs)
    
    def get_rule(self, rule_key: str):
        """[Compatibility] Récupère les détails d'une règle."""
        return self.rules.get(rule_key)
    
    def search_rules(self, **kwargs) -> Dict[str, Any]:
        """[Compatibility] Recherche des règles."""
        return self.rules.search(**kwargs)
    
    def search_users(self, query: str, **kwargs):
        """[Compatibility] Recherche des utilisateurs."""
        return self.users.search(query, **kwargs)
    
    def search_projects(self, **kwargs):
        """[Compatibility] Recherche des projets."""
        return self.projects.search(**kwargs)
    
    def get_project(self, project_key: str):
        """[Compatibility] Récupère un projet."""
        return self.projects.get(project_key)
    
    def get_quality_gate_status(self, project_key: str) -> Dict[str, Any]:
        """[Compatibility] Récupère le statut du Quality Gate."""
        return self.projects.get_quality_gate_status(project_key)
    
    def get_server_version(self) -> str:
        """[Compatibility] Récupère la version du serveur."""
        return self.projects.get_server_version()
    
    def health_check(self) -> Dict[str, Any]:
        """[Compatibility] Vérifie la santé du serveur."""
        return self.projects.health_check()


__all__ = [
    'SonarQubeAPI',
    'SonarQubeAPIError',
    'IssuesAPI',
    'MeasuresAPI',
    'SecurityAPI',
    'ProjectsAPI',
    'UsersAPI',
    'RulesAPI',
]





