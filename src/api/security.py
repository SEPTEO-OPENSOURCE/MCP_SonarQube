"""API SonarQube - Endpoints Security Hotspots."""

from typing import Optional, Dict, Any
from .base import SonarQubeAPIBase
from ..models import Hotspot, HotspotStatus


class SecurityAPI(SonarQubeAPIBase):
    """Client pour les endpoints Security."""
    
    def search_hotspots(self, project_key: str, 
                        status: Optional[HotspotStatus] = None,
                        resolution: Optional[str] = None,
                        page: int = 1,
                        page_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Recherche les hotspots de sécurité.
        
        Args:
            project_key: Clé du projet
            status: Statut des hotspots
            resolution: Résolution (FIXED, SAFE, ACKNOWLEDGED)
            page: Numéro de page
            page_size: Taille de page
        
        Returns:
            Liste des hotspots
        """
        params = {
            'projectKey': project_key,
            'p': page,
            'ps': page_size or self.config.page_size
        }
        
        if status:
            params['status'] = status.value
        if resolution:
            params['resolution'] = resolution
        
        response = self._get('/api/hotspots/search', params)
        
        # Convertir en objets Hotspot
        if 'hotspots' in response:
            response['hotspots'] = [Hotspot.from_api_response(hotspot) for hotspot in response['hotspots']]
        
        return response
    
    def get_hotspot_detail(self, hotspot_key: str) -> Dict[str, Any]:
        """Récupère les détails d'un hotspot."""
        return self._get('/api/hotspots/show', {'hotspot': hotspot_key})





