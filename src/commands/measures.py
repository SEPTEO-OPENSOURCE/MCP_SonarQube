"""Commandes liées aux métriques et mesures SonarQube."""

from typing import List
from .base import BaseCommands, CommandResult
from ..api import SonarQubeAPIError


class MeasuresCommands(BaseCommands):
    """Commandes pour récupérer les métriques."""
    
    def get_measures(self, args: List[str]) -> CommandResult:
        """
        Récupère les métriques d'un projet.
        
        Usage: measures <project_key> [metric1,metric2,...]
        """
        if not args:
            return self._error("Usage: measures <project_key> [metric1,metric2,...]")
        
        try:
            project_key = args[0]
            metrics = args[1].split(',') if len(args) > 1 else None
            
            component = self.api.get_component_measures(project_key, metrics)
            
            return self._success(
                data={
                    'component': {
                        'key': component.key,
                        'name': component.name,
                        'qualifier': component.qualifier,
                        'measures': [
                            {'metric': m.metric, 'value': m.value, 'best_value': m.best_value}
                            for m in component.measures
                        ]
                    }
                }
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, f"Erreur lors de la récupération des métriques de {args[0]}")
    
    def get_metrics_list(self, args: List[str]) -> CommandResult:  # noqa: ARG002
        """
        Liste toutes les métriques disponibles.
        
        Usage: metrics-list
        """
        try:
            result = self.api.measures.get_metrics_list()
            return self._success(data=result)
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, "Erreur lors de la récupération de la liste des métriques")
    
    def get_languages(self, args: List[str]) -> CommandResult:  # noqa: ARG002
        """
        Récupère la liste des langages supportés.
        
        Usage: languages
        """
        try:
            result = self.api.measures.get_languages()
            return self._success(data=result)
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, "Erreur lors de la récupération de la liste des langages")

