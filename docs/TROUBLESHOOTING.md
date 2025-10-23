# 🔧 Dépannage SonarQube MCP

## 🎯 Utiliser le script de diagnostic

**Première étape recommandée** : Lancer le script de diagnostic complet

```bash
cd /path/to/MCP_SonarQube
source venv/bin/activate
python3 diagnose.py
```

Ce script vérifie automatiquement :
- ✅ Variables d'environnement
- ✅ Installation Python
- ✅ Structure du projet
- ✅ Connexion SonarQube
- ✅ Authentification
- ✅ Permissions du token

## ⚠️ Limitations Connues

### Commande `projects` - HTTP 403

**Symptôme**: `python3 sonarqube_cli.py projects` retourne HTTP 403

**Cause**: La commande `projects` nécessite des droits Browse globaux sur tous les projets. 
Votre token peut avoir accès uniquement à des projets spécifiques.

**Solutions**:
1. Utiliser `project-info <project_key>` pour un projet spécifique
2. Demander les droits Browse globaux à l'administrateur SonarQube
3. Utiliser directement l'API SonarQube pour des requêtes spécifiques

**Alternatives**:
```bash
# Au lieu de:
python3 sonarqube_cli.py projects

# Utiliser:
python3 sonarqube_cli.py project-info mon-projet
```

### Commande `health` - HTTP 403

**Symptôme**: `python3 sonarqube_cli.py health` retourne HTTP 403

**Cause**: La commande `health` est réservée aux administrateurs système.

**Solution**: Cette commande n'est pas nécessaire pour l'utilisation normale du MCP.
Elle est utilisée uniquement pour le diagnostic système.

**Alternative**: Utiliser `version` pour vérifier que le serveur est accessible:
```bash
python3 sonarqube_cli.py version
```

## ✅ Nouveaux Outils v4.0.0

Les 5 nouveaux outils suivants sont disponibles depuis la version 4.0.0 :

1. **Historique des analyses** (`analyses`) - Suivi de l'évolution qualité
2. **Duplications de code** (`duplications`) - Détection de code dupliqué
3. **Code source annoté** (`source-lines`) - Visualisation code avec issues
4. **Liste des métriques** (`metrics-list`) - Métriques disponibles
5. **Langages supportés** (`languages`) - Langages de programmation

**Exemples d'utilisation** :
```bash
# Historique des analyses
python3 sonarqube_cli.py analyses mon-projet

# Liste des métriques
python3 sonarqube_cli.py metrics-list

# Langages supportés
python3 sonarqube_cli.py languages
```

Voir [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md) pour plus d'exemples.

## ❌ Erreur HTTP 403 (Forbidden)

### Symptôme
```
ERROR: HTTP 403: 403 Client Error
API Projects: Code 403
```

### Cause
Votre token est **valide** mais n'a **pas les permissions** nécessaires.

### Solution

1. **Vérifier vos permissions actuelles** :
   - Se connecter à https://sonarqube.example.com
   - Mon compte → Sécurité → Tokens
   - Vérifier les tokens existants

2. **Générer un nouveau token** :
   - Cliquer sur "Generate"
   - Nom : "MCP Cursor" ou similaire
   - Type : User Token
   - Copier le token (affiché une seule fois !)

3. **Mettre à jour le token** :
   ```bash
   nano ~/.zshrc
   
   # Modifier la ligne :
   export SONARQUBE_TOKEN="nouveau_token_ici"
   
   # Sauvegarder et recharger
   source ~/.zshrc
   ```

4. **Vérifier que ça fonctionne** :
   ```bash
   cd /path/to/MCP_SonarQube
   source venv/bin/activate
   python3 diagnose.py
   ```

### Permissions minimales requises

Pour que le MCP fonctionne, votre token doit avoir accès au minimum à :
- ✅ **Browse** sur les projets
- ✅ **See Source Code** pour voir les détails des fichiers
- ✅ **Administer Issues** pour assigner des issues (optionnel)

Si vous n'avez pas accès à un projet, demandez à l'administrateur SonarQube de vous donner les permissions.

## ❌ Erreur HTTP 401 (Unauthorized)

### Symptôme
```
ERROR: HTTP 401: 401 Client Error
```

### Cause
Token invalide, expiré ou non défini.

### Solution

```bash
# Vérifier que le token est défini
echo $SONARQUBE_TOKEN

# Si vide ou invalide, définir un nouveau token
export SONARQUBE_TOKEN="votre_token"
```

## ❌ Token non défini

### Symptôme
```
SONARQUBE_TOKEN: NON DÉFINIE
```

### Solution

```bash
# Ajouter dans ~/.zshrc
echo 'export SONARQUBE_TOKEN="votre_token_ici"' >> ~/.zshrc
source ~/.zshrc

# Vérifier
echo $SONARQUBE_TOKEN
```

## ❌ Module 'requests' non trouvé

### Symptôme
```
ModuleNotFoundError: No module named 'requests'
```

### Cause
Le script n'est pas exécuté dans l'environnement virtuel.

### Solution

```bash
cd /path/to/MCP_SonarQube
source venv/bin/activate
pip install -r requirements.txt
```

## ❌ Cursor ne voit pas le MCP

### Symptôme
L'assistant ne répond pas aux requêtes SonarQube.

### Solution

1. **Vérifier la configuration** :
   ```bash
   cat ~/.cursor/mcp.json | grep sonarqube
   ```

2. **Vérifier les chemins** :
   ```bash
   ls -la /path/to/MCP_SonarQube/venv/bin/python
   ls -la /path/to/MCP_SonarQube/sonarqube_mcp_server.py
   ```

3. **Redémarrer Cursor** complètement

4. **Vérifier les logs** :
   ```bash
   tail -f /tmp/sonarqube_mcp.log
   ```

## ❌ Variables d'environnement non prises en compte

### Symptôme
Les variables définies dans `~/.zshrc` ne sont pas visibles.

### Cause
Le terminal ou Cursor n'a pas rechargé le fichier.

### Solution

```bash
# Recharger le shell
source ~/.zshrc

# Vérifier
echo $SONARQUBE_URL
echo $SONARQUBE_TOKEN

# Si Cursor est déjà lancé, le fermer complètement et relancer
# Ou lancer Cursor depuis un nouveau terminal
cursor
```

## ❌ Erreur "Extra data: line 1 column 5"

### Symptôme
```
ERROR: Request error: Extra data: line 1 column 5 (char 4)
```

### Cause
Bug dans l'ancien code pour l'endpoint `version` (maintenant corrigé).

### Solution

Le code a été corrigé. Mettez à jour votre copie du projet :
```bash
cd /path/to/MCP_SonarQube
git pull  # Si vous utilisez git
```

Ou utilisez plutôt ces commandes de test :
```bash
python3 sonarqube_cli.py projects
python3 sonarqube_cli.py users votre.nom
```

## ❌ Changement de projet ne fonctionne pas

### Symptôme
Le MCP utilise toujours le même projet.

### Solution

```bash
# Changer le projet par défaut
export SONARQUBE_PROJECT_KEY="NouveauProjet"

# Ou spécifier le projet directement dans la commande
python3 sonarqube_cli.py issues AutreProjet
```

## ❌ Erreur SSL Certificate

### Symptôme
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

### Solution

```bash
# Temporairement désactiver la vérification SSL (développement uniquement)
export SONARQUBE_VERIFY_SSL="false"
```

## 🔍 Commandes de diagnostic utiles

```bash
# Vérifier toute la configuration
cd /path/to/MCP_SonarQube
source venv/bin/activate
python3 diagnose.py

# Vérifier les variables
echo "URL: $SONARQUBE_URL"
echo "Token: ${SONARQUBE_TOKEN:0:10}..."
echo "Project: $SONARQUBE_PROJECT_KEY"

# Tester des commandes simples
python3 sonarqube_cli.py projects
python3 sonarqube_cli.py users votre.nom

# Voir les logs du serveur MCP
tail -f /tmp/sonarqube_mcp.log

# Vérifier la config Cursor
cat ~/.cursor/mcp.json | jq '.mcpServers.sonarqube'
```

## 📞 Obtenir de l'aide

Si aucune solution ne fonctionne :

1. **Lancer le diagnostic complet** :
   ```bash
   python3 diagnose.py > diagnostic-output.txt
   ```

2. **Vérifier les logs** :
   ```bash
   cat /tmp/sonarqube_mcp.log
   ```

3. **Contacter l'équipe** avec :
   - Le fichier `diagnostic-output.txt`
   - Les logs d'erreur
   - Votre configuration (sans le token !)

## 📚 Documentation

- [QUICK_START.md](QUICK_START.md) - Démarrage rapide
- [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md) - Guide complet
- [INSTALLATION.md](INSTALLATION.md) - Installation détaillée

---

**N'oubliez pas : Le diagnostic (`python3 diagnose.py`) résout 90% des problèmes ! 🎯**

