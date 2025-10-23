"""Registre et schémas des outils MCP."""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MCPToolsRegistry:
    """Registre des outils MCP avec descriptions externalisées."""
    
    def __init__(self, descriptions_file: str = None):
        """
        Initialise le registre des outils.
        
        Args:
            descriptions_file: Chemin vers le fichier YAML de descriptions.
                              Par défaut: tools_descriptions.yaml dans le même dossier.
        """
        if descriptions_file is None:
            descriptions_file = Path(__file__).parent / 'tools_descriptions.yaml'
        
        try:
            with open(descriptions_file, 'r', encoding='utf-8') as f:
                self.descriptions = yaml.safe_load(f)
            logger.info(f"Loaded {len(self.descriptions)} tool descriptions from {descriptions_file}")
        except Exception as e:
            logger.error(f"Failed to load tool descriptions: {e}")
            raise
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        Récupère le schéma MCP complet d'un outil.
        
        Args:
            tool_name: Nom de l'outil (ex: 'sonarqube_issues')
        
        Returns:
            Schéma MCP de l'outil
        
        Raises:
            ValueError: Si l'outil n'est pas trouvé
        """
        desc = self.descriptions.get(tool_name)
        if not desc:
            raise ValueError(f"Tool {tool_name} not found in registry")
        
        # Construire le schéma inputSchema
        properties = {}
        required = []
        
        for param_name, param_spec in desc.get('parameters', {}).items():
            prop = {
                'type': param_spec['type'],
                'description': param_spec['description']
            }
            
            # Ajouter enum si présent
            if 'enum' in param_spec:
                prop['enum'] = param_spec['enum']
            
            # Ajouter items si type array
            if 'items' in param_spec:
                prop['items'] = param_spec['items']
            
            properties[param_name] = prop
            
            # Marquer comme required si nécessaire
            if param_spec.get('required', False):
                required.append(param_name)
        
        return {
            'name': desc['name'],
            'description': desc['description'],
            'inputSchema': {
                'type': 'object',
                'properties': properties,
                'required': required,
                'additionalProperties': False
            }
        }
    
    def list_all_tools(self) -> List[Dict[str, Any]]:
        """
        Liste tous les outils disponibles avec leurs schémas MCP.
        
        Returns:
            Liste des schémas MCP de tous les outils
        """
        return [self.get_tool_schema(name) for name in self.descriptions.keys()]
    
    def get_tool_names(self) -> List[str]:
        """
        Récupère la liste des noms d'outils disponibles.
        
        Returns:
            Liste des noms d'outils
        """
        return list(self.descriptions.keys())
    
    def tool_exists(self, tool_name: str) -> bool:
        """
        Vérifie si un outil existe dans le registre.
        
        Args:
            tool_name: Nom de l'outil à vérifier
        
        Returns:
            True si l'outil existe, False sinon
        """
        return tool_name in self.descriptions



