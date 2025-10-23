"""Classes de base pour les commandes SonarQube MCP."""

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..api import SonarQubeAPI, SonarQubeAPIError
from ..config import SonarQubeConfig


logger = logging.getLogger(__name__)

# Constantes pour les messages d'erreur
ERROR_NO_PROJECT = "Aucun projet configuré. Définissez SONARQUBE_PROJECT_KEY dans votre environnement (~/.zshrc)."
ERROR_NO_USER = "Aucun utilisateur configuré. Définissez SONARQUBE_USER dans votre environnement (~/.zshrc)."


@dataclass
class CommandResult:
    """Résultat d'une commande avec métadonnées."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        """Convertit le résultat en JSON."""
        result = {
            'success': self.success,
            'data': self.data
        }
        if self.error:
            result['error'] = self.error
        if self.metadata:
            result['metadata'] = self.metadata
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        result = {
            'success': self.success,
            'data': self.data
        }
        if self.error:
            result['error'] = self.error
        if self.metadata:
            result['metadata'] = self.metadata
        return result


class BaseCommands:
    """Classe de base pour tous les groupes de commandes."""
    
    def __init__(self, api: SonarQubeAPI, config: SonarQubeConfig):
        """
        Initialise le groupe de commandes.
        
        Args:
            api: Instance de l'API SonarQube
            config: Configuration SonarQube
        """
        self.api = api
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _success(self, data: Any, metadata: Optional[Dict] = None) -> CommandResult:
        """Crée un résultat de succès."""
        return CommandResult(success=True, data=data, metadata=metadata)
    
    def _error(self, error: str) -> CommandResult:
        """Crée un résultat d'erreur."""
        return CommandResult(success=False, data=None, error=error)
    
    def _handle_api_error(self, e: Exception, context: str = "") -> CommandResult:
        """Gère une erreur d'API."""
        error_msg = f"{context}: {str(e)}" if context else str(e)
        self.logger.error(error_msg)
        return self._error(error_msg)
    
    def _get_default_project_key(self) -> str:
        """
        Récupère la clé du projet par défaut.
        
        Returns:
            Clé du projet configuré
        
        Raises:
            ValueError: Si aucun projet n'est configuré
        """
        if not self.config.default_project:
            raise ValueError(ERROR_NO_PROJECT)
        return self.config.default_project.key

