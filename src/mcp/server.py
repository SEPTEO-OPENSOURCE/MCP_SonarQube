"""Serveur MCP SonarQube - Protocole pur."""

import sys
import json
import logging
import threading
from typing import Dict, Any, Optional, List

from ..config import SonarQubeConfig
from ..api import SonarQubeAPI, SonarQubeAPIError
from ..commands import CommandHandler
from ..utils import validate_file_path, validate_project_key, validate_rule_key, validate_user_login, ValidationError
from .tools_registry import MCPToolsRegistry

logger = logging.getLogger(__name__)


class MCPServer:
    """Serveur MCP implémentant le protocole."""
    
    def __init__(self, config: SonarQubeConfig):
        """
        Initialise le serveur MCP.
        
        Args:
            config: Configuration SonarQube
        """
        self.config = config
        self.api = SonarQubeAPI(config)
        self.command_handler = CommandHandler(self.api, config)
        self.tools_registry = MCPToolsRegistry()
        
        logger.info("Serveur MCP SonarQube initialisé")
        logger.info(f"URL: {config.url}")
        logger.info(f"{len(self.tools_registry.get_tool_names())} outils chargés")
    
    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Traite une requête MCP.
        
        Args:
            request: Requête MCP
        
        Returns:
            Réponse MCP ou None pour les notifications
        """
        method = request.get('method')
        
        handlers = {
            'initialize': self._handle_initialize,
            'initialized': lambda r: {'result': {}},
            'notifications/initialized': lambda r: None,
            'tools/list': self._handle_tools_list,
            'tools/call': self._handle_tools_call,
            'resources/list': self._handle_resources_list,
            'resources/read': self._handle_resources_read,
            'ping': lambda r: {'result': {'status': 'pong'}}
        }
        
        handler = handlers.get(method)
        if handler:
            try:
                return handler(request)
            except Exception as e:
                logger.error(f"Error handling {method}: {e}", exc_info=True)
                return self._error_response(-32603, str(e))
        else:
            return self._error_response(-32601, f"Méthode inconnue: {method}")
    
    def _handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Traite requête initialize."""
        return {
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': {
                    'tools': {},
                    'resources': {
                        'subscribe': True,
                        'listChanged': True
                    }
                },
                'serverInfo': {
                    'name': 'sonarqube-mcp',
                    'version': '4.0.0'
                }
            }
        }
    
    def _handle_tools_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Liste les outils disponibles."""
        tools = self.tools_registry.list_all_tools()
        return {'result': {'tools': tools}}
    
    def _handle_tools_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appelle un outil.
        
        Args:
            request: Requête MCP avec params.name et params.arguments
        
        Returns:
            Résultat de l'outil ou erreur
        """
        params = request.get('params', {})
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        # Variables pour gérer le timeout de manière cross-platform
        result_container = [None]
        exception_container = [None]
        
        def execute_tool():
            """Exécute l'outil dans un thread séparé."""
            try:
                # Tool special: ping
                if tool_name == 'sonarqube_ping':
                    result_container[0] = {
                        'result': {
                            'content': [{
                                'type': 'text',
                                'text': json.dumps({
                                    'success': True,
                                    'message': 'pong',
                                    'config': {
                                        'url': self.config.url,
                                        'project_key': self.config.default_project.key if self.config.default_project else None,
                                        'user': self.config.default_project.assignee if self.config.default_project else None
                                    }
                                }, indent=2)
                            }]
                        }
                    }
                    return
                
                # Mapping outil -> commande
                tool_to_command = {
                    'sonarqube_issues': 'issues',
                    'sonarqube_search_issues': 'search-issues',
                    'sonarqube_measures': 'measures',
                    'sonarqube_hotspots': 'hotspots',
                    'sonarqube_rule': 'rule',
                    'sonarqube_users': 'users',
                    'sonarqube_quality_gate': 'quality-gate',
                    'sonarqube_analyses_history': 'analyses',
                    'sonarqube_duplications': 'duplications',
                    'sonarqube_source_lines': 'source-lines',
                    'sonarqube_metrics_list': 'metrics-list',
                    'sonarqube_languages': 'languages',
                    'sonarqube_projects': 'projects'
                }
                
                command = tool_to_command.get(tool_name)
                if not command:
                    result_container[0] = self._error_response(-32602, f"Outil inconnu: {tool_name}")
                    return
                
                # Convertir arguments + exécuter
                args = self._convert_arguments(command, arguments)
                result = self.command_handler.execute(command, args)
                
                if result.success:
                    result_container[0] = {
                        'result': {
                            'content': [{'type': 'text', 'text': result.to_json()}]
                        }
                    }
                else:
                    result_container[0] = self._error_response(-32603, result.error)
            
            except SonarQubeAPIError as e:
                exception_container[0] = ('api', e)
            except Exception as e:
                exception_container[0] = ('general', e)
        
        # Exécuter avec timeout de 60 secondes
        thread = threading.Thread(target=execute_tool)
        thread.daemon = True
        thread.start()
        thread.join(timeout=60)
        
        # Vérifier si le timeout s'est produit
        if thread.is_alive():
            logger.error(f"Timeout lors de l'appel de {tool_name}: dépassé 60 secondes")
            return self._error_response(-32603, "Timeout: L'appel de l'outil a dépassé le timeout de 60 secondes")
        
        # Vérifier si une exception s'est produite
        if exception_container[0]:
            exc_type, exc = exception_container[0]
            if exc_type == 'api':
                logger.error(f"Erreur API SonarQube: {exc}")
                return self._error_response(-32603, f'Erreur SonarQube: {exc.message}')
            else:
                logger.error(f"Erreur inattendue: {exc}", exc_info=True)
                return self._error_response(-32603, f'Erreur interne: {str(exc)}')
        
        # Retourner le résultat
        return result_container[0] if result_container[0] else self._error_response(-32603, "Erreur interne: aucun résultat")
    
    def _convert_arguments(self, command: str, arguments: Dict[str, Any]) -> list:  # noqa: C901
        """
        Convertit arguments outil en liste args commande.
        
        Args:
            command: Nom de la commande
            arguments: Arguments de l'outil
        
        Returns:
            Liste d'arguments pour la commande
        
        Raises:
            SonarQubeAPIError: Si la validation échoue
        """
        try:
            # Table de dispatch pour réduire la complexité
            command_converters = {
                'issues': self._convert_issues_args,
                'search-issues': self._convert_search_issues_args,
                'measures': self._convert_measures_args,
                'hotspots': self._convert_hotspots_args,
                'rule': self._convert_rule_args,
                'users': self._convert_users_args,
                'quality-gate': self._convert_quality_gate_args,
                'analyses': self._convert_analyses_args,
                'duplications': self._convert_duplications_args,
                'source-lines': self._convert_source_lines_args,
                'metrics-list': self._convert_metrics_list_args,
                'languages': self._convert_languages_args,
                'projects': self._convert_projects_args
            }
            
            converter = command_converters.get(command)
            if converter:
                return converter(arguments)
            else:
                raise SonarQubeAPIError(f"Commande inconnue: {command}")
        
        except ValidationError as e:
            logger.warning(f"Validation error for command '{command}': {e}")
            raise SonarQubeAPIError(400, str(e))
    
    def _convert_issues_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande issues."""
        # Toujours utiliser les variables d'environnement
        if not self.config.default_project:
            return []
        
        project_key = self.config.default_project.key
        assignee = self.config.default_project.assignee
        
        if not project_key or not assignee:
            return []
        
        args = [project_key, assignee]
        
        # Si file_path spécifié, le valider et l'ajouter
        if arguments.get('file_path'):
            validated_path = validate_file_path(arguments['file_path'])
            args.append(validated_path)
        
        return args
    
    def _convert_search_issues_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande search-issues."""
        # Recherche d'issues avec project_key requis, assignee et statuses optionnels
        project_key = validate_project_key(arguments['project_key'])
        args = [project_key]
        
        # Si assignee est spécifié (même vide), l'ajouter
        if 'assignee' in arguments:
            assignee = arguments['assignee']
            if assignee:  # Si non vide, valider
                assignee = validate_user_login(assignee)
            args.append(assignee)
        else:
            args.append('')
        
        # Si statuses est spécifié, l'ajouter (supporte string ou array)
        if 'statuses' in arguments:
            statuses = arguments['statuses']
            if statuses:
                # Si c'est une liste, joindre avec des virgules
                if isinstance(statuses, list):
                    status_str = ','.join(statuses)
                else:
                    status_str = statuses
                # La validation sera faite par la commande elle-même
                args.append(status_str)
        
        return args
    
    def _convert_measures_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande measures."""
        project_key = validate_project_key(arguments['project_key'])
        args = [project_key]
        if 'metrics' in arguments:
            args.append(','.join(arguments['metrics']))
        return args
    
    def _convert_hotspots_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande hotspots."""
        project_key = validate_project_key(arguments['project_key'])
        args = [project_key]
        if 'status' in arguments:
            args.append(arguments['status'])
        return args
    
    def _convert_rule_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande rule."""
        rule_key = validate_rule_key(arguments['rule_key'])
        return [rule_key]
    
    def _convert_users_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande users."""
        query = validate_user_login(arguments['query'])
        return [query]
    
    def _convert_quality_gate_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande quality-gate."""
        project_key = validate_project_key(arguments['project_key'])
        return [project_key]
    
    def _convert_analyses_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande analyses."""
        # project_key, from_date, to_date tous optionnels
        args = []
        if 'project_key' in arguments:
            args.append(validate_project_key(arguments['project_key']))
        if 'from_date' in arguments:
            args.append(arguments['from_date'])
        if 'to_date' in arguments:
            args.append(arguments['to_date'])
        return args
    
    def _convert_duplications_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande duplications."""
        # file_key requis, validation basique
        file_key = arguments.get('file_key', '')
        if not file_key:
            raise ValidationError("file_key est requis")
        validate_file_path(file_key)
        return [file_key]
    
    def _convert_source_lines_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande source-lines."""
        # file_key requis, from_line et to_line optionnels
        file_key = arguments.get('file_key', '')
        if not file_key:
            raise ValidationError("file_key est requis")
        validate_file_path(file_key)
        args = [file_key]
        if 'from_line' in arguments:
            args.append(str(arguments['from_line']))
        if 'to_line' in arguments:
            args.append(str(arguments['to_line']))
        return args
    
    def _convert_metrics_list_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande metrics-list."""
        # Aucun paramètre
        return []
    
    def _convert_languages_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande languages."""
        # Aucun paramètre
        return []
    
    def _convert_projects_args(self, arguments: Dict[str, Any]) -> List[str]:
        """Convertit les arguments pour la commande projects."""
        # search optionnel
        args = []
        if 'search' in arguments and arguments['search']:
            args.append(arguments['search'])
        return args
    
    def _handle_resources_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Liste les ressources disponibles."""
        resources = []
        
        # Ajouter le projet par défaut comme ressource si configuré
        if self.config.default_project:
            resources.append({
                'uri': f'sonarqube://project/{self.config.default_project.key}',
                'name': self.config.default_project.name or self.config.default_project.key,
                'description': f'Projet SonarQube par défaut: {self.config.default_project.key}',
                'mimeType': 'application/json'
            })
        
        return {'result': {'resources': resources}}
    
    def _handle_resources_read(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Lit une ressource."""
        params = request.get('params', {})
        uri = params.get('uri', '')
        
        if uri.startswith('sonarqube://project/'):
            project_key = uri.replace('sonarqube://project/', '')
            
            try:
                # Récupérer les informations du projet
                project = self.api.projects.get_project(project_key)
                if not project:
                    return self._error_response(-32602, f'Projet non trouvé: {project_key}')
                
                # Récupérer les métriques
                component = self.api.measures.get_component_measures(project_key)
                
                data = {
                    'project': {
                        'key': project.key,
                        'name': project.name,
                        'qualifier': project.qualifier,
                        'visibility': project.visibility,
                        'last_analysis_date': str(project.last_analysis_date) if project.last_analysis_date else None
                    },
                    'measures': [
                        {'metric': m.metric, 'value': m.value}
                        for m in component.measures
                    ]
                }
                
                return {
                    'result': {
                        'contents': [{
                            'uri': uri,
                            'mimeType': 'application/json',
                            'text': json.dumps(data, indent=2, ensure_ascii=True)
                        }]
                    }
                }
            except SonarQubeAPIError as e:
                return self._error_response(-32603, f'Erreur SonarQube: {e.message}')
        
        return self._error_response(-32602, f'URI de ressource inconnue: {uri}')
    
    def _error_response(self, code: int, message: str) -> Dict[str, Any]:
        """Crée une réponse d'erreur MCP."""
        return {'error': {'code': code, 'message': message}}
    
    def run(self):
        """Lance le serveur en mode stdio."""
        logger.info("Démarrage serveur MCP en mode stdio")
        
        try:
            for line in sys.stdin:
                if not line.strip():
                    continue
                
                try:
                    request = json.loads(line)
                    logger.debug(f"Requête reçue: {request.get('method')}")
                    
                    response = self.handle_request(request)
                    
                    if response is None:
                        logger.debug("Notification traitée, aucune réponse")
                        continue
                    
                    # Ajouter l'ID de la requête si présent
                    if 'id' in request:
                        response['id'] = request['id']
                    response['jsonrpc'] = '2.0'
                    
                    print(json.dumps(response, ensure_ascii=True))
                    sys.stdout.flush()
                    logger.debug(f"Réponse envoyée pour {request.get('method')}")
                
                except json.JSONDecodeError as e:
                    logger.error(f"JSON invalide: {e}")
                    error_response = {
                        'jsonrpc': '2.0',
                        'error': {'code': -32700, 'message': 'Parse error'}
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
        
        except KeyboardInterrupt:
            logger.info("Arrêt serveur MCP (Ctrl+C)")
        except Exception as e:
            logger.error(f"Erreur fatale: {e}", exc_info=True)
            raise

