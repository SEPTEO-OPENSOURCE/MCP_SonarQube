"""API SonarQube - Endpoints Measures."""

from typing import List, Optional, Dict, Any
from .base import SonarQubeAPIBase
from ..models import Component


class MeasuresAPI(SonarQubeAPIBase):
    """Client pour les endpoints Measures."""
    
    def get_component(self, component_key: str, metric_keys: Optional[List[str]] = None) -> Component:
        """
        Récupère les métriques d'un composant.
        
        Args:
            component_key: Clé du composant (projet, fichier, etc.)
            metric_keys: Liste des métriques à récupérer
        
        Returns:
            Composant avec ses métriques
        """
        if metric_keys is None:
            metric_keys = [
                'ncloc', 'coverage', 'bugs', 'vulnerabilities', 'code_smells',
                'security_hotspots', 'duplicated_lines_density',
                'reliability_rating', 'security_rating', 'sqale_rating'
            ]
        
        params = {
            'component': component_key,
            'metricKeys': ','.join(metric_keys)
        }
        
        response = self._get('/api/measures/component', params)
        return Component.from_api_response(response['component'])
    
    def get_metrics_list(self, page: int = 1, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Liste toutes les métriques disponibles."""
        params = {'p': page, 'ps': page_size or self.config.page_size}
        return self._get('/api/metrics/search', params)
    
    def get_languages(self) -> Dict[str, Any]:
        """Récupère la liste des langages supportés."""
        return self._get('/api/languages/list', {})

