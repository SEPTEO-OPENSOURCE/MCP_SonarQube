# 📝 Configuration MCP pour Cursor - Guide

## 🎯 Approche recommandée

Ce fichier `cursor-mcp-config.json` contient **uniquement les paramètres génériques** de configuration MCP. Les variables sensibles et spécifiques au projet sont **intentionnellement absentes**.

## ✅ Variables dans la configuration Cursor (mcp.json)

Ces variables sont **génériques** et peuvent rester dans la configuration globale :

```json
"env": {
  "SONARQUBE_QUALITY_AUDIENCE": "assistant",
  "SONARQUBE_QUALITY_PRIORITY": "0.8",
  "SONARQUBE_SECURITY_AUDIENCE": "assistant",
  "SONARQUBE_SECURITY_PRIORITY": "0.9",
  "SONARQUBE_METADATA_ENABLED": "true"
}
```

## ❌ Variables À NE PAS mettre dans mcp.json

Ces variables sont **spécifiques au projet/environnement** et doivent être dans `~/.zshrc` :

- `SONARQUBE_URL` - URL du serveur (spécifique à l'organisation)
- `SONARQUBE_TOKEN` - Token d'authentification (secret)
- `SONARQUBE_PROJECT_KEY` - Projet par défaut (spécifique au projet)
- `SONARQUBE_USER` - Utilisateur par défaut (personnel)

## 🔧 Configuration complète

### 1. Variables d'environnement dans ~/.zshrc

```bash
# Ouvrir le fichier
nano ~/.zshrc

# Ajouter ces lignes à la fin
export SONARQUBE_URL="https://sonarqube.example.com"
export SONARQUBE_TOKEN="votre_token_ici"
export SONARQUBE_PROJECT_KEY="MyProject"  # Optionnel
export SONARQUBE_USER="developer-user"    # Optionnel

# Sauvegarder et recharger
source ~/.zshrc
```

### 2. Configuration Cursor dans ~/.cursor/mcp.json

```json
{
  "mcpServers": {
    "sonarqube": {
      "command": "/path/to/MCP_SonarQube/venv/bin/python",
      "args": [
        "/path/to/MCP_SonarQube/sonarqube_mcp_server.py"
      ],
      "env": {
        "SONARQUBE_QUALITY_AUDIENCE": "assistant",
        "SONARQUBE_QUALITY_PRIORITY": "0.8",
        "SONARQUBE_SECURITY_AUDIENCE": "assistant",
        "SONARQUBE_SECURITY_PRIORITY": "0.9",
        "SONARQUBE_METADATA_ENABLED": "true"
      },
      "capabilities": {
        "resources": {
          "subscribe": true,
          "listChanged": true
        }
      }
    }
  }
}
```

**Note** : Adaptez les chemins `command` et `args` à votre installation.

## ✅ Vérification de la configuration

Après configuration et redémarrage de Cursor :

### Dans Cursor Settings > Tools & MCP

Vous devriez voir :
```
sonarqube : 7 tools, 1 resource enabled
```

### Les 7 outils exposés

1. `sonarqube_issues` - 🔍 VOS issues assignées (automatique)
2. `sonarqube_measures` - 📊 Métriques de qualité
3. `sonarqube_hotspots` - 🔒 Hotspots de sécurité
4. `sonarqube_rule` - 📖 Détails de règles
5. `sonarqube_users` - 👥 Recherche d'utilisateurs
6. `sonarqube_quality_gate` - ✅ Quality Gate
7. `sonarqube_ping` - 🏓 Test de connexion

### 1 ressource exposée

- Votre projet par défaut (SONARQUBE_PROJECT_KEY)

Si les outils n'apparaissent pas, consultez [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## 🎯 Pourquoi cette approche ?

### ✅ Avantages

1. **Sécurité** : Les tokens et URLs ne sont pas dans des fichiers de config partagés
2. **Flexibilité** : Changez de projet en modifiant seulement `~/.zshrc`
3. **Générique** : La config Cursor est réutilisable pour tous les projets
4. **Séparation** : Config globale (Cursor) vs config personnelle (shell)
5. **Portabilité** : Facile de partager le projet sans exposer vos credentials

### ❌ Problèmes évités

- ❌ Hardcoding d'URLs spécifiques dans la config globale
- ❌ Tokens exposés dans des fichiers versionés
- ❌ Configuration couplée à un projet spécifique
- ❌ Difficulté de changer de projet ou d'environnement

## 🔄 Workflow multi-projets

Pour travailler sur différents projets :

```bash
# Projet 1
export SONARQUBE_PROJECT_KEY="MyProject"

# Projet 2
export SONARQUBE_PROJECT_KEY="AutreProjet"

# Vérifier la variable active
echo $SONARQUBE_PROJECT_KEY

# Pas besoin de modifier ~/.cursor/mcp.json !
```

## 📚 Mécanisme de récupération

Le serveur MCP (`sonarqube_mcp_server.py`) utilise `SonarQubeConfig.from_env()` qui :

1. Lit **d'abord** les variables d'environnement du shell (`~/.zshrc`)
2. Puis les variables définies dans `mcp.json` (si présentes)
3. Enfin utilise les valeurs par défaut

Ordre de priorité :
```
~/.zshrc  >  mcp.json env  >  valeurs par défaut
```

## 🐛 Dépannage

### Le serveur ne trouve pas SONARQUBE_URL

```bash
# Vérifier que la variable est définie
echo $SONARQUBE_URL

# Si vide, l'ajouter dans ~/.zshrc
echo 'export SONARQUBE_URL="https://sonarqube.example.com"' >> ~/.zshrc
source ~/.zshrc
```

### Cursor ne récupère pas les variables du shell

Cursor hérite des variables d'environnement du shell qui l'a lancé. Si vous avez modifié `~/.zshrc`, vous devez :

1. Ouvrir un nouveau terminal
2. Taper `source ~/.zshrc`
3. Lancer Cursor depuis ce terminal : `cursor`

Ou redémarrez votre session macOS pour que les nouvelles variables soient prises en compte.

## 📖 Références

- [README.md](README.md) - Documentation principale
- [INSTALLATION.md](INSTALLATION.md) - Guide d'installation
- [config.yaml.example](config.yaml.example) - Alternative avec fichier YAML

---

**Configuration propre et sécurisée ! ✨**




