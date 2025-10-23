# 📦 Guide d'installation SonarQube MCP

Ce guide vous accompagne pas à pas dans l'installation et la configuration du SonarQube MCP.

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :

- ✅ Python 3.8 ou supérieur installé
- ✅ pip (gestionnaire de paquets Python)
- ✅ Accès à un serveur SonarQube
- ✅ Un token d'authentification SonarQube valide
- ✅ Cursor IDE installé (pour l'intégration MCP)

## 🚀 Installation

### Étape 1 : Cloner le repository

```bash
# Via GitHub
git clone https://github.com/SEPTEO-OPENSOURCE/MCP_SonarQube.git
cd MCP_SonarQube
```

### Étape 2 : Créer l'environnement virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement (macOS/Linux)
source venv/bin/activate

# Activer l'environnement (Windows)
venv\Scripts\activate
```

### Étape 3 : Installer les dépendances

```bash
# Installer les dépendances de production
pip install -r requirements.txt

# Vérifier l'installation
python -c "import src; print('Installation réussie !')"
```

## ⚙️ Configuration

### Étape 4 : Configurer les variables d'environnement

> ⚠️ **Changement depuis v4.0:** SONARQUBE_URL est maintenant obligatoire.
> Ajoutez-le à votre ~/.zshrc: `export SONARQUBE_URL="https://votre-server.com"`

#### Méthode 1 : Via ~/.zshrc ou ~/.bashrc (Recommandé)

```bash
# Ouvrir le fichier de configuration
nano ~/.zshrc  # ou ~/.bashrc sur Linux

# Ajouter ces lignes à la fin du fichier
export SONARQUBE_URL="https://sonarqube.example.com"
export SONARQUBE_TOKEN="votre_token_ici"
export SONARQUBE_PROJECT_KEY="MyProject"  # Optionnel : projet par défaut
export SONARQUBE_USER="votre-login"       # Optionnel : utilisateur par défaut

# Sauvegarder et recharger
source ~/.zshrc  # ou source ~/.bashrc
```

#### Méthode 2 : Via fichier .env.local (Alternatif)

```bash
# Créer un fichier .env.local
cat > .env.local << EOF
SONARQUBE_URL=https://sonarqube.example.com
SONARQUBE_TOKEN=votre_token_ici
SONARQUBE_PROJECT_KEY=MyProject
SONARQUBE_USER=votre-login
EOF

# Charger les variables avant utilisation
set -a; source .env.local; set +a
```

### Étape 5 : Créer le fichier de configuration (Optionnel)

```bash
# Copier l'exemple de configuration
cp config.yaml.example config.yaml

# Éditer avec vos paramètres
nano config.yaml
```

Exemple de configuration personnalisée :

```yaml
url: "https://sonarqube.example.com"
timeout: 30

default_project:
  key: "MyProject"
  name: "My Application"
  assignee: "developer-user"

projects:
  - key: "MyProject"
    name: "My Application"
    branch: "main"
    assignee: "developer-user"
```

## ✅ Vérification de l'installation

### Étape 6 : Tester la connexion

```bash
# Test de santé du serveur
python3 sonarqube_cli.py health

# Test de récupération de la version
python3 sonarqube_cli.py version

# Test de récupération de projet
python3 sonarqube_cli.py project-info MyProject
```

Si tout fonctionne, vous devriez voir des réponses JSON avec les données SonarQube.

## 🔗 Intégration avec Cursor

### Étape 7 : Configuration MCP dans Cursor

#### 7.1 : Obtenir les chemins absolus

```bash
# Obtenir le chemin du projet
echo "Chemin du projet: $(pwd)"

# Obtenir le chemin de Python dans le venv
echo "Chemin Python: $(pwd)/venv/bin/python"
```

#### 7.2 : Éditer la configuration Cursor

```bash
# Ouvrir le fichier de configuration MCP de Cursor
nano ~/.cursor/mcp.json
```

#### 7.3 : Ajouter la configuration SonarQube

Ajoutez cette section dans le fichier `mcp.json` :

```json
{
  "mcpServers": {
    "sonarqube": {
      "command": "/chemin/absolu/vers/MCP_SonarQube/venv/bin/python",
      "args": [
        "/chemin/absolu/vers/MCP_SonarQube/sonarqube_mcp_server.py"
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

**⚠️ Important** : 
- Remplacez `/chemin/absolu/vers/` par vos chemins réels obtenus à l'étape 7.1
- Les variables `SONARQUBE_URL`, `SONARQUBE_TOKEN`, `SONARQUBE_PROJECT_KEY` et `SONARQUBE_USER` sont automatiquement récupérées depuis votre `~/.zshrc` (configuré à l'étape 4)
- Cette approche permet de changer de projet sans modifier la configuration Cursor

#### 7.4 : Utiliser le script d'aide

Un fichier de configuration exemple est fourni :

```bash
# Copier et adapter le fichier exemple
cp cursor-mcp-config.json ~/.cursor/mcp.json.sonarqube

# Éditer avec vos chemins
nano ~/.cursor/mcp.json.sonarqube

# Fusionner avec votre configuration existante
```

### Étape 8 : Redémarrer Cursor

1. Fermez complètement Cursor
2. Rouvrez Cursor
3. Vérifiez que le MCP SonarQube est chargé dans les paramètres

### Étape 9 : Tester l'intégration

Dans Cursor, essayez ces commandes avec l'assistant :

```
"Montre-moi mes issues SonarQube assignées"
"Quelles sont les métriques du projet MyProject ?"
"Liste les hotspots de sécurité à corriger"
"Explique-moi la règle dart:S1192"
```

### Étape 10 : Vérifier la visibilité des outils

1. Ouvrez Cursor Settings
2. Allez dans Tools & MCP
3. Vous devriez voir : **"sonarqube : 7 tools, 1 resource enabled"**

Si vous voyez "No tools", vérifiez :
- Les chemins dans ~/.cursor/mcp.json
- Les logs dans /tmp/sonarqube_mcp.log
- Redémarrez complètement Cursor

Si l'outil ne répond pas ou bloque :
- Vérifiez que SONARQUBE_PROJECT_KEY est défini : `echo $SONARQUBE_PROJECT_KEY`
- Vérifiez que SONARQUBE_USER est défini : `echo $SONARQUBE_USER`
- Consultez les logs : `tail -f /tmp/sonarqube_mcp.log`

## 🎯 Utilisation quotidienne

### Démarrage rapide

```bash
# Activer l'environnement
cd /chemin/vers/MCP_SonarQube
source venv/bin/activate

# Utiliser le CLI
python3 sonarqube_cli.py mine
python3 sonarqube_cli.py bugs
python3 sonarqube_cli.py hotspots MyProject
```

### Commandes utiles

```bash
# Voir toutes les commandes disponibles
python3 sonarqube_cli.py help

# Aide sur une commande spécifique
python3 sonarqube_cli.py help issues

# Mode verbeux pour déboguer
python3 sonarqube_cli.py --verbose issues MyProject
```

## 🐛 Dépannage

### Problème : Module 'src' introuvable

**Solution** :
```bash
# Vérifier que vous êtes dans le bon répertoire
pwd

# Vérifier que l'environnement virtuel est activé
which python  # Doit pointer vers venv/bin/python

# Réinstaller si nécessaire
pip install -r requirements.txt
```

### Problème : Erreur d'authentification SonarQube

**Solution** :
```bash
# Vérifier que le token est défini
echo $SONARQUBE_TOKEN

# Si vide, le définir
export SONARQUBE_TOKEN="votre_token"

# Tester la connexion
python3 sonarqube_cli.py health
```

### Problème : Cursor ne trouve pas le MCP

**Solution** :
1. Vérifier les chemins absolus dans `~/.cursor/mcp.json`
2. Vérifier que les fichiers existent :
   ```bash
   ls -la /chemin/vers/SonarQubeMCP/venv/bin/python
   ls -la /chemin/vers/SonarQubeMCP/sonarqube_mcp_server.py
   ```
3. Redémarrer complètement Cursor

### Problème : Erreur SSL/Certificat

**Solution** :
```bash
# Désactiver la vérification SSL (développement uniquement)
export SONARQUBE_VERIFY_SSL="false"
```

## 📚 Ressources supplémentaires

- [README.md](README.md) - Documentation principale
- [SONARQUBE_MCP_README.md](SONARQUBE_MCP_README.md) - Guide détaillé
- [config.yaml.example](config.yaml.example) - Exemple de configuration

## 💬 Support

Pour toute question ou problème :

1. Consultez la documentation dans le repository
2. Vérifiez les logs dans `/tmp/sonarqube_mcp.log`
3. Contactez l'équipe de développement

---

**Installation terminée ! 🎉**

Vous pouvez maintenant utiliser SonarQube MCP avec Cursor ou en ligne de commande.

