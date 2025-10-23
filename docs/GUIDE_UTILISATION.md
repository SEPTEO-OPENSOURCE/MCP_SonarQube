# 🚀 Guide d'utilisation - MCP SonarQube depuis un projet tiers

## 📋 Vue d'ensemble

Une fois le MCP SonarQube installé et configuré, vous pouvez l'utiliser depuis **n'importe quel projet** ouvert dans Cursor. Le MCP fonctionne comme un service global accessible à tous vos projets.

## 🎯 Concept : Comment ça fonctionne ?

```
┌──────────────────────────────────────────────────────────┐
│  Votre Projet Flutter/React/Python/etc.                 │
│  (n'importe où sur votre machine)                        │
└──────────────────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  Cursor IDE                                              │
│  • Ouvre votre projet                                    │
│  • Charge la config MCP globale (~/.cursor/mcp.json)    │
└──────────────────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  MCP SonarQube Server                                    │
│  (/path/to/MCP_SonarQube/)                              │
│  • Lit vos variables d'environnement (~/.zshrc)         │
│  • Se connecte à SonarQube                               │
│  • Expose les outils à l'assistant Cursor               │
└──────────────────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  SonarQube Server                                        │
│  (https://sonarqube.example.com)                         │
└──────────────────────────────────────────────────────────┘
```

**Point clé** : Le MCP SonarQube est **global** et fonctionne pour tous vos projets ouverts dans Cursor !

## ✅ Prérequis

Avant d'utiliser le MCP depuis un projet tiers, assurez-vous que :

1. ✅ Le MCP SonarQube est installé (`/path/to/MCP_SonarQube/`)
2. ✅ Les variables d'environnement sont configurées dans `~/.zshrc`
3. ✅ La configuration MCP est ajoutée dans `~/.cursor/mcp.json`
4. ✅ Cursor a été redémarré après la configuration

### Vérification rapide

```bash
# Vérifier les variables d'environnement
echo $SONARQUBE_URL
echo $SONARQUBE_TOKEN
echo $SONARQUBE_PROJECT_KEY
echo $SONARQUBE_USER

# Vérifier la configuration Cursor
cat ~/.cursor/mcp.json | grep sonarqube

# Tester le MCP directement
cd /path/to/MCP_SonarQube
source venv/bin/activate
python3 sonarqube_cli.py health
```

## 🎨 Utilisation depuis un projet tiers

### Scénario 1 : Votre projet principal

Vous travaillez sur votre projet principal :

```bash
cd /path/to/your/project
cursor .
```

Dans Cursor, vous pouvez maintenant interroger l'assistant :

#### Exemples de requêtes

**Mes issues assignées** :
```
Montre-moi mes issues SonarQube
```
→ Utilise **automatiquement** SONARQUBE_PROJECT_KEY et SONARQUBE_USER
→ **Aucun moyen** de spécifier un autre projet (par design)
→ Pour un autre projet, modifiez temporairement la variable d'environnement

**Issues d'un fichier spécifique** :
```
Quelles sont les issues SonarQube du fichier lib/main.dart ?
```

**Métriques du projet** :
```
Donne-moi les métriques de qualité du projet MyProject
```

**Hotspots de sécurité** :
```
Liste les hotspots de sécurité à corriger sur MyProject
```

**Détails d'une règle** :
```
Explique-moi la règle SonarQube dart:S1192
```

### Scénario 2 : Autre projet (nouveau projet)

Vous travaillez sur un nouveau projet :

```bash
cd /path/to/NewProject
cursor .
```

#### Option A : Utiliser le projet par défaut

Si votre `~/.zshrc` définit `SONARQUBE_PROJECT_KEY` et `SONARQUBE_USER`, le MCP les utilisera automatiquement :

```
Montre-moi mes issues SonarQube
Liste les bugs critiques
Quels sont les hotspots de sécurité ?
```

#### Option B : Spécifier un autre projet

Demandez explicitement un autre projet :

```
Montre-moi les issues du projet AutreProjet.Backend
Liste les bugs du projet MonNouveauProjet
Donne-moi les métriques du projet XYZ
```

### Scénario 3 : Changer de projet temporairement

Si vous voulez temporairement analyser un autre projet sans modifier `~/.zshrc` :

```bash
# Dans le terminal de Cursor
export SONARQUBE_PROJECT_KEY="AutreProjet"
```

Puis dans l'assistant :
```
Montre-moi mes issues SonarQube  # Utilisera "AutreProjet"
```

## 🎯 Commandes disponibles dans Cursor

### Via l'assistant conversationnel

Voici les formulations que l'assistant comprend :

#### Issues

| Demande | Description |
|---------|-------------|
| "Montre-moi mes issues SonarQube" | Issues assignées à vous |
| "Liste les issues du projet X" | Toutes les issues d'un projet |
| "Quelles sont les issues du fichier Y ?" | Issues d'un fichier spécifique |
| "Liste les bugs critiques" | Issues de type BUG avec sévérité CRITICAL |
| "Montre les vulnérabilités" | Issues de type VULNERABILITY |
| "Donne l'historique de l'issue ABC123" | Changelog d'une issue |

#### Métriques et qualité

| Demande | Description |
|---------|-------------|
| "Métriques du projet X" | Toutes les métriques de qualité |
| "Couverture de tests du projet X" | Métrique coverage |
| "Statut du Quality Gate du projet X" | État du Quality Gate |
| "Nombre de bugs dans le projet X" | Métrique bugs |

#### Sécurité

| Demande | Description |
|---------|-------------|
| "Liste les hotspots de sécurité" | Hotspots à revoir |
| "Hotspots revus du projet X" | Hotspots déjà traités |

#### Projets et utilisateurs

| Demande | Description |
|---------|-------------|
| "Liste les projets SonarQube" | Tous les projets disponibles |
| "Infos sur le projet X" | Détails d'un projet |
| "Recherche l'utilisateur Y" | Trouver un utilisateur |

#### Règles

| Demande | Description |
|---------|-------------|
| "Explique la règle dart:S1192" | Détails d'une règle |
| "Cherche les règles sur les strings" | Recherche de règles |

## 💡 Exemples pratiques complets

### Exemple 1 : Review de code

Vous êtes en train de faire une review de code dans votre projet Flutter :

```
Vous : "Quelles sont les issues SonarQube du fichier lib/services/api_service.dart ?"

Assistant : [Utilise le MCP SonarQube]
"J'ai trouvé 3 issues dans ce fichier :
1. Ligne 42 : String literals should not be duplicated (dart:S1192)
2. Ligne 58 : Exception should not be caught without being logged (dart:S1234)
3. Ligne 105 : Method complexity too high (dart:S5678)"

Vous : "Explique-moi la règle dart:S1192"

Assistant : [Utilise le MCP SonarQube]
"La règle dart:S1192 concerne les String literals dupliqués.
Détails : [Description complète de la règle]
Recommandation : Créer des constantes pour les strings réutilisés."
```

### Exemple 2 : Dashboard de qualité

Vous voulez un aperçu de la qualité du projet :

```
Vous : "Donne-moi un aperçu complet de la qualité du projet MyProject"

Assistant : [Utilise le MCP SonarQube]
"Voici l'état de qualité du projet :

📊 Métriques principales :
- Lignes de code : 15,234
- Couverture de tests : 78.5%
- Bugs : 12 (dont 2 critiques)
- Vulnérabilités : 3
- Code smells : 45
- Dette technique : 2j 4h

🚨 Points d'attention :
1. 2 bugs critiques à corriger
2. 3 vulnérabilités de sécurité
3. 8 hotspots de sécurité à revoir

Quality Gate : ✅ PASSED"
```

### Exemple 3 : Triage des issues

Vous voulez prioriser votre travail :

```
Vous : "Liste mes issues SonarQube par ordre de sévérité"

Assistant : [Utilise le MCP SonarQube]
"Issues assignées à developer-user :

🔴 BLOCKER (1) :
- Issue #1234 : SQL injection vulnerability (lib/database.dart:45)

🟠 CRITICAL (3) :
- Issue #1235 : Null pointer dereference (lib/main.dart:120)
- Issue #1236 : Hardcoded credentials (lib/config.dart:12)
- Issue #1237 : Resource leak (lib/services/file_service.dart:78)

🟡 MAJOR (8) :
[...]"

Vous : "Montre-moi le détail de l'issue #1234"

Assistant : [Utilise le MCP SonarQube]
"Détails de l'issue #1234 :
[Historique complet, commentaires, etc.]"
```

## 🔄 Workflow recommandé

### 1. Analyse quotidienne

Au début de votre journée de travail :

```
"Montre-moi mes nouvelles issues SonarQube depuis hier"
"Y a-t-il des issues critiques sur le projet ?"
```

### 2. Avant un commit

Avant de committer du code :

```
"Analyse les issues SonarQube du fichier que je viens de modifier"
"Le Quality Gate du projet est-il OK ?"
```

### 3. Review de Pull Request

Lors d'une review de PR :

```
"Quelles sont les nouvelles issues introduites dans cette PR ?"
"Y a-t-il des hotspots de sécurité dans les fichiers modifiés ?"
```

### 4. Sprint planning

Pour planifier votre sprint :

```
"Liste toutes mes issues SonarQube"
"Quelles sont les issues les plus anciennes ?"
"Combien de temps faudra-t-il pour corriger mes issues critiques ?"
```

## 🎓 Cas d'usage avancés

### Multi-projets

Si vous travaillez sur plusieurs projets :

```bash
# Terminal 1 - Projet Frontend
cd ~/workspace/Frontend/MyApp
export SONARQUBE_PROJECT_KEY="MyApp.Frontend"
cursor .

# Terminal 2 - Projet Backend
cd ~/workspace/Backend/API
export SONARQUBE_PROJECT_KEY="MyApp.Backend"
cursor .
```

Chaque instance de Cursor utilisera le bon projet !

### Avec fichier de configuration

Créez un fichier `sonarqube.config.yaml` dans votre projet :

```yaml
# ~/workspace/MyProject/sonarqube.config.yaml
url: "https://sonarqube.example.com"
default_project:
  key: "MyProject"
  name: "My Project"
  assignee: "developer-user"
```

Puis utilisez-le :

```bash
export SONARQUBE_CONFIG="$(pwd)/sonarqube.config.yaml"
```

### Scripts d'automatisation

Créez des scripts pour automatiser vos analyses :

```bash
#!/bin/bash
# ~/workspace/MyProject/check-sonarqube.sh

cd /path/to/MCP_SonarQube
source venv/bin/activate

echo "📊 Vérification SonarQube pour MyProject..."

# Mes issues
python3 sonarqube_cli.py my-issues MyProject developer-user > /tmp/my-issues.json

# Bugs critiques
python3 sonarqube_cli.py issues-by-severity MyProject CRITICAL > /tmp/critical-bugs.json

# Quality Gate
python3 sonarqube_cli.py quality-gate MyProject > /tmp/quality-gate.json

echo "✅ Rapports générés dans /tmp/"
```

## 🐛 Dépannage

### Le MCP ne répond pas

```bash
# Vérifier que Cursor voit le MCP
# Dans Cursor : Ouvrir les paramètres > MCP Servers
# Vous devriez voir "sonarqube" dans la liste

# Vérifier les logs
tail -f /tmp/sonarqube_mcp.log
```

### L'assistant ne comprend pas mes commandes

Soyez explicite :

❌ "mes issues"  
✅ "Montre-moi mes issues SonarQube"

❌ "bugs"  
✅ "Liste les bugs du projet MyProject"

### Changement de projet ne fonctionne pas

```bash
# Redémarrer Cursor après avoir modifié les variables
# Ou ouvrir un nouveau projet pour forcer le rechargement
```

## 🆕 Nouveaux Outils (v4.1.0)

### 📊 Historique des Analyses

**Description** : Suivez l'évolution de la qualité de votre projet dans le temps.

**Exemples CLI** :
```bash
# Toutes les analyses du projet
python3 sonarqube_cli.py analyses MyProject

# Analyses depuis une date
python3 sonarqube_cli.py analyses MyProject 2025-01-01

# Analyses sur une période
python3 sonarqube_cli.py analyses MyProject 2025-01-01 2025-01-31
```

**Exemples MCP (Cursor)** :
```
"Historique des analyses de mon projet"
"Analyses depuis janvier 2025"
"Évolution qualité du projet MyProject depuis septembre"
```

**Cas d'usage** :
- Identifier les régressions après un déploiement
- Analyser les tendances qualité sur plusieurs semaines
- Suivre l'impact des corrections

---

### 🔄 Duplications de Code

**Description** : Détectez le code dupliqué dans vos fichiers pour améliorer la maintenabilité.

**Exemples CLI** :
```bash
# Duplications dans un fichier Dart
python3 sonarqube_cli.py duplications "MyProject:lib/main.dart"

# Duplications dans un fichier Java
python3 sonarqube_cli.py duplications "MyProject:src/main/java/UserService.java"
```

**Exemples MCP (Cursor)** :
```
"Duplications dans main.dart"
"Code dupliqué de UserService.java"
"Quels blocs de code sont répétés ?"
```

**Cas d'usage** :
- Identifier le code à refactorer
- Réduire la duplication pour améliorer la maintenabilité
- Analyser les patterns répétés

---

### 📝 Code Source Annoté

**Description** : Visualisez le code source avec toutes les annotations SonarQube (issues, couverture, etc.).

**Exemples CLI** :
```bash
# Code complet d'un fichier
python3 sonarqube_cli.py source-lines "MyProject:lib/main.dart"

# Lignes 10 à 50
python3 sonarqube_cli.py source-lines "MyProject:lib/main.dart" 10 50

# Depuis la ligne 100
python3 sonarqube_cli.py source-lines "MyProject:lib/main.dart" 100
```

**Exemples MCP (Cursor)** :
```
"Code source de main.dart avec les issues"
"Lignes 10-50 de UserService.java"
"Montre-moi le code avec les annotations SonarQube"
```

**Cas d'usage** :
- Voir le code avec les issues annotées directement
- Comprendre le contexte d'une issue
- Analyser une portion spécifique de code

---

### 📐 Liste des Métriques

**Description** : Découvrez toutes les métriques disponibles dans SonarQube.

**Exemples CLI** :
```bash
# Liste toutes les métriques
python3 sonarqube_cli.py metrics-list
```

**Exemples MCP (Cursor)** :
```
"Quelles métriques sont disponibles ?"
"Liste des métriques SonarQube"
"Métriques que je peux suivre"
```

**Cas d'usage** :
- Découvrir les métriques disponibles
- Choisir les métriques pertinentes pour votre projet
- Comprendre la signification des métriques

---

### 🌐 Langages Supportés

**Description** : Liste tous les langages de programmation supportés par SonarQube.

**Exemples CLI** :
```bash
# Liste tous les langages
python3 sonarqube_cli.py languages
```

**Exemples MCP (Cursor)** :
```
"Quels langages sont supportés ?"
"Liste des langages SonarQube"
"Est-ce que Dart est supporté ?"
```

**Cas d'usage** :
- Vérifier si un langage est supporté
- Planifier l'analyse de nouveaux projets
- Découvrir les langages disponibles

---

## 📚 Ressources

- [README.md](README.md) - Documentation complète
- [INSTALLATION.md](INSTALLATION.md) - Guide d'installation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Dépannage
- [cursor-mcp-config-README.md](cursor-mcp-config-README.md) - Configuration MCP

## 💬 Questions fréquentes

**Q : Le MCP fonctionne-t-il avec tous mes projets ?**  
R : Oui ! Le MCP est global, il fonctionne depuis n'importe quel projet ouvert dans Cursor.

**Q : Dois-je installer quelque chose dans mon projet Flutter/React/etc ?**  
R : Non, aucune installation n'est requise dans vos projets. Le MCP fonctionne de manière indépendante.

**Q : Puis-je utiliser le MCP dans plusieurs projets simultanément ?**  
R : Oui, chaque instance de Cursor peut utiliser le MCP indépendamment.

**Q : Comment changer de projet SonarQube rapidement ?**  
R : Modifiez la variable `SONARQUBE_PROJECT_KEY` dans votre terminal avant de lancer Cursor.

**Q : Le MCP consomme-t-il des ressources quand je ne l'utilise pas ?**  
R : Non, le MCP ne s'exécute que lorsque l'assistant l'appelle.

---

**Profitez du MCP SonarQube dans tous vos projets ! 🚀**

