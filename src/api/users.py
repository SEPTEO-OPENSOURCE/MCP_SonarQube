"""API SonarQube - Endpoints Users."""

from typing import List, Optional
from .base import SonarQubeAPIBase
from ..models import User


class UsersAPI(SonarQubeAPIBase):
    """Client pour les endpoints Users."""
    
    def search(self, query: str, page: int = 1, page_size: Optional[int] = None) -> List[User]:
        """
        Recherche des utilisateurs.
        
        Args:
            query: Terme de recherche (nom, email, login)
            page: Numéro de page
            page_size: Taille de page
        
        Returns:
            Liste des utilisateurs
        """
        params = {
            'q': query,
            'p': page,
            'ps': page_size or self.config.page_size
        }
        
        response = self._get('/api/users/search', params)
        return [User.from_api_response(user) for user in response.get('users', [])]





