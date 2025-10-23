"""Commandes liées à la sécurité SonarQube."""

from typing import List
from .base import BaseCommands, CommandResult
from ..models import HotspotStatus
from ..api import SonarQubeAPIError


class SecurityCommands(BaseCommands):
    """Commandes pour gérer les hotspots de sécurité."""
    
    def get_hotspots(self, args: List[str]) -> CommandResult:
        """
        Récupère les hotspots de sécurité.
        
        Usage: hotspots <project_key> [status]
        Status: TO_REVIEW (default), REVIEWED, SAFE
        """
        if not args:
            return self._error("Usage: hotspots <project_key> [status]")
        
        try:
            project_key = args[0]
            status = HotspotStatus(args[1]) if len(args) > 1 else HotspotStatus.TO_REVIEW
            
            result = self.api.search_hotspots(project_key, status=status)
            
            return self._success(
                data=result,
                metadata={
                    'total': len(result.get('hotspots', [])),
                    'status': status.value
                }
            )
        
        except (ValueError, SonarQubeAPIError) as e:
            return self._handle_api_error(e, "Erreur lors de la récupération des hotspots")





