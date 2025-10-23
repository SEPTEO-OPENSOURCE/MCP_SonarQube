# Exemples d'Utilisation

Ce dossier contient des exemples d'utilisation de l'API SonarQube MCP.

## 📝 Liste des exemples

### [basic_usage.py](basic_usage.py)
Utilisation basique de l'API pour récupérer vos issues assignées.

**Usage:**
```bash
python examples/basic_usage.py
```

### [metrics_dashboard.py](metrics_dashboard.py)
Exemple de dashboard simple affichant les métriques de qualité d'un projet.

**Usage:**
```bash
python examples/metrics_dashboard.py
```

### [advanced_filters.py](advanced_filters.py)
Filtres avancés pour rechercher des issues spécifiques (type, sévérité, tags, etc.).

**Usage:**
```bash
python examples/advanced_filters.py
```

## ⚙️ Configuration

Tous les exemples nécessitent que les variables d'environnement suivantes soient définies :

```bash
export SONARQUBE_URL="https://sonarqube.example.com"
export SONARQUBE_TOKEN="votre_token_ici"
export SONARQUBE_PROJECT_KEY="YourProject"  # Optionnel
export SONARQUBE_USER="votre-login"         # Optionnel
```

## 🚀 Exécution

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Exécuter un exemple
python examples/basic_usage.py
```

## 📚 Documentation

Pour plus d'informations, consultez :
- [README principal](../README.md)
- [Guide d'utilisation](../docs/GUIDE_UTILISATION.md)
- [Documentation de l'API](../src/api/)





