"""API SonarQube - Endpoints Rules."""

from typing import List, Optional, Dict, Any
from .base import SonarQubeAPIBase
from ..models import Rule


class RulesAPI(SonarQubeAPIBase):
    """Client pour les endpoints Rules."""
    
    def get(self, rule_key: str) -> Rule:
        """Récupère les détails d'une règle."""
        response = self._get('/api/rules/show', {'key': rule_key})
        return Rule.from_api_response(response['rule'])
    
    def search(self, languages: Optional[List[str]] = None,
               types: Optional[List[str]] = None,
               tags: Optional[List[str]] = None,
               q: Optional[str] = None,
               page: int = 1,
               page_size: Optional[int] = None) -> Dict[str, Any]:
        """Recherche des règles."""
        params = {
            'p': page,
            'ps': page_size or self.config.page_size
        }
        
        if languages:
            params['languages'] = ','.join(languages)
        if types:
            params['types'] = ','.join(types)
        if tags:
            params['tags'] = ','.join(tags)
        if q:
            params['q'] = q
        
        response = self._get('/api/rules/search', params)
        
        # Convertir en objets Rule
        if 'rules' in response:
            response['rules'] = [Rule.from_api_response(rule) for rule in response['rules']]
        
        return response





