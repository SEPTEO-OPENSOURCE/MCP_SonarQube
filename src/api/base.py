"""Classe de base pour l'API SonarQube."""

import requests
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config import SonarQubeConfig


logger = logging.getLogger(__name__)


class SonarQubeAPIError(Exception):
    """Exception levée lors d'erreurs d'API SonarQube."""
    
    def __init__(self, status_code: int, message: str, response_text: str = ""):
        self.status_code = status_code
        self.message = message
        self.response_text = response_text
        super().__init__(f"HTTP {status_code}: {message}")


class SonarQubeAPIBase:
    """Classe de base pour tous les clients API."""
    
    def __init__(self, config: SonarQubeConfig):
        """
        Initialise le client API.
        
        Args:
            config: Configuration SonarQube
        """
        self.config = config
        self.session = self._create_session()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _create_session(self) -> requests.Session:
        """
        Crée une session HTTP avec retry logic et authentification.
        
        Returns:
            Session requests configurée
        """
        session = requests.Session()
        
        # Configuration de l'authentification (token comme username, password vide)
        session.auth = (self.config.token, '')
        
        # Configuration du retry avec backoff exponentiel
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                 json: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Effectue une requête HTTP avec gestion d'erreur centralisée.
        
        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint de l'API (ex: /api/issues/search)
            params: Paramètres de requête (optionnel)
            json: Corps de la requête JSON (optionnel)
        
        Returns:
            Réponse JSON désérialisée
        
        Raises:
            SonarQubeAPIError: En cas d'erreur HTTP
        """
        url = f"{self.config.url}{endpoint}"
        
        try:
            self.logger.debug(f"{method} {url} - params: {params}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            raise SonarQubeAPIError(
                status_code=e.response.status_code,
                message=str(e),
                response_text=e.response.text
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise SonarQubeAPIError(
                status_code=0,
                message=f"Erreur de connexion: {str(e)}"
            )
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectue une requête GET."""
        return self._request("GET", endpoint, params=params)
    
    def _post(self, endpoint: str, params: Optional[Dict] = None, 
              json: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectue une requête POST."""
        return self._request("POST", endpoint, params=params, json=json)
    
    def _put(self, endpoint: str, params: Optional[Dict] = None,
             json: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectue une requête PUT."""
        return self._request("PUT", endpoint, params=params, json=json)
    
    def _delete(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectue une requête DELETE."""
        return self._request("DELETE", endpoint, params=params)





