"""API SonarQube - Endpoints Issues."""

from typing import List, Optional, Dict, Any
from .base import SonarQubeAPIBase
from ..models import Issue, IssueType, Severity, IssueStatus


class IssuesAPI(SonarQubeAPIBase):
    """Client pour les endpoints Issues."""
    
    def search(self, 
               project_keys: Optional[List[str]] = None,
               assignees: Optional[List[str]] = None,
               types: Optional[List[IssueType]] = None,
               severities: Optional[List[Severity]] = None,
               statuses: Optional[List[IssueStatus]] = None,
               resolved: Optional[bool] = None,
               files: Optional[List[str]] = None,
               rules: Optional[List[str]] = None,
               tags: Optional[List[str]] = None,
               page: int = 1,
               page_size: Optional[int] = None) -> Dict[str, Any]:
        """Recherche des issues avec filtres multiples."""
        params = {
            'p': page,
            'ps': page_size or self.config.page_size
        }
        
        if resolved is not None:
            params['resolved'] = 'true' if resolved else 'false'
        
        if project_keys:
            params['componentKeys'] = ','.join(project_keys)
        if assignees and assignees[0] != '':
            params['assignees'] = ','.join(assignees)
        if types:
            params['types'] = ','.join([t.value for t in types])
        if severities:
            params['severities'] = ','.join([s.value for s in severities])
        if statuses:
            params['issueStatuses'] = ','.join([s.value for s in statuses])
        if files:
            params['files'] = ','.join(files)
        if rules:
            params['rules'] = ','.join(rules)
        if tags:
            params['tags'] = ','.join(tags)
        
        response = self._get('/api/issues/search', params)
        
        # Convertir en objets Issue
        if 'issues' in response:
            response['issues'] = [Issue.from_api_response(issue) for issue in response['issues']]
        
        return response
    
    def get_changelog(self, issue_key: str) -> Dict[str, Any]:
        """Récupère l'historique d'une issue."""
        return self._get('/api/issues/changelog', {'issue': issue_key})
    
    def assign(self, issue_key: str, assignee: str) -> Dict[str, Any]:
        """Assigne une issue à un utilisateur."""
        return self._post('/api/issues/assign', {'issue': issue_key, 'assignee': assignee})
    
    def add_comment(self, issue_key: str, text: str) -> Dict[str, Any]:
        """Ajoute un commentaire à une issue."""
        return self._post('/api/issues/add_comment', {'issue': issue_key, 'text': text})
    
    def set_severity(self, issue_key: str, severity: Severity) -> Dict[str, Any]:
        """Modifie la sévérité d'une issue."""
        return self._post('/api/issues/set_severity', {'issue': issue_key, 'severity': severity.value})
    
    def set_type(self, issue_key: str, issue_type: IssueType) -> Dict[str, Any]:
        """Modifie le type d'une issue."""
        return self._post('/api/issues/set_type', {'issue': issue_key, 'type': issue_type.value})





