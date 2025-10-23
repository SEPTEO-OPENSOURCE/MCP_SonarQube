# Changelog

Tous les changements notables de ce projet sont documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [4.1.0] - 2025-10-10

### 🎉 Ajouté

#### Nouveaux Outils MCP (7)
- ✨ **`sonarqube_analyses_history`** - Historique des analyses d'un projet
  - Suivi de l'évolution de la qualité dans le temps
  - Filtrage par dates (from/to)
  - Identification des régressions
  
- ✨ **`sonarqube_duplications`** - Détection de code dupliqué
  - Analyse des duplications dans un fichier
  - Identification du code à refactorer
  - Amélioration de la maintenabilité
  
- ✨ **`sonarqube_source_lines`** - Code source annoté
  - Visualisation du code avec annotations SonarQube
  - Support de range de lignes (from/to)
  - Contexte complet des issues
  
- ✨ **`sonarqube_metrics_list`** - Liste des métriques disponibles
  - Découverte des métriques SonarQube
  - Aide au choix des métriques à suivre
  
- ✨ **`sonarqube_languages`** - Langages supportés
  - Liste des langages de programmation supportés
  - Vérification de compatibilité

- ✨ **`sonarqube_projects`** - Liste des projets disponibles
  - Recherche de projets avec filtrage optionnel
  - Accès aux informations de base des projets
  - Support de la recherche par nom

- ✨ **`sonarqube_search_issues`** - Recherche avancée d'issues
  - Filtrage par projet, assigné et statuts multiples
  - Support des issues non assignées (assignee vide)
  - Validation des statuts d'issues (OPEN, CONFIRMED, etc.)

#### Tests
- 73 nouveaux tests unitaires pour les 7 nouveaux outils
- Couverture globale : 67% → **87%** (+20%)
- Total tests : 84 → **250** (+166, +198%)
- Tous les tests passent (100%)

#### Documentation
- Section "Limitations Connues" dans TROUBLESHOOTING.md
- Section "Nouveaux Outils v4.0.0" dans TROUBLESHOOTING.md
- Mise à jour QUICK_START.md avec nouveaux outils
- Mise à jour README.md avec statistiques actualisées
- Nouveau fichier NOUVEAUX_OUTILS_v4.0.md

### Amélioré
- **Couverture de tests** : +21% (67% → 88%)
- **Documentation** : Reflet exact des fonctionnalités disponibles
- **Commandes CLI** : 5 nouvelles commandes disponibles
- **BaseCommands** : Ajout de `_get_default_project_key()` helper

### Corrigé
- Test d'intégration `test_tools_list` (7 → 14 outils attendus)
- Documentation des limitations (projects, health) avec alternatives

## [4.0.0] - 2025-10-10

### 🏗️ REFACTORING MAJEUR - Clean Architecture & Clean Code

#### Changed (Breaking)
- **Licence** : Proprietary → MIT (open source)
- **Configuration** : URL SonarQube obligatoire (plus de fallback hardcodé)
- **Architecture** : Refactoring complet en modules (src/api/, src/commands/, src/mcp/)

#### Added
- **Logging** : Chemin de log configurable et portable (`SONARQUBE_LOG_DIR`, défaut: `~/.sonarqube_mcp/logs`)
- **Logging** : Niveau de log configurable (`SONARQUBE_LOG_LEVEL`, défaut: INFO)
- **Logging** : Rotation automatique par jour
- **Sécurité** : Filtrage automatique des tokens sensibles dans les logs
- **Validation** : Protection contre path traversal et injection (module `src/utils.py`)
- **Tests** : Tests d'intégration pour MCP server (>70% couverture)
- **Tests** : Tests pour CLI
- **Documentation** : Dossier `docs/` structuré
- **Documentation** : Dossier `examples/` avec exemples d'utilisation
- **Documentation** : Dossier `scripts/` pour utilitaires
- **Documentation** : `CONTRIBUTING.md` pour contributeurs
- **Documentation** : Diagrammes d'architecture Mermaid dans README

#### Security
- Les tokens et credentials sont automatiquement masqués dans les logs (patterns: squ_*, Bearer, API keys)
- Protection contre path traversal (validation des chemins de fichiers)
- Protection contre injection (validation des project_key et rule_key)
- Mode DEBUG safe pour production

#### Architecture
- **src/api/** : Client API modulaire (7 modules spécialisés)
- **src/commands/** : Commandes modulaires (6 modules par domaine)
- **src/mcp/** : Serveur MCP refactoré avec descriptions YAML externalisées
- **src/utils.py** : Utilitaires de validation et sécurité
- Aucun fichier >200 lignes (objectif Clean Code atteint)

#### Migration
- ⚠️ **Breaking**: `SONARQUBE_URL` maintenant obligatoire
- ⚠️ Migration: Ajouter à `~/.zshrc`: `export SONARQUBE_URL="https://votre-server.com"`
- ℹ️ Voir `docs/INSTALLATION.md` pour guide complet

## [3.1.4] - 2025-10-10

### 🎯 FIX CRITIQUE : Compatibilité protocole MCP et format de réponse

- **Problème**: Les appels MCP se bloquaient indéfiniment sans retourner de résultat
- **Cause 1**: Version du protocole incompatible (`2024-11-05` vs `2025-06-18` attendu par Cursor)
- **Cause 2**: Format de réponse `tools/call` incorrect (manquait l'enveloppe `result`)
- **Fix 1**: Mise à jour vers `protocolVersion: '2025-06-18'`
- **Fix 2**: Enveloppe toutes les réponses `tools/call` dans `{"result": {"content": [...]}}`

### Impact

- **Avant**: Pastille rouge dans Cursor Settings, appels bloqués indéfiniment
- **Après**: Pastille verte, réponses immédiates (< 2s)
- **Compatibilité**: Conforme au protocole MCP 2025-06-18

### Détails techniques

- Modification de `handle_request()` : `protocolVersion: '2025-06-18'`
- Modification de `_call_tool()` : enveloppe `sonarqube_ping` dans `result`
- Modification de `_call_tool()` : enveloppe les réponses success dans `result`
- Version serveur mise à jour : `3.1.3` → `3.1.4`

## [3.1.3] - 2025-10-10

### 🚨 FIX CRITIQUE : Crash du serveur MCP après 60 secondes

- **Problème**: Le serveur MCP crashait 60 secondes après le premier appel d'outil
- **Cause**: Le timeout `signal.alarm(60)` n'était pas annulé pour `sonarqube_ping`, l'alarme restait active
- **Effet**: Le serveur se terminait brutalement avec "L'appel de l'outil a dépassé le timeout de 60 secondes"
- **Fix**: Ajout de `signal.alarm(0)` avant le return de `sonarqube_ping` pour annuler l'alarme

### Impact

- **Symptôme côté utilisateur**: "Le MCP SonarQube n'est pas connecté" après 60 secondes
- **Raison**: Le serveur MCP s'arrêtait complètement au lieu de continuer à fonctionner
- **Solution**: L'alarme est maintenant correctement annulée pour tous les outils

## [3.1.2] - 2025-10-10

### 🐛 Correction critique de la pastille rouge

- **Fix de `notifications/initialized`** : Cette notification MCP ne retourne maintenant plus d'erreur
- **Raison**: Le serveur MCP retournait une erreur `-32601` pour `notifications/initialized`, causant une pastille rouge dans Cursor Settings
- **Effet**: Les notifications MCP retournent `None` (pas de réponse) au lieu d'une erreur
- La pastille devrait maintenant être **verte** dans Cursor Settings > Tools & MCP

### Détails techniques

- Ajout de la gestion de `notifications/initialized` qui retourne `None`
- Ajout d'une vérification pour ne pas envoyer de réponse quand `response is None`
- Les notifications MCP ne nécessitent pas de réponse (protocole MCP)

## [3.1.1] - 2025-10-10

### 🔧 Correction importante

- **Ajout de `additionalProperties: false`** au schéma de `sonarqube_issues`
- **Raison**: L'IA Cursor inventait parfois des paramètres invalides (ex: `random_string: "dummy"`)
- **Effet**: Force l'IA à utiliser UNIQUEMENT les paramètres définis (file_path optionnel)
- Amélioration de la description avec avertissement explicite : "Appeler SANS PARAMÈTRE (objet vide {}) pour 'mes issues'"

### Diagnostic

- Le MCP fonctionnait correctement (ignorait les paramètres invalides et utilisait les env vars)
- Mais l'interface Cursor restait bloquée en "en cours" à cause du paramètre invalide
- `additionalProperties: false` empêche désormais l'IA d'inventer des paramètres

## [3.1.0] - 2025-10-09

### Simplification finale

- **BREAKING CHANGE**: Retrait des paramètres `project_key` et `assignee` de `sonarqube_issues`
- Seul `file_path` reste optionnel
- L'outil utilise TOUJOURS les variables d'environnement `SONARQUBE_PROJECT_KEY` et `SONARQUBE_USER`
- **Raison**: Éviter la confusion de l'IA sur les paramètres optionnels qui peuvent l'inciter à deviner des valeurs

### Impact

- L'outil `sonarqube_issues` devient encore plus simple : aucun paramètre requis
- Comportement cohérent : toujours "mes issues assignées"
- Seule option : filtrer par fichier avec `file_path`

## [3.0.0] - 2025-10-09

### 🎯 SIMPLIFICATION MAJEURE - UN SEUL OUTIL POUR LES ISSUES

#### Changement MAJEUR (Breaking)
- **Suppression de `sonarqube_my_issues`** : fusionné dans `sonarqube_issues`
- **Suppression des alias** : `show_my_issues` et `get_sonarqube_issues` retirés
- **7 outils au lieu de 10** : simplification radicale de l'API MCP

#### Nouveau comportement de `sonarqube_issues`

L'outil est maintenant **intelligent** avec un comportement adaptatif :

**SANS PARAMÈTRE** (comportement par défaut) :
- Utilise automatiquement `SONARQUBE_PROJECT_KEY` (projet)
- Utilise automatiquement `SONARQUBE_USER` (assigné à moi)
- **C'est le mode recommandé pour "mes issues assignées"**
- Exemple : `sonarqube_issues()` ou `sonarqube_issues({})`

**AVEC PARAMÈTRES** (pour des cas avancés) :
- `project_key` : issues d'un projet spécifique
- `assignee` : filtrer par utilisateur assigné
- `file_path` : filtrer par fichier
- Tous les paramètres sont optionnels

#### Avantages

✅ **Plus simple** : Un seul outil au lieu de trois
✅ **Moins de confusion** : L'IA ne choisit plus le mauvais outil
✅ **Plus flexible** : Un outil qui s'adapte au contexte
✅ **Même comportement** : Par défaut = mes issues assignées

#### Impact sur le CLI

La commande `issues` a également été mise à jour :
- `python3 sonarqube_cli.py issues` → mes issues (utilise les env vars)
- `python3 sonarqube_cli.py issues <project_key>` → toutes les issues du projet
- `python3 sonarqube_cli.py issues <project_key> <assignee>` → issues filtrées
- `python3 sonarqube_cli.py my-issues` → toujours disponible (rétrocompatibilité)

#### Documentation mise à jour

- **README.md** : Nouvelle section sur le comportement intelligent de `issues`
- **QUICK_START.md** : Exemples simplifiés
- **GUIDE_UTILISATION.md** : Un seul outil à documenter
- **CHANGELOG.md** : Version 3.0.0 avec breaking changes
- **DIAGNOSTIC_v3.0.0.md** : Nouveau fichier explicatif

## [2.1.2] - 2025-10-09

### 🎯 Guidage IA renforcé

#### Problème résolu
- **L'IA choisissait le mauvais outil** : elle utilisait `sonarqube_issues` au lieu de `sonarqube_my_issues` pour "mes issues"
- **L'IA tentait de deviner** le `project_key` et se trompait (ex: "my-mobile-app" au lieu de "MyProject.Mobile.App")

#### Amélioré
- **Descriptions d'outils radicalement clarifiées** avec instructions explicites sur QUEL outil utiliser QUAND
- **`sonarqube_my_issues`** : 
  - Titre modifié en "MES ISSUES ASSIGNÉES" avec avertissements ⚠️
  - Indique OBLIGATOIREMENT quand l'utiliser ("mes issues", "mes problèmes", "ce qui m'est assigné")
  - Précise de ne JAMAIS utiliser `sonarqube_issues` pour les issues de l'utilisateur
- **`sonarqube_issues`** :
  - Titre modifié en "TOUTES LES ISSUES" avec avertissements ⚠️
  - Précise que c'est pour TOUTES les issues (pas seulement les miennes)
  - Liste explicitement les cas où il NE FAUT PAS l'utiliser
  - Redirige vers `sonarqube_my_issues` pour les issues de l'utilisateur
- **Alias simplifiés** : `show_my_issues` et `get_sonarqube_issues` avec descriptions claires

#### Impact
- ✅ **L'IA choisit le bon outil** pour "mes issues"
- ✅ **Pas de confusion** entre "mes issues" et "toutes les issues"
- ✅ **Pas de tentative de deviner** le `project_key` pour les issues personnelles

## [2.1.1] - 2025-10-09

### 🐛 Corrections critiques

#### Suppression du paramètre project_key de sonarqube_my_issues
- **BREAKING CHANGE** : `project_key` n'est plus accepté comme paramètre
- Les outils `sonarqube_my_issues` et `show_my_issues` n'ont maintenant AUCUN paramètre
- Utilisation obligatoire de SONARQUBE_PROJECT_KEY depuis l'environnement
- **Raison** : L'IA devinait incorrectement le project_key, causant des erreurs et des blocages

#### Amélioration de la robustesse
- Ajout de try-catch global renforcé dans `_call_tool()` pour garantir des réponses MCP valides
- Amélioration des messages d'erreur pour guider l'utilisateur vers la configuration correcte
- Logging déjà correctement configuré (stderr, pas stdout)

#### Documentation
- Clarification que SONARQUBE_PROJECT_KEY et SONARQUBE_USER sont REQUIS pour "mes issues"
- Ajout de troubleshooting pour les blocages et erreurs de configuration
- Mise à jour de tous les exemples CLI et des guides d'utilisation
- Note importante ajoutée dans README.md

## [2.1.0] - 2025-10-09

### 🎉 Nouveautés majeures

#### Conformité complète au protocole MCP
- Ajout des méthodes `initialize` et `initialized` pour l'initialisation correcte du serveur
- Correction du format des réponses `tools/list` et `resources/list` pour respecter le protocole MCP
- Les outils sont maintenant visibles dans Cursor Settings (9 outils à cette version, réduits à 7 en v3.0.0)
- Support complet de la découverte automatique des outils par l'assistant

#### Simplification de sonarqube_my_issues
- **BREAKING CHANGE** : Suppression du paramètre `assignee` de l'outil `sonarqube_my_issues`
- L'outil utilise maintenant **TOUJOURS** la variable d'environnement `SONARQUBE_USER`
- Plus de confusion : "mes issues" signifie automatiquement VOS issues
- Le paramètre `project_key` reste optionnel (défaut: SONARQUBE_PROJECT_KEY)
- Comportement 100% automatique sans paramètre requis

#### Amélioration des descriptions d'outils
- Descriptions enrichies avec émojis et cas d'usage clairs
- Exemples de prompts utilisateur inclus dans chaque description
- Note explicite : "Aucune installation requise" pour chaque outil
- Meilleure découvrabilité par l'assistant Cursor

#### Outils exposés
- `sonarqube_issues` : Récupère les issues d'un projet
- `sonarqube_my_issues` : Affiche VOS issues assignées (ZÉRO paramètre)
- `sonarqube_measures` : Métriques de qualité
- `sonarqube_hotspots` : Hotspots de sécurité
- `sonarqube_rule` : Détails d'une règle
- `sonarqube_users` : Recherche d'utilisateurs
- `sonarqube_quality_gate` : Statut du Quality Gate
- `show_my_issues` : Alias de sonarqube_my_issues
- `get_sonarqube_issues` : Alias de sonarqube_issues

#### Ressource exposée
- `sonarqube://project/MyProject` : Projet par défaut

### 📚 Documentation

- Nouveau fichier `QUICK_START.md` pour démarrage rapide
- Mise à jour de `README.md` avec nouveaux exemples
- Amélioration de `INSTALLATION.md` avec troubleshooting
- Nouveau fichier `GUIDE_UTILISATION.md` pour l'utilisation depuis un projet tiers

### 🔒 Améliorations techniques

- Logging configuré sur stderr (pas stdout) pour compatibilité MCP
- Support de SONARQUBE_USER dans toute la chaîne (config, CLI, MCP)
- Messages d'erreur plus clairs et informatifs
- Meilleure gestion des cas limites et des erreurs

## [2.0.0] - Date précédente

Versions antérieures à 2.1.0 (historique non documenté dans ce format)
