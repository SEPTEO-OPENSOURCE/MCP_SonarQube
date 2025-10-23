"""Commandes liées aux issues SonarQube."""

from typing import List
from .base import BaseCommands, CommandResult, ERROR_NO_PROJECT, ERROR_NO_USER
from ..models import IssueType, Severity, IssueStatus
from ..api import SonarQubeAPIError


class IssuesCommands(BaseCommands):
    """Commandes pour gérer les issues."""
    
    def issues(self, args: List[str]) -> CommandResult:
        """
        Récupère les issues d'un projet.
        
        Usage: 
        - issues (sans paramètre) -> utilise SONARQUBE_PROJECT_KEY et SONARQUBE_USER (mes issues)
        - issues <project_key> -> toutes les issues du projet
        - issues <project_key> <assignee> -> issues du projet assignées à l'utilisateur
        - issues <project_key> <assignee> <file_path> -> issues filtrées par fichier
        """
        try:
            # Cas 1 : Sans paramètre -> mes issues (utilise la config par défaut)
            if len(args) == 0:
                project_key = self.config.default_project.key if self.config.default_project else None
                assignee = self.config.default_project.assignee if self.config.default_project else None
                
                if not project_key:
                    return self._error(ERROR_NO_PROJECT)
                
                if not assignee:
                    return self._error(ERROR_NO_USER)
                
                result = self.api.search_issues(
                    project_keys=[project_key],
                    assignees=[assignee],
                    resolved=False
                )
                
                return self._success(
                    data=result,
                    metadata={
                        'total': result.get('total', 0),
                        'project': project_key,
                        'assignee': assignee,
                        'mode': 'my-issues'
                    }
                )
            
            # Cas 2+ : Avec paramètres
            project_key = args[0]
            assignees = None
            files = None
            
            # Si 2+ arguments, le 2ème est l'assignee
            if len(args) >= 2:
                assignees = [args[1]]
            
            # Si 3 arguments, le 3ème est le file_path
            if len(args) >= 3:
                files = [args[2]]
            
            result = self.api.search_issues(
                project_keys=[project_key],
                assignees=assignees,
                files=files,
                resolved=False
            )
            
            return self._success(
                data=result,
                metadata={
                    'total': result.get('total', 0),
                    'project': project_key,
                    'assignee': assignees[0] if assignees else None,
                    'file_path': files[0] if files else None
                }
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, "Erreur lors de la récupération des issues")
    
    def my_issues(self, args: List[str]) -> CommandResult:
        """
        Récupère VOS issues (utilise variables d'environnement).
        
        Usage: my-issues [project_key] [assignee]
        """
        try:
            # Récupérer les valeurs depuis les arguments ou la config par défaut
            project_key = args[0] if len(args) > 0 else (self.config.default_project.key if self.config.default_project else None)
            assignee = args[1] if len(args) > 1 else (self.config.default_project.assignee if self.config.default_project else None)
            
            # Vérifier que nous avons les valeurs nécessaires
            if not project_key:
                return self._error(ERROR_NO_PROJECT)
            
            if not assignee:
                return self._error(ERROR_NO_USER)
            
            result = self.api.search_issues(
                project_keys=[project_key],
                assignees=[assignee],
                resolved=False
            )
            
            return self._success(
                data=result,
                metadata={
                    'total': result.get('total', 0),
                    'assignee': assignee,
                    'project': project_key
                }
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, "Erreur lors de la récupération de vos issues")
    
    def search_issues(self, args: List[str]) -> CommandResult:
        """
        Recherche des issues dans un projet avec filtrage optionnel par utilisateur et statut(s).
        
        Usage: 
        - search-issues <project_key> -> toutes les issues du projet
        - search-issues <project_key> <assignee> -> issues assignées à l'utilisateur
        - search-issues <project_key> "" -> issues non assignées (assignee vide)
        - search-issues <project_key> <assignee> <status> -> filtrer par statut (OPEN, CONFIRMED, FALSE_POSITIVE, ACCEPTED, FIXED, IN_SANDBOX)
        - search-issues <project_key> <assignee> <status1,status2,...> -> filtrer par plusieurs statuts (séparés par des virgules)
        """
        if not args:
            return self._error("Usage: search-issues <project_key> [assignee] [status1,status2,...]")
        
        try:
            project_key = args[0]
            assignees = None
            statuses = None
            
            # Si un assignee est spécifié (y compris vide)
            if len(args) >= 2:
                assignee = args[1]
                if assignee:  # Non vide -> filtrer par assignee
                    assignees = [assignee]
                else:  # Vide -> filtrer issues non assignées
                    assignees = ['']
            
            # Si un ou plusieurs statuts sont spécifiés (séparés par des virgules)
            if len(args) >= 3:
                status_arg = args[2]
                if status_arg:
                    try:
                        # Séparer les statuts par des virgules et les convertir
                        status_values = [s.strip() for s in status_arg.split(',') if s.strip()]
                        statuses = [IssueStatus(status) for status in status_values]
                    except ValueError as e:
                        invalid_status = str(e).split("'")[1] if "'" in str(e) else status_arg
                        return self._error(f"Statut invalide: {invalid_status}. Valeurs valides: OPEN, CONFIRMED, FALSE_POSITIVE, ACCEPTED, FIXED, IN_SANDBOX")
            
            result = self.api.search_issues(
                project_keys=[project_key],
                assignees=assignees,
                statuses=statuses
            )
            
            metadata = {
                'total': result.get('total', 0),
                'project': project_key
            }
            
            if assignees is not None:
                if assignees == ['']:
                    metadata['filter'] = 'unassigned'
                else:
                    metadata['assignee'] = assignees[0]
            else:
                metadata['filter'] = 'all'
            
            if statuses is not None:
                if len(statuses) == 1:
                    metadata['status'] = statuses[0].value
                else:
                    metadata['statuses'] = [s.value for s in statuses]
            
            return self._success(
                data=result,
                metadata=metadata
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, "Erreur lors de la recherche des issues")
    
    def changelog(self, args: List[str]) -> CommandResult:
        """
        Récupère l'historique d'une issue.
        
        Usage: issue-changelog <issue_key>
        """
        if not args:
            return self._error("Usage: issue-changelog <issue_key>")
        
        try:
            issue_key = args[0]
            result = self.api.get_issue_changelog(issue_key)
            
            return self._success(data=result)
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, f"Erreur lors de la récupération de l'historique de {args[0]}")
    
    def by_type(self, args: List[str]) -> CommandResult:
        """
        Filtre les issues par type.
        
        Usage: issues-by-type <project_key> <type> [assignee]
        Types: BUG, VULNERABILITY, CODE_SMELL, SECURITY_HOTSPOT
        """
        if len(args) < 2:
            return self._error("Usage: issues-by-type <project_key> <type> [assignee]")
        
        try:
            project_key = args[0]
            issue_type = IssueType(args[1])
            assignees = [args[2]] if len(args) > 2 else None
            
            result = self.api.search_issues(
                project_keys=[project_key],
                types=[issue_type],
                assignees=assignees,
                resolved=False
            )
            
            return self._success(
                data=result,
                metadata={
                    'total': result.get('total', 0),
                    'type': issue_type.value,
                    'project': project_key
                }
            )
        
        except (ValueError, SonarQubeAPIError) as e:
            return self._handle_api_error(e, "Erreur lors du filtrage par type")
    
    def by_severity(self, args: List[str]) -> CommandResult:
        """
        Filtre les issues par sévérité.
        
        Usage: issues-by-severity <project_key> <severity> [assignee]
        Severities: BLOCKER, CRITICAL, MAJOR, MINOR, INFO
        """
        if len(args) < 2:
            return self._error("Usage: issues-by-severity <project_key> <severity> [assignee]")
        
        try:
            project_key = args[0]
            severity = Severity(args[1])
            assignees = [args[2]] if len(args) > 2 else None
            
            result = self.api.search_issues(
                project_keys=[project_key],
                severities=[severity],
                assignees=assignees,
                resolved=False
            )
            
            return self._success(
                data=result,
                metadata={
                    'total': result.get('total', 0),
                    'severity': severity.value,
                    'project': project_key
                }
            )
        
        except (ValueError, SonarQubeAPIError) as e:
            return self._handle_api_error(e, "Erreur lors du filtrage par sévérité")
    
    # Raccourcis par type
    
    def bugs(self, args: List[str]) -> CommandResult:
        """
        Raccourci pour lister les bugs.
        
        Usage: bugs [project_key]
        """
        project_key = args[0] if args else (self.config.default_project.key if self.config.default_project else None)
        
        if not project_key:
            return self._error(ERROR_NO_PROJECT)
        
        return self.by_type([project_key, 'BUG'])
    
    def vulnerabilities(self, args: List[str]) -> CommandResult:
        """
        Raccourci pour lister les vulnérabilités.
        
        Usage: vulnerabilities [project_key]
        """
        project_key = args[0] if args else (self.config.default_project.key if self.config.default_project else None)
        
        if not project_key:
            return self._error(ERROR_NO_PROJECT)
        
        return self.by_type([project_key, 'VULNERABILITY'])
    
    def code_smells(self, args: List[str]) -> CommandResult:
        """
        Raccourci pour lister les code smells.
        
        Usage: code-smells [project_key]
        """
        project_key = args[0] if args else (self.config.default_project.key if self.config.default_project else None)
        
        if not project_key:
            return self._error(ERROR_NO_PROJECT)
        
        return self.by_type([project_key, 'CODE_SMELL'])





