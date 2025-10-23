"""Commandes liées aux utilisateurs et règles SonarQube."""

from typing import List
from .base import BaseCommands, CommandResult
from ..api import SonarQubeAPIError


class UsersCommands(BaseCommands):
    """Commandes pour gérer les utilisateurs et les règles."""
    
    def search_users(self, args: List[str]) -> CommandResult:
        """
        Recherche des utilisateurs.
        
        Usage: users <search_term>
        """
        if not args:
            return self._error("Usage: users <search_term>")
        
        try:
            query = args[0]
            users = self.api.search_users(query)
            
            return self._success(
                data={
                    'users': [
                        {
                            'login': u.login,
                            'name': u.name,
                            'email': u.email,
                            'active': u.active
                        }
                        for u in users
                    ]
                },
                metadata={'total': len(users)}
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, f"Erreur lors de la recherche d'utilisateurs '{args[0]}'")
    
    def get_rule(self, args: List[str]) -> CommandResult:
        """
        Récupère les détails d'une règle.
        
        Usage: rule <rule_key>
        """
        if not args:
            return self._error("Usage: rule <rule_key>")
        
        try:
            rule_key = args[0]
            rule = self.api.get_rule(rule_key)
            
            return self._success(
                data={
                    'key': rule.key,
                    'name': rule.name,
                    'lang': rule.lang,
                    'type': rule.type,
                    'severity': rule.severity.value,
                    'html_desc': rule.html_desc,
                    'markdown_desc': rule.markdown_desc,
                    'tags': rule.tags
                }
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, f"Erreur lors de la récupération de la règle {args[0]}")
    
    def search_rules(self, args: List[str]) -> CommandResult:
        """
        Recherche des règles.
        
        Usage: rules [search_term]
        """
        try:
            query = args[0] if args else None
            result = self.api.search_rules(q=query)
            
            return self._success(
                data=result,
                metadata={'total': result.get('total', 0)}
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(e, "Erreur lors de la recherche de règles")





