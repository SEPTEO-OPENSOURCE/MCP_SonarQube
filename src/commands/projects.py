"""Commandes liées aux projets SonarQube."""

from typing import List, Optional
from .base import BaseCommands, CommandResult
from ..api import SonarQubeAPIError


class ProjectsCommands(BaseCommands):
    """Commandes pour gérer les projets."""
    
    def get_info(self, args: List[str]) -> CommandResult:
        """
        Récupère les informations d'un projet.
        
        Usage: project-info <project_key>
        """
        if not args:
            return self._error("Usage: project-info <project_key>")
        
        try:
            project_key = args[0]
            project = self.api.get_project(project_key)
            
            if not project:
                return self._error(f"Projet non trouvé: {project_key}")
            
            return self._success(
                data={
                    'key': project.key,
                    'name': project.name,
                    'qualifier': project.qualifier,
                    'visibility': project.visibility,
                    'last_analysis_date': project.last_analysis_date
                }
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, f"Erreur lors de la récupération du projet {args[0]}")
    
    def list_projects(self, args: List[str]) -> CommandResult:
        """
        Liste les projets.
        
        Usage: projects [search_term]
        """
        try:
            query = args[0] if args else None
            projects = self.api.search_projects(query=query)
            
            return self._success(
                data={
                    'projects': [
                        {
                            'key': p.key,
                            'name': p.name,
                            'qualifier': p.qualifier,
                            'visibility': p.visibility,
                            'last_analysis_date': p.last_analysis_date
                        }
                        for p in projects
                    ]
                },
                metadata={'total': len(projects)}
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, "Erreur lors de la recherche de projets")
    
    def get_quality_gate(self, args: List[str]) -> CommandResult:
        """
        Récupère le statut du Quality Gate.
        
        Usage: quality-gate <project_key>
        """
        if not args:
            return self._error("Usage: quality-gate <project_key>")
        
        try:
            project_key = args[0]
            result = self.api.get_quality_gate_status(project_key)
            
            return self._success(data=result)
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, f"Erreur lors de la récupération du quality gate de {args[0]}")
    
    def health_check(self, args: List[str]) -> CommandResult:  # noqa: ARG002
        """
        Vérifie la santé du serveur SonarQube.
        
        Usage: health
        """
        try:
            result = self.api.health_check()
            return self._success(data=result)
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, "Erreur lors de la vérification de santé")
    
    def get_version(self, args: List[str]) -> CommandResult:  # noqa: ARG002
        """
        Récupère la version du serveur SonarQube.
        
        Usage: version
        """
        try:
            version = self.api.get_server_version()
            return self._success(data={'version': version})
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, "Erreur lors de la récupération de la version")
    
    def get_analyses_history(self, args: List[str]) -> CommandResult:
        """
        Récupère l'historique des analyses d'un projet.
        
        Usage: analyses [project_key] [from_date] [to_date]
        """
        try:
            project_key = args[0] if args else self._get_default_project_key()
            from_date = args[1] if len(args) > 1 else None
            to_date = args[2] if len(args) > 2 else None
            
            result = self.api.projects.get_analyses_history(project_key, from_date, to_date)
            return self._success(data=result)
        
        except SonarQubeAPIError as e:
            project_ref = args[0] if args else "projet par défaut"
            return self._handle_api_error(e, f"Erreur lors de la récupération de l'historique des analyses de {project_ref}")
    
    def get_duplications(self, args: List[str]) -> CommandResult:
        """
        Récupère les duplications de code d'un fichier.
        
        Usage: duplications <file_key>
        """
        if not args:
            return self._error("Usage: duplications <file_key>")
        
        try:
            file_key = args[0]
            result = self.api.projects.get_duplications(file_key)
            return self._success(data=result)
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, f"Erreur lors de la récupération des duplications de {args[0]}")
    
    def get_source_lines(self, args: List[str]) -> CommandResult:
        """
        Récupère le code source annoté d'un fichier.
        
        Usage: source-lines <file_key> [from_line] [to_line]
        """
        if not args:
            return self._error("Usage: source-lines <file_key> [from_line] [to_line]")
        
        try:
            file_key = args[0]
            from_line = int(args[1]) if len(args) > 1 else 1
            to_line = int(args[2]) if len(args) > 2 else None
            
            result = self.api.projects.get_source_lines(file_key, from_line, to_line)
            return self._success(data=result)
        
        except ValueError:
            return self._error("Les numéros de ligne doivent être des entiers")
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, f"Erreur lors de la récupération du code source de {args[0]}")

