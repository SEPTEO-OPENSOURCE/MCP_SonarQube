# Guide de Contribution

Merci de votre intérêt pour contribuer au projet SonarQube MCP !

## 🚀 Démarrage rapide

1. Fork le projet sur GitHub
2. Créer une branche: `git checkout -b feature/ma-feature`
3. Faire vos modifications
4. Lancer les tests: `make test`
5. Commit: `git commit -m "feat: ma fonctionnalité"`
6. Push: `git push origin feature/ma-feature`
7. Ouvrir une Pull Request

## 📁 Structure du Code

```
src/
├── api/         # Client API SonarQube (7 modules spécialisés)
├── commands/    # Commandes utilisateur (6 modules par domaine)
├── mcp/         # Serveur MCP (protocole + descriptions YAML)
├── config.py    # Configuration centralisée
├── models.py    # Modèles de données (dataclasses)
└── utils.py     # Utilitaires de validation & sécurité
```

## ✅ Standards de Code

### Style
- **PEP 8** : Vérifier avec `make lint`
- **Black** : Formatage automatique avec `make format`
- **Type hints** : Obligatoires pour toutes les fonctions
- **Docstrings** : Style Google pour toutes les classes/fonctions publiques

### Tests
- Couverture actuelle: 87% (objectif >70%)
- Tests unitaires obligatoires pour toute nouvelle fonction
- Tests d'intégration pour nouvelles commandes
- Tous les tests doivent passer (250/250 ✅)

```bash
# Tous les tests
make test

# Avec couverture
make test-cov

# Tests spécifiques
pytest tests/unit/test_api.py -v

# Linting
make lint
```

### Commits
Format conventional commits:
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `refactor:` refactoring sans changement fonctionnel
- `test:` ajout/modification de tests
- `docs:` documentation

**Exemple:**
```bash
feat: ajouter recherche d'utilisateurs
fix: corriger gestion d'erreurs HTTP
refactor: simplifier couche API
test: ajouter tests pour configuration
docs: mettre à jour README
```

## 📝 Ajouter une Nouvelle Commande

1. Ajouter méthode dans `src/commands/<domaine>.py`
2. Enregistrer dans `CommandHandler._register_commands()`
3. Ajouter tests dans `tests/unit/commands/test_<domaine>.py`
4. Documenter dans README.md

**Exemple:**
```python
# src/commands/issues.py
def ma_nouvelle_commande(self, args: List[str]) -> CommandResult:
    """
    Description de la commande.
    
    Usage: ma-commande <arg1> [arg2]
    """
    try:
        # Votre logique ici
        return self._success(data=result)
    except SonarQubeAPIError as e:
        return self._handle_api_error(e, "Erreur...")
```

## 🏗️ Ajouter un Nouveau Endpoint API

1. Ajouter méthode dans `src/api/<domaine>.py`
2. Ajouter tests dans `tests/unit/api/test_<domaine>.py`
3. Mettre à jour la façade dans `src/api/__init__.py` si nécessaire

**Exemple:**
```python
# src/api/issues.py
def ma_nouvelle_methode(self, param: str) -> Dict[str, Any]:
    """Description de la méthode."""
    response = self._get('/api/endpoint', {'param': param})
    return response
```

## 📖 Documentation

- **Code** : Docstrings obligatoires (style Google)
- **Features** : Mettre à jour README.md
- **Changements** : Ajouter entrée dans docs/CHANGELOG.md

**Format docstring:**
```python
def ma_fonction(arg1: str, arg2: int = 0) -> Dict[str, Any]:
    """
    Description brève de la fonction.
    
    Args:
        arg1: Description du premier argument
        arg2: Description du deuxième argument (défaut: 0)
    
    Returns:
        Description du retour
    
    Raises:
        SonarQubeAPIError: En cas d'erreur API
    
    Examples:
        >>> ma_fonction("test", 5)
        {'resultat': 'OK'}
    """
```

## 🧪 Principes de Test

- **Isolation** : Chaque test doit être indépendant
- **Mocking** : Utiliser `pytest-mock` pour les appels API
- **Coverage** : Viser >70% de couverture sur les nouveaux fichiers

**Exemple de test:**
```python
def test_ma_commande(mock_api):
    """Test de ma nouvelle commande."""
    # Arrange
    mock_api.search_issues.return_value = {'issues': []}
    handler = CommandHandler(mock_api, config)
    
    # Act
    result = handler.execute('ma-commande', ['arg1'])
    
    # Assert
    assert result.success is True
    assert 'data' in result.data
```

## 🔒 Sécurité

- **Jamais** de tokens ou secrets dans le code
- **Toujours** valider les inputs utilisateur
- **Filtrage** des logs sensibles automatique

## ❓ Questions

- Ouvrir une issue sur GitHub

## 📜 Licence

Projet open source sous licence MIT.





