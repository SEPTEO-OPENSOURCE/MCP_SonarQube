# ⚡ Quick Start - MCP SonarQube

> ⚠️ **Changement depuis v4.0:** SONARQUBE_URL est maintenant obligatoire.
> Ajoutez-le à votre ~/.zshrc: `export SONARQUBE_URL="https://votre-server.com"`

## 🎯 En 3 étapes

### 1️⃣ Configuration initiale (une seule fois)

```bash
# REQUIS : Configurer les variables d'environnement
echo 'export SONARQUBE_URL="https://sonarqube.example.com"' >> ~/.zshrc
echo 'export SONARQUBE_TOKEN="votre_token"' >> ~/.zshrc
echo 'export SONARQUBE_PROJECT_KEY="MyProject"' >> ~/.zshrc  # REQUIS pour "mes issues"
echo 'export SONARQUBE_USER="votre-login"' >> ~/.zshrc       # REQUIS pour "mes issues"
source ~/.zshrc

# Installer le MCP
cd /path/to/MCP_SonarQube
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Tester la connexion
python3 sonarqube_cli.py projects
```

### 2️⃣ Configurer Cursor (une seule fois)

Ajouter dans `~/.cursor/mcp.json` :

```json
{
  "mcpServers": {
    "sonarqube": {
      "command": "/path/to/MCP_SonarQube/venv/bin/python",
      "args": ["/path/to/MCP_SonarQube/sonarqube_mcp_server.py"],
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

Redémarrer Cursor.

### 3️⃣ Utiliser depuis n'importe quel projet

Ouvrez **n'importe quel projet** dans Cursor et demandez à l'assistant :

```
"Montre-moi mes issues SonarQube"          ← Automatique !
"Mes issues assignées"                      ← Automatique !
"Qu'ai-je à corriger ?"                     ← Automatique !
"Liste les bugs du projet MyProject"
"Quelles sont les métriques du projet ?"
"Explique la règle dart:S1192"
```

L'assistant utilisera automatiquement votre projet (SONARQUBE_PROJECT_KEY) et votre utilisateur (SONARQUBE_USER).
**Aucun paramètre à fournir.**

## 📝 Commandes les plus utiles

| Demande | Ce que ça fait |
|---------|----------------|
| `Mes issues SonarQube` | Issues assignées à vous |
| `Bugs critiques du projet X` | Bugs critiques |
| `Métriques du projet X` | Qualité du code |
| `Hotspots de sécurité` | Vulnérabilités à revoir |
| `Explique la règle Y` | Détails d'une règle |
| `Historique des analyses` | Évolution qualité ✨ NOUVEAU |
| `Duplications dans fichier.dart` | Code dupliqué ✨ NOUVEAU |
| `Quelles métriques disponibles ?` | Liste métriques ✨ NOUVEAU |
| `Langages supportés ?` | Langages SonarQube ✨ NOUVEAU |

## 🔄 Changer de projet

```bash
# Dans le terminal
export SONARQUBE_PROJECT_KEY="AutreProjet"
cursor .
```

Ou demandez directement :
```
"Issues du projet AnotherProject"
```

## 🐛 Problème ?

### Script de diagnostic automatique

```bash
cd /path/to/MCP_SonarQube
source venv/bin/activate
python3 diagnose.py  # ← Vérifie tout automatiquement
```

### Dépannage manuel

Voir la [documentation de dépannage complète](TROUBLESHOOTING.md)

## 📚 Documentation complète

- [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md) - Guide complet avec exemples
- [README.md](README.md) - Documentation technique
- [INSTALLATION.md](INSTALLATION.md) - Installation détaillée

---

**C'est tout ! Le MCP fonctionne maintenant dans tous vos projets Cursor ! 🎉**

