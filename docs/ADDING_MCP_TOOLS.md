# Guide d'Ajout d'Outils MCP - SonarQube MCP v4.0.0

Ce guide vous explique pas à pas comment ajouter un nouvel outil MCP au projet SonarQube MCP.

## 📋 Table des matières

1. [Introduction](#introduction)
2. [Prérequis](#prérequis)
3. [Architecture des Outils](#architecture-des-outils)
4. [Guide Pas à Pas](#guide-pas-à-pas)
5. [Checklist Complète](#checklist-complète)
6. [Exemple Complet](#exemple-complet)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

### Qu'est-ce qu'un outil MCP ?

Un outil MCP (Model Context Provider) est une fonctionnalité exposée via le protocole MCP qui permet à un assistant IA (comme Cursor) d'interagir avec SonarQube.

**Flux d'un outil MCP** :
```
Cursor IDE → MCP Server → CommandHandler → Commands → API → SonarQube
                                                               ↓
Cursor IDE ← MCP Server ← CommandResult ← Commands ← API ← SonarQube
```

### Quand créer un nouvel outil ?

Créez un nouvel outil MCP quand :
- ✅ Une API SonarQube existe pour la fonctionnalité
- ✅ La fonctionnalité apporte une valeur à l'assistant IA
- ✅ Vous avez les permissions nécessaires (lecture/écriture)
- ❌ N'utilisez pas d'alias sauf si vraiment nécessaire

---

## Prérequis

### Connaissances requises

- Python 3.8+ (dataclasses, type hints)
- Programmation orientée objet
- API REST et JSON
- Tests unitaires avec pytest
- Format YAML

### Outils nécessaires

- Environnement de développement Python
- Accès à un serveur SonarQube
- Token d'authentification avec les droits appropriés
- IDE (VSCode, PyCharm, ou Cursor recommandé)

---

## Architecture des Outils

Le projet utilise une **architecture en couches** :

```
┌─────────────────────────────────────────┐
│   MCP Layer (Interface)                 │
│   - tools_descriptions.yaml             │
│   - server.py (mapping)                 │
├─────────────────────────────────────────┤
│   Commands Layer (Business Logic)       │
│   - commands/*.py                       │
├─────────────────────────────────────────┤
│   API Layer (Infrastructure)            │
│   - api/*.py                            │
├─────────────────────────────────────────┤
│   Models (Domain)                       │
│   - models.py                           │
└─────────────────────────────────────────┘
```

**Séparation des responsabilités** :

| Couche | Responsabilité | Fichiers |
|--------|---------------|----------|
| **MCP** | Protocole, descriptions, validation | `src/mcp/` |
| **Commands** | Logique métier, formatage résultats | `src/commands/` |
| **API** | Communication HTTP, retry, erreurs | `src/api/` |
| **Models** | Structures de données | `src/models.py` |

---

## Guide Pas à Pas

### Étape 1: Identifier le besoin

#### 1.1 Vérifier l'API SonarQube

Consultez la documentation officielle : https://docs.sonarqube.org/latest/extend/web-api/

**Exemple** : Pour ajouter un outil qui liste les analyses d'un projet
- Endpoint: `/api/project_analyses/search`
- Méthode: GET
- Paramètres: `project` (requis), `from` (opt), `to` (opt)
- Réponse: Liste d'analyses avec dates et statuts

#### 1.2 Vérifier les permissions

Testez l'endpoint avec votre token :

```bash
curl -u YOUR_TOKEN: \
  "https://your-sonarqube.com/api/project_analyses/search?project=YOUR_PROJECT"
```

Si `HTTP 200` → ✅ Accessible  
Si `HTTP 403` → ❌ Permissions insuffisantes

#### 1.3 Définir les paramètres

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `project_key` | string | Oui | Clé du projet |
| `from_date` | string | Non | Date début (ISO 8601) |
| `to_date` | string | Non | Date fin (ISO 8601) |

---

### Étape 2: Implémenter la couche API

#### 2.1 Créer/étendre le fichier API approprié

Choisissez le bon fichier dans `src/api/` :
- `issues.py` - Issues et bugs
- `measures.py` - Métriques et mesures
- `security.py` - Hotspots et vulnérabilités
- `projects.py` - Projets, composants, analyses
- `users.py` - Utilisateurs
- `rules.py` - Règles de qualité

Pour notre exemple (analyses), on utilise `projects.py`.

#### 2.2 Ajouter la méthode API

```python
# src/api/projects.py

from typing import List, Optional, Dict, Any
from .base import SonarQubeAPIBase

class ProjectsAPI(SonarQubeAPIBase):
    """Client pour les endpoints Projects."""
    
    def search_analyses(
        self, 
        project_key: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 1,
        page_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Récupère l'historique des analyses d'un projet.
        
        Args:
            project_key: Clé du projet
            from_date: Date de début (format ISO 8601)
            to_date: Date de fin (format ISO 8601)
            page: Numéro de page
            page_size: Taille de la page
        
        Returns:
            Réponse API avec liste des analyses
        
        Raises:
            SonarQubeAPIError: En cas d'erreur HTTP
        
        Example:
            >>> api = ProjectsAPI(config)
            >>> analyses = api.search_analyses('my-project')
            >>> for analysis in analyses['analyses']:
            ...     print(analysis['date'])
        """
        params = {
            'project': project_key,
            'p': page,
            'ps': page_size or self.config.page_size
        }
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        return self._get('/api/project_analyses/search', params)
```

**Points clés** :
- ✅ Hériter de `SonarQubeAPIBase`
- ✅ Utiliser `self._get()`, `self._post()`, `self._put()`, `self._delete()`
- ✅ Type hints complets
- ✅ Docstring Google style
- ✅ Laisser la gestion d'erreur à la classe de base

---

### Étape 3: Implémenter la commande

#### 3.1 Ajouter la méthode de commande

```python
# src/commands/projects.py

from typing import List
from .base import BaseCommands, CommandResult
from ..api import SonarQubeAPIError

class ProjectsCommands(BaseCommands):
    """Commandes pour gérer les projets."""
    
    def get_analyses_history(self, args: List[str]) -> CommandResult:
        """
        Récupère l'historique des analyses d'un projet.
        
        Usage: analyses-history <project_key> [from_date] [to_date]
        
        Args:
            args[0]: project_key (requis)
            args[1]: from_date (optionnel, format ISO 8601)
            args[2]: to_date (optionnel, format ISO 8601)
        
        Returns:
            CommandResult avec données ou erreur
        
        Example:
            >>> cmd = ProjectsCommands(api, config)
            >>> result = cmd.get_analyses_history(['my-project'])
            >>> print(result.data['analyses'])
        """
        if not args:
            return self._error(
                "Usage: analyses-history <project_key> [from_date] [to_date]"
            )
        
        try:
            project_key = args[0]
            from_date = args[1] if len(args) > 1 else None
            to_date = args[2] if len(args) > 2 else None
            
            result = self.api.projects.search_analyses(
                project_key,
                from_date=from_date,
                to_date=to_date
            )
            
            return self._success(
                data=result,
                metadata={
                    'project': project_key,
                    'total': len(result.get('analyses', [])),
                    'from_date': from_date,
                    'to_date': to_date
                }
            )
        
        except SonarQubeAPIError as e:
            return self._handle_api_error(
                e, 
                f"Erreur lors de la récupération de l'historique de {args[0]}"
            )
```

**Points clés** :
- ✅ Hériter de `BaseCommands`
- ✅ Retourner `CommandResult` (via `self._success()` ou `self._error()`)
- ✅ Utiliser `self._handle_api_error()` pour gérer erreurs API
- ✅ Inclure métadonnées utiles
- ✅ Validation basique des arguments

---

### Étape 4: Enregistrer la commande

#### 4.1 Ajouter dans CommandHandler

```python
# src/commands/__init__.py

class CommandHandler:
    """Gestionnaire principal des commandes."""
    
    def _register_commands(self) -> Dict[str, Any]:
        """Enregistre toutes les commandes disponibles."""
        return {
            # ... commandes existantes ...
            
            # Projects (ajouter à la section Projects)
            'analyses-history': self.projects.get_analyses_history,
            
            # ... autres commandes ...
        }
```

#### 4.2 Tester via CLI

```bash
# Test basique
python3 sonarqube_cli.py analyses-history YOUR_PROJECT_KEY

# Test avec dates
python3 sonarqube_cli.py analyses-history YOUR_PROJECT_KEY 2024-01-01 2024-12-31
```

---

### Étape 5: Créer l'outil MCP

#### 5.1 Ajouter la définition YAML

```yaml
# src/mcp/tools_descriptions.yaml

sonarqube_analyses_history:
  name: "sonarqube_analyses_history"
  title: "Historique Analyses"
  description: |
    📊 HISTORIQUE ANALYSES - Récupère l'historique des analyses d'un projet.
    
    ✅ Cas d'usage:
    - Suivre l'évolution de la qualité du code
    - Détecter des régressions
    - Analyser la fréquence des analyses
    - Comparer les métriques dans le temps
    
    📝 Exemples:
    - "Historique d'analyses du projet X"
    - "Analyses entre janvier et mars 2024"
    - "Dernières 10 analyses du projet"
    
    🔧 Outil autonome, aucune configuration supplémentaire requise.
  parameters:
    project_key:
      type: "string"
      description: "Clé du projet SonarQube"
      required: true
    from_date:
      type: "string"
      description: "Date de début (format ISO 8601, ex: 2024-01-01) (optionnel)"
      required: false
    to_date:
      type: "string"
      description: "Date de fin (format ISO 8601, ex: 2024-12-31) (optionnel)"
      required: false
```

**Bonnes pratiques pour les descriptions** :
- 🎯 Commencer par un émoji thématique
- ✅ Lister clairement les cas d'usage
- 📝 Donner 3-4 exemples concrets
- 🔧 Indiquer si autonome ou nécessite config
- ⚠️ Mentionner limitations si existantes

---

### Étape 6: Mapper l'outil

#### 6.1 Ajouter le mapping dans le serveur MCP

```python
# src/mcp/server.py

class MCPServer:
    """Serveur MCP implémentant le protocole."""
    
    def _handle_tools_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Appelle un outil."""
        # ... code existant ...
        
        # Mapping outil → commande
        tool_to_command = {
            # ... mappings existants ...
            'sonarqube_analyses_history': 'analyses-history',
            # ... autres mappings ...
        }
        
        # ... reste du code ...
```

#### 6.2 Implémenter la conversion d'arguments

```python
# src/mcp/server.py (dans _convert_arguments)

def _convert_arguments(self, command: str, arguments: Dict[str, Any]) -> list:
    """Convertit arguments outil en liste args commande."""
    try:
        # ... cas existants ...
        
        elif command == 'analyses-history':
            # Valider project_key
            from ..utils import validate_project_key
            project_key = validate_project_key(arguments['project_key'])
            
            args = [project_key]
            
            # Ajouter dates optionnelles
            if 'from_date' in arguments and arguments['from_date']:
                args.append(arguments['from_date'])
                
                if 'to_date' in arguments and arguments['to_date']:
                    args.append(arguments['to_date'])
            
            return args
        
        # ... autres cas ...
```

**Validation des paramètres** :

Utilisez les fonctions de `src/utils.py` :
- `validate_file_path()` - Chemins de fichiers
- `validate_project_key()` - Clés de projet
- `validate_rule_key()` - Clés de règles
- `validate_user_login()` - Logins utilisateurs

---

### Étape 7: Tests unitaires

#### 7.1 Tests API

```python
# tests/unit/test_api_projects_extended.py

import pytest
from unittest.mock import patch
from src.api.projects import ProjectsAPI
from src.config import SonarQubeConfig

@pytest.fixture
def config():
    return SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test_token"
    )

class TestProjectsAPIAnalyses:
    """Tests pour search_analyses."""
    
    def test_search_analyses_minimal(self, config):
        """Test search_analyses avec paramètres minimaux."""
        api = ProjectsAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'analyses': []}
            
            result = api.search_analyses('test-project')
            
            assert result is not None
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[0][1]
            assert params['project'] == 'test-project'
    
    def test_search_analyses_with_dates(self, config):
        """Test search_analyses avec dates."""
        api = ProjectsAPI(config)
        
        with patch.object(api, '_get') as mock_get:
            mock_get.return_value = {'analyses': []}
            
            result = api.search_analyses(
                'test-project',
                from_date='2024-01-01',
                to_date='2024-12-31'
            )
            
            assert result is not None
            call_args = mock_get.call_args
            params = call_args[0][1]
            assert params['from'] == '2024-01-01'
            assert params['to'] == '2024-12-31'
```

#### 7.2 Tests commande

```python
# tests/unit/test_commands_projects_extended.py

import pytest
from unittest.mock import Mock
from src.commands.projects import ProjectsCommands
from src.config import SonarQubeConfig
from src.api import SonarQubeAPIError

@pytest.fixture
def mock_api():
    api = Mock()
    api.projects = Mock()
    return api

@pytest.fixture
def config():
    return SonarQubeConfig(
        url="https://test.sonarqube.com",
        token="test_token"
    )

@pytest.fixture
def commands(mock_api, config):
    return ProjectsCommands(mock_api, config)

class TestAnalysesHistoryCommand:
    """Tests pour get_analyses_history."""
    
    def test_analyses_history_success(self, commands, mock_api):
        """Test analyses-history avec succès."""
        mock_api.projects.search_analyses.return_value = {
            'analyses': [
                {'date': '2024-01-01', 'key': 'A1'},
                {'date': '2024-01-02', 'key': 'A2'}
            ]
        }
        
        result = commands.get_analyses_history(['test-project'])
        
        assert result.success is True
        assert result.metadata['total'] == 2
        assert result.metadata['project'] == 'test-project'
    
    def test_analyses_history_with_dates(self, commands, mock_api):
        """Test analyses-history avec dates."""
        mock_api.projects.search_analyses.return_value = {'analyses': []}
        
        result = commands.get_analyses_history([
            'test-project',
            '2024-01-01',
            '2024-12-31'
        ])
        
        assert result.success is True
        assert result.metadata['from_date'] == '2024-01-01'
        assert result.metadata['to_date'] == '2024-12-31'
    
    def test_analyses_history_missing_args(self, commands):
        """Test analyses-history sans arguments."""
        result = commands.get_analyses_history([])
        
        assert result.success is False
        assert 'Usage' in result.error
    
    def test_analyses_history_api_error(self, commands, mock_api):
        """Test analyses-history avec erreur API."""
        mock_api.projects.search_analyses.side_effect = SonarQubeAPIError(
            status_code=404,
            message="Project not found"
        )
        
        result = commands.get_analyses_history(['unknown-project'])
        
        assert result.success is False
```

#### 7.3 Tests outil MCP

```python
# tests/integration/test_mcp_tools_extended.py

def test_sonarqube_analyses_history(mcp_server):
    """Test outil sonarqube_analyses_history."""
    request = {
        "method": "tools/call",
        "params": {
            "name": "sonarqube_analyses_history",
            "arguments": {
                "project_key": "test-project"
            }
        }
    }
    
    with patch.object(
        mcp_server.command_handler, 
        'execute'
    ) as mock_execute:
        mock_execute.return_value = Mock(
            success=True,
            data={'analyses': []},
            to_json=lambda: '{"success": true}'
        )
        
        response = mcp_server.handle_request(request)
        
        assert 'result' in response
        mock_execute.assert_called_once_with('analyses-history', ['test-project'])
```

---

### Étape 8: Vérification couverture

#### 8.1 Exécuter les tests avec couverture

```bash
# Tests unitaires seulement
pytest tests/unit/test_api_projects_extended.py --cov=src/api/projects --cov-report=term-missing

# Tests commandes
pytest tests/unit/test_commands_projects_extended.py --cov=src/commands/projects --cov-report=term-missing

# Tous les tests
pytest --cov=src --cov-report=html
```

#### 8.2 Analyser les lignes manquantes

```bash
# Ouvrir le rapport HTML
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Objectif** : >80% sur les nouveaux modules

#### 8.3 Compléter si nécessaire

Si couverture < 80%, identifiez :
- Branches conditionnelles non testées
- Cas d'erreur non couverts
- Validations non testées

---

### Étape 9: Documentation

#### 9.1 Mettre à jour README.md

```markdown
# README.md

## Commandes disponibles

### Projets

| Commande | Description | Usage |
|----------|-------------|-------|
| `analyses-history` | Historique analyses | `analyses-history <project_key> [from] [to]` |
```

#### 9.2 Ajouter dans CLI help

```python
# sonarqube_cli.py

def print_help():
    """Affiche l'aide complète."""
    help_text = """
    ...
    ┌─ Projets ────────────────────────────────────────┐
    │ analyses-history <project_key> [from] [to]      │
    │                                  - Historique   │
    └──────────────────────────────────────────────────┘
    """
```

#### 9.3 Créer un exemple

```python
# examples/analyses_history.py

"""
Exemple d'utilisation de l'outil analyses-history.

Ce script montre comment récupérer l'historique des analyses
d'un projet SonarQube.
"""

from src.config import SonarQubeConfig
from src.api import SonarQubeAPI
from src.commands import CommandHandler

# Configuration
config = SonarQubeConfig.from_env()
api = SonarQubeAPI(config)
handler = CommandHandler(api, config)

# Récupérer historique
result = handler.execute('analyses-history', ['my-project'])

if result.success:
    analyses = result.data['analyses']
    print(f"Trouvé {len(analyses)} analyses")
    
    for analysis in analyses[:5]:  # 5 plus récentes
        print(f"- {analysis['date']}: {analysis.get('events', [])}")
else:
    print(f"Erreur: {result.error}")
```

---

### Étape 10: Test end-to-end

#### 10.1 Test CLI

```bash
# Test basique
python3 sonarqube_cli.py analyses-history YOUR_PROJECT_KEY

# Test avec verbosité
python3 sonarqube_cli.py --verbose analyses-history YOUR_PROJECT_KEY

# Test avec dates
python3 sonarqube_cli.py analyses-history YOUR_PROJECT_KEY 2024-01-01 2024-12-31
```

**Vérifiez** :
- ✅ Pas d'erreur Python
- ✅ JSON valide en sortie
- ✅ Données cohérentes
- ✅ Gestion erreurs (projet inexistant, etc.)

#### 10.2 Test MCP dans Cursor

1. Redémarrer Cursor pour recharger la config MCP
2. Ouvrir un fichier du projet
3. Demander à l'assistant :

```
"Montre-moi l'historique des analyses du projet X"
"Quelles analyses ont été faites en janvier 2024 ?"
"Compare les 5 dernières analyses"
```

**Vérifiez** :
- ✅ L'outil apparaît dans Cursor Settings > MCP
- ✅ L'assistant utilise l'outil
- ✅ Les résultats sont corrects
- ✅ Pas de timeout ou erreur

#### 10.3 Vérifier les logs

```bash
# Logs du serveur MCP
tail -f ~/.sonarqube_mcp/logs/sonarqube_mcp_$(date +%Y-%m-%d).log

# Chercher erreurs
grep ERROR ~/.sonarqube_mcp/logs/*.log
```

---

## Checklist Complète

### ☐ Phase Conception
- [ ] Endpoint API SonarQube identifié
- [ ] Documentation API consultée
- [ ] Permissions token vérifiées (curl test)
- [ ] Paramètres d'entrée/sortie définis
- [ ] Cas d'usage documentés

### ☐ Phase Implémentation API
- [ ] Méthode ajoutée dans `src/api/*.py`
- [ ] Type hints complets
- [ ] Docstring Google style
- [ ] Utilise `self._get/post/put/delete()`
- [ ] Gestion d'erreur déléguée à base

### ☐ Phase Implémentation Commande
- [ ] Méthode ajoutée dans `src/commands/*.py`
- [ ] Hérite de `BaseCommands`
- [ ] Retourne `CommandResult`
- [ ] Validation arguments
- [ ] Métadonnées ajoutées
- [ ] Gestion erreur avec `_handle_api_error()`

### ☐ Phase Enregistrement
- [ ] Commande dans `CommandHandler._register_commands()`
- [ ] Test CLI réussi
- [ ] Aide CLI mise à jour

### ☐ Phase MCP
- [ ] Définition dans `tools_descriptions.yaml`
- [ ] Description avec émojis et cas d'usage
- [ ] Paramètres bien typés
- [ ] Mapping dans `server.py` (`tool_to_command`)
- [ ] Conversion arguments dans `_convert_arguments()`
- [ ] Validation paramètres

### ☐ Phase Tests
- [ ] Tests API (succès, erreur, paramètres)
- [ ] Tests commande (succès, erreur, validation)
- [ ] Tests outil MCP
- [ ] Couverture >80% sur nouveaux modules
- [ ] Tous les tests passent

### ☐ Phase Documentation
- [ ] README.md mis à jour
- [ ] CLI help mis à jour
- [ ] Exemple créé dans `examples/`
- [ ] CHANGELOG.md mis à jour

### ☐ Phase Validation
- [ ] Test CLI fonctionnel
- [ ] Test MCP dans Cursor
- [ ] Pas d'erreur dans logs
- [ ] Gestion erreurs validée

---

## Exemple Complet

Voir le commit `feat: add analyses history tool` pour un exemple complet d'implémentation.

**Fichiers modifiés** :
- `src/api/projects.py` - Méthode `search_analyses()`
- `src/commands/projects.py` - Méthode `get_analyses_history()`
- `src/commands/__init__.py` - Enregistrement commande
- `src/mcp/tools_descriptions.yaml` - Définition outil
- `src/mcp/server.py` - Mapping et conversion
- `tests/unit/test_api_projects_extended.py` - Tests API
- `tests/unit/test_commands_projects_extended.py` - Tests commande
- `tests/integration/test_mcp_tools_extended.py` - Tests MCP
- `sonarqube_cli.py` - Aide CLI
- `README.md` - Documentation
- `examples/analyses_history.py` - Exemple

---

## Troubleshooting

### Problème : L'outil n'apparaît pas dans Cursor

**Causes possibles** :
1. Syntaxe YAML invalide dans `tools_descriptions.yaml`
2. Serveur MCP non redémarré
3. Erreur dans `tools_registry.py`

**Solutions** :
```bash
# Valider YAML
python3 -c "import yaml; yaml.safe_load(open('src/mcp/tools_descriptions.yaml'))"

# Redémarrer Cursor complètement
# Vérifier logs MCP
tail -f ~/.sonarqube_mcp/logs/*.log
```

### Problème : Erreur "Tool not found"

**Cause** : Mapping manquant dans `server.py`

**Solution** :
```python
# Vérifier que le mapping existe
tool_to_command = {
    'sonarqube_your_tool': 'your-command',  # ← Doit exister
}
```

### Problème : Erreur de validation paramètres

**Cause** : `additionalProperties: false` empêche paramètres non déclarés

**Solution** :
- Déclarer tous les paramètres dans `tools_descriptions.yaml`
- Ou utiliser validation personnalisée

### Problème : Couverture < 80%

**Causes** :
- Branches conditionnelles non testées
- Cas d'erreur manquants

**Solution** :
```bash
# Identifier lignes manquantes
pytest --cov=src/your_module --cov-report=term-missing

# Ajouter tests pour branches et erreurs
```

### Problème : Tests MCP timeout

**Cause** : Serveur MCP bloque (signal.alarm)

**Solution** :
- Vérifier que `signal.alarm(0)` est appelé
- Utiliser mocks pour éviter appels réels

---

## Patterns de Validation Courants

### Validation de clé de projet

```python
from ..utils import validate_project_key, ValidationError

try:
    project_key = validate_project_key(arguments['project_key'])
except ValidationError as e:
    raise SonarQubeAPIError(status_code=400, message=str(e))
```

### Validation de chemin de fichier

```python
from ..utils import validate_file_path, ValidationError

try:
    file_path = validate_file_path(arguments['file_path'])
except ValidationError as e:
    raise SonarQubeAPIError(status_code=400, message=str(e))
```

### Validation de clé de règle

```python
from ..utils import validate_rule_key, ValidationError

try:
    rule_key = validate_rule_key(arguments['rule_key'])
except ValidationError as e:
    raise SonarQubeAPIError(status_code=400, message=str(e))
```

---

## Ressources

- [Documentation API SonarQube](https://docs.sonarqube.org/latest/extend/web-api/)
- [Protocole MCP](https://modelcontextprotocol.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

**Besoin d'aide ?** Consultez les exemples existants dans le code ou créez une issue sur le repository.

