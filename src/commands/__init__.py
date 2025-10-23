"""Package de commandes modulaire pour SonarQube MCP."""

import logging
from typing import Dict, Any, List
from .base import CommandResult, BaseCommands
from .issues import IssuesCommands
from .measures import MeasuresCommands
from .security import SecurityCommands
from .projects import ProjectsCommands
from .users import UsersCommands

from ..api import SonarQubeAPI
from ..config import SonarQubeConfig


logger = logging.getLogger(__name__)


class CommandHandler:
    """
    Gestionnaire principal des commandes.
    Délègue aux sous-groupes spécialisés.
    """
    
    def __init__(self, api: SonarQubeAPI, config: SonarQubeConfig):
        """
        Initialise le gestionnaire de commandes.
        
        Args:
            api: Instance de l'API SonarQube
            config: Configuration SonarQube
        """
        self.api = api
        self.config = config
        
        # Initialiser les groupes de commandes
        self.issues = IssuesCommands(api, config)
        self.measures = MeasuresCommands(api, config)
        self.security = SecurityCommands(api, config)
        self.projects = ProjectsCommands(api, config)
        self.users = UsersCommands(api, config)
        
        # Enregistrer toutes les commandes
        self.commands = self._register_commands()
    
    def _register_commands(self) -> Dict[str, Any]:
        """Enregistre toutes les commandes disponibles."""
        return {
            # Issues
            'issues': self.issues.issues,
            'my-issues': self.issues.my_issues,
            'mine': self.issues.my_issues,  # Alias
            'search-issues': self.issues.search_issues,
            'issue-changelog': self.issues.changelog,
            'issues-by-type': self.issues.by_type,
            'issues-by-severity': self.issues.by_severity,
            'bugs': self.issues.bugs,
            'vulnerabilities': self.issues.vulnerabilities,
            'code-smells': self.issues.code_smells,
            
            # Measures
            'measures': self.measures.get_measures,
            'metrics': self.measures.get_measures,  # Alias
            'metrics-list': self.measures.get_metrics_list,
            'languages': self.measures.get_languages,
            
            # Security
            'hotspots': self.security.get_hotspots,
            'security-hotspots': self.security.get_hotspots,  # Alias
            
            # Projects
            'project-info': self.projects.get_info,
            'projects': self.projects.list_projects,
            'quality-gate': self.projects.get_quality_gate,
            'health': self.projects.health_check,
            'version': self.projects.get_version,
            'analyses': self.projects.get_analyses_history,
            'analyses-history': self.projects.get_analyses_history,  # Alias
            'duplications': self.projects.get_duplications,
            'source-lines': self.projects.get_source_lines,
            
            # Users & Rules
            'users': self.users.search_users,
            'search-users': self.users.search_users,  # Alias
            'rule': self.users.get_rule,
            'rules': self.users.search_rules,
            
            # Help
            'help': self._help,
            'commands': self._help,  # Alias
        }
    
    def execute(self, command: str, args: List[str]) -> CommandResult:
        """
        Exécute une commande.
        
        Args:
            command: Nom de la commande
            args: Arguments de la commande
        
        Returns:
            Résultat de la commande
        """
        if command not in self.commands:
            return CommandResult(
                success=False,
                data=None,
                error=f"Commande inconnue: {command}. Utilisez 'help' pour voir les commandes disponibles."
            )
        
        try:
            return self.commands[command](args)
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de {command}: {e}", exc_info=True)
            return CommandResult(
                success=False,
                data=None,
                error=f"Erreur lors de l'exécution de la commande: {str(e)}"
            )
    
    def execute_command(self, command: str, args: List[str]) -> CommandResult:
        """
        Alias pour execute() pour rétrocompatibilité.
        
        Args:
            command: Nom de la commande
            args: Arguments de la commande
        
        Returns:
            Résultat de la commande
        """
        return self.execute(command, args)
    
    def _help(self, args: List[str]) -> CommandResult:
        """
        Affiche l'aide des commandes.
        
        Usage: help [command]
        """
        if args:
            # Aide pour une commande spécifique
            command = args[0]
            if command not in self.commands:
                return CommandResult(
                    success=False,
                    data=None,
                    error=f"Commande inconnue: {command}"
                )
            
            func = self.commands[command]
            return CommandResult(
                success=True,
                data={
                    'command': command,
                    'description': func.__doc__
                }
            )
        
        # Aide générale
        commands_by_category = {
            'Issues': [
                'issues', 'my-issues', 'mine', 'search-issues', 'issue-changelog', 
                'issues-by-type', 'issues-by-severity'
            ],
            'Raccourcis Issues': [
                'bugs', 'vulnerabilities', 'code-smells'
            ],
            'Métriques': ['measures', 'metrics', 'metrics-list', 'languages'],
            'Sécurité': ['hotspots', 'security-hotspots'],
            'Projets': ['project-info', 'projects', 'quality-gate', 'analyses', 'analyses-history'],
            'Code Source': ['duplications', 'source-lines'],
            'Système': ['health', 'version'],
            'Utilisateurs': ['users', 'search-users'],
            'Règles': ['rule', 'rules'],
            'Aide': ['help', 'commands']
        }
        
        return CommandResult(
            success=True,
            data={
                'commands': commands_by_category,
                'usage': 'Utilisez "help <command>" pour plus de détails sur une commande'
            }
        )


__all__ = [
    'CommandHandler',
    'CommandResult',
    'BaseCommands',
    'IssuesCommands',
    'MeasuresCommands',
    'SecurityCommands',
    'ProjectsCommands',
    'UsersCommands',
]





