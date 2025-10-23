"""API SonarQube - Endpoints Projects & Quality Gates."""

from typing import List, Optional, Dict, Any
from .base import SonarQubeAPIBase
from ..models import Project


class ProjectsAPI(SonarQubeAPIBase):
    """Client pour les endpoints Projects."""
    
    def search(self, query: Optional[str] = None, page: int = 1, page_size: Optional[int] = None) -> List[Project]:
        """Recherche des projets."""
        params = {
            'p': page,
            'ps': page_size or self.config.page_size
        }
        
        if query:
            params['q'] = query
        
        # Utilise /api/components/search_projects qui nécessite moins de permissions
        # que /api/projects/search (pas besoin de permission "Administer System")
        response = self._get('/api/components/search_projects', params)
        return [Project.from_api_response(proj) for proj in response.get('components', [])]
    
    def get(self, project_key: str) -> Optional[Project]:
        """Récupère un projet spécifique."""
        projects = self.search(query=project_key)
        return projects[0] if projects else None
    
    def get_quality_gate_status(self, project_key: str) -> Dict[str, Any]:
        """Récupère le statut du Quality Gate d'un projet."""
        return self._get('/api/qualitygates/project_status', {'projectKey': project_key})
    
    def get_component_tree(self, component_key: str, qualifiers: Optional[List[str]] = None,
                           page: int = 1, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Récupère l'arborescence d'un composant."""
        params = {
            'component': component_key,
            'p': page,
            'ps': page_size or self.config.page_size
        }
        
        if qualifiers:
            params['qualifiers'] = ','.join(qualifiers)
        
        return self._get('/api/components/tree', params)
    
    def get_component_sources(self, component_key: str, from_line: int = 1, to_line: Optional[int] = None) -> Dict[str, Any]:
        """Récupère le code source d'un composant."""
        params = {'key': component_key, 'from': from_line}
        if to_line:
            params['to'] = to_line
        return self._get('/api/sources/lines', params)
    
    def get_server_version(self) -> str:
        """Récupère la version du serveur SonarQube."""
        url = f"{self.config.url}/api/server/version"
        response = self.session.get(url, timeout=self.config.timeout, verify=self.config.verify_ssl)
        response.raise_for_status()
        return response.text.strip()
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé du serveur SonarQube."""
        return self._get('/api/system/health')
    
    def get_analyses_history(self, project_key: str, from_date: Optional[str] = None, 
                             to_date: Optional[str] = None, page: int = 1, 
                             page_size: Optional[int] = None) -> Dict[str, Any]:
        """Récupère l'historique des analyses d'un projet."""
        params = {'project': project_key, 'p': page, 'ps': page_size or self.config.page_size}
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        return self._get('/api/project_analyses/search', params)
    
    def get_duplications(self, file_key: str) -> Dict[str, Any]:
        """Récupère les duplications de code d'un fichier."""
        return self._get('/api/duplications/show', {'key': file_key})
    
    def get_source_lines(self, file_key: str, from_line: int = 1, 
                         to_line: Optional[int] = None) -> Dict[str, Any]:
        """Récupère le code source annoté d'un fichier."""
        params = {'key': file_key, 'from': from_line}
        if to_line:
            params['to'] = to_line
        return self._get('/api/sources/lines', params)

