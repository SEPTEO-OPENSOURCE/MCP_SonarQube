# 🚀 Guide d'Installation - Serveur MCP SonarQube

Ce guide vous accompagne pas à pas pour installer et configurer le serveur MCP SonarQube avec Visual Studio Code.

---

## 📋 Table des matières

- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration SonarQube](#-configuration-sonarqube)
- [Configuration VS Code](#-configuration-vs-code)
- [Utilisation](#-utilisation)
- [Dépannage](#-dépannage)

---

## ✅ Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants :

| Outil | Version minimale | Lien de téléchargement |
|-------|------------------|------------------------|
| **Visual Studio Code** | Dernière version | [code.visualstudio.com](https://code.visualstudio.com/) |
| **Git** | 2.x | [git-scm.com](https://git-scm.com/) |
| **Python** | 3.8+ | [python.org](https://www.python.org/downloads/) |
| **pip** | Inclus avec Python | - |

### Vérification des installations

Ouvrez un terminal et vérifiez que tout est correctement installé :

```bash
# Vérifier Git
git --version

# Vérifier Python
python --version
# ou
python3 --version

# Vérifier pip
pip --version
# ou
pip3 --version
```

Si une de ces commandes ne fonctionnent pas, vérifiez l'installation et que les chemins des outils ont été rajoutés au PATH.
Vous pouvez également essayer d'utiliser le chemin complet vers ces outils si l'accès au PATH vous est impossible.

---

## 📦 Installation

### 1. Cloner le repository

Ouvrez un terminal et clonez le projet :

```bash
git clone https://github.com/SEPTEO-OPENSOURCE/MCP_SonarQube.git
cd SonarQubeMCP
```

### 2. Créer un environnement virtuel

**Sous Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Sous macOS/Linux :**
```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 Vous devriez voir `(venv)` apparaître au début de votre ligne de commande.

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Noter le chemin complet

Notez le chemin absolu de votre installation pour la configuration :

**Sous Windows :**
```bash
echo %CD%
# Exemple : C:\Users\username\workspace\SonarQubeMCP
```

**Sous macOS/Linux :**
```bash
pwd
# Exemple : /Users/username/workspace/SonarQubeMCP
```

---

## 🔐 Configuration SonarQube

### 1. Accéder à SonarQube

Connectez-vous à votre instance SonarQube :

```
https://votre-sonarqube-url.com
```

### 2. Générer un token d'authentification

1. Cliquez sur votre **avatar** en haut à droite
2. Sélectionnez **My Account**
3. Allez dans l'onglet **Security**
4. Dans la section **Generate Tokens** :
    - **Name** : `VSCode MCP Server` (ou un nom de votre choix)
    - **Type** : `User Token`
    - **Expires in** : Choisissez la durée de validité
5. Cliquez sur **Generate**
6. **⚠️ IMPORTANT** : Copiez immédiatement le token généré (il ne sera plus visible après)

> 💾 Conservez ce token dans un endroit sûr (gestionnaire de mots de passe recommandé).

### 3. Récupérer vos informations

Notez les informations suivantes :

| Information | Exemple | Où la trouver |
|-------------|---------|---------------|
| **URL SonarQube** | `https://sonarqube.example.com` | URL de connexion |
| **Token** | `squ_abc123...` | Token généré à l'étape précédente |
| **Username** | `john.doe` | Votre nom d'utilisateur SonarQube |

---

## ⚙️ Configuration VS Code

### 1. Ouvrir les paramètres VS Code

1. Ouvrez VS Code
2. Accédez aux paramètres :
    - **Windows/Linux** : `Ctrl + ,`
    - **macOS** : `Cmd + ,`
3. Cliquez sur l'icône **{}** en haut à droite pour ouvrir `settings.json`

### 2. Configurer le serveur MCP pour GitHub Copilot

Ajoutez ou modifiez la configuration suivante dans votre fichier `mcp.json` :

```json
{
  "servers": {
    "sonarqube": {
      "command": "C:\\Users\\<VOTRE_USERNAME>\\workspace\\SonarQubeMCP\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\<VOTRE_USERNAME>\\workspace\\SonarQubeMCP\\sonarqube_mcp_server.py"
      ],
      "env": {
        "SONARQUBE_QUALITY_AUDIENCE": "assistant",
        "SONARQUBE_QUALITY_PRIORITY": "0.8",
        "SONARQUBE_SECURITY_AUDIENCE": "assistant",
        "SONARQUBE_SECURITY_PRIORITY": "0.9",
        "SONARQUBE_METADATA_ENABLED": "true",
        "SONARQUBE_URL": "https://votre-sonarqube-url.com",
        "SONARQUBE_TOKEN": "votre_token_ici",
        "SONARQUBE_USER": "votre_username"
      }
    }
  }
}
```

Vous pourrez trouver ce fichier dans : %APPDATA%\Code\User\mcp.json

### 3. Personnaliser la configuration

Remplacez les valeurs suivantes :

| Placeholder | À remplacer par |
|-------------|-----------------|
| `<VOTRE_USERNAME>` | Votre nom d'utilisateur système |
| `https://votre-sonarqube-url.com` | L'URL de votre instance SonarQube |
| `votre_token_ici` | Le token généré précédemment |
| `votre_username` | Votre nom d'utilisateur SonarQube |

### 4. Configuration alternative (User settings.json)

Si vous préférez configurer au niveau utilisateur plutôt que workspace :

**Emplacement du fichier :**

- **Windows** : `%APPDATA%\Code\User\settings.json`
- **macOS** : `~/Library/Application Support/Code/User/settings.json`
- **Linux** : `~/.config/Code/User/settings.json`

Vous pouvez y accéder rapidement via :
1. `Ctrl/Cmd + Shift + P`
2. Tapez `Preferences: Open User Settings (JSON)`

### 5. Redémarrer VS Code

1. Fermez complètement VS Code
2. Relancez l'application

---

## 🎯 Utilisation

### Démarrer une conversation avec GitHub Copilot

1. Ouvrez VS Code
2. Ouvrez le panneau **GitHub Copilot Chat** :
    - **Windows/Linux** : `Ctrl + Shift + I`
    - **macOS** : `Cmd + Shift + I`

   Ou via la barre latérale en cliquant sur l'icône de chat

### Vérifier la connexion MCP

Dans le chat Copilot, tapez :

```
@workspace Peux-tu vérifier si le serveur SonarQube MCP est connecté ?
```

L'assistant devrait confirmer la connexion et lister les capacités disponibles.

### Utiliser le serveur MCP avec Copilot

Pour interroger explicitement le serveur SonarQube, vous pouvez :

**Option 1 - Via @workspace :**
```
@workspace Affiche-moi les problèmes de qualité du projet "mon-projet" depuis SonarQube
```

**Option 2 - Directement :**
```
Quelles sont les vulnérabilités de sécurité critiques détectées par SonarQube ?
```

**Option 3 - Avec contexte spécifique :**
```
Analyse les issues SonarQube du composant "backend-api" et propose des corrections
```

### Exemples de commandes avancées

```
Liste tous les projets SonarQube avec leur statut de qualité
```

```
Quels sont les bugs bloquants dans le projet "frontend" ?
```

```
Donne-moi un résumé des problèmes de sécurité pour l'équipe
```

```
Compare la qualité du code entre les projets "api-v1" et "api-v2"
```

---

## 🔧 Dépannage

### Le serveur MCP ne démarre pas

**Vérifiez les chemins :**

```bash
# Tester manuellement le serveur
cd /path/to/SonarQubeMCP
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
python sonarqube_mcp_server.py
```

**Vérifiez les logs dans VS Code :**
1. Menu **View** > **Output**
2. Sélectionnez **GitHub Copilot** dans le dropdown
3. Recherchez les erreurs liées à MCP

### GitHub Copilot ne reconnaît pas le serveur MCP

**Vérifiez que MCP est activé :**

1. Ouvrez les paramètres (`Ctrl/Cmd + ,`)
2. Recherchez `github.copilot.chat.mcp`
3. Assurez-vous que les options sont activées :
    - ✅ `github.copilot.chat.mcp.enabled`
    - ✅ `github.copilot.chat.mcp.autoStart`

**Redémarrez le service MCP :**

1. Ouvrez la palette de commandes (`Ctrl/Cmd + Shift + P`)
2. Tapez `Developer: Reload Window`

### Erreur d'authentification SonarQube

- ✅ Vérifiez que le token est valide et non expiré
- ✅ Vérifiez l'URL SonarQube (pas de slash `/` à la fin)
- ✅ Vérifiez votre nom d'utilisateur
- ✅ Testez la connexion manuellement :

```bash
curl -u votre_token: https://votre-sonarqube-url.com/api/system/status
```

### Le serveur se connecte mais Copilot ne répond pas

**Vérifiez la configuration JSON :**
- La syntaxe JSON est correcte (virgules, accolades)
- Les chemins utilisent les bons séparateurs (`\\` pour Windows, `/` pour macOS/Linux)
- Les chemins pointent vers les bons fichiers

**Testez avec une commande simple :**
```
Que peux-tu faire avec SonarQube ?
```

### 4. Personnaliser la configuration

Remplacez les valeurs suivantes :

| Placeholder | À remplacer par |
|-------------|-----------------|
| `<VOTRE_USERNAME>` | Votre nom d'utilisateur système |
| `https://votre-sonarqube-url.com` | L'URL de votre instance SonarQube |
| `votre_token_ici` | Le token généré précédemment |
| `votre_username` | Votre nom d'utilisateur SonarQube |

### 5. Redémarrer VS Code

1. Fermez complètement VS Code
2. Relancez l'application

---

## 🎯 Utilisation

### Démarrer une conversation avec l'agent

1. Ouvrez VS Code
2. Ouvrez la palette de commandes (Ctrl+Shift+P / Cmd+Shift+P)
3. Tapez **"Cline: Open Chat"** et appuyez sur Entrée
4. Une nouvelle fenêtre de chat s'ouvre sur le côté

### Vérifier la connexion MCP

Dans le chat Cline, tapez :

```
Peux-tu vérifier si le serveur SonarQube MCP est connecté ?
```

L'assistant devrait confirmer la connexion et lister les capacités disponibles.

### Exemples de commandes

```
Affiche-moi les problèmes de qualité du projet "mon-projet"
```

```
Quelles sont les vulnérabilités de sécurité critiques ?
```

```
Donne-moi un résumé de l'état de qualité de tous les projets
```

---

## 🔧 Dépannage

### Le serveur MCP ne démarre pas

**Vérifiez les chemins :**

```bash
# Tester manuellement le serveur
cd /path/to/SonarQubeMCP
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
python sonarqube_mcp_server.py
```

### Erreur d'authentification SonarQube

- ✅ Vérifiez que le token est valide et non expiré
- ✅ Vérifiez l'URL SonarQube (pas de slash `/` à la fin)
- ✅ Vérifiez votre nom d'utilisateur

### Le serveur se connecte mais ne répond pas

Vérifiez les logs dans VS Code :
1. Menu **View** > **Output**
2. Sélectionnez **Cline** dans le dropdown

### Variables d'environnement

Les priorités et audiences peuvent être ajustées :

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `SONARQUBE_QUALITY_PRIORITY` | Priorité des issues qualité | `0.8` |
| `SONARQUBE_SECURITY_PRIORITY` | Priorité des issues sécurité | `0.9` |
| `SONARQUBE_QUALITY_AUDIENCE` | Audience pour issues qualité | `assistant` |
| `SONARQUBE_SECURITY_AUDIENCE` | Audience pour issues sécurité | `assistant` |
| `SONARQUBE_METADATA_ENABLED` | Activer les métadonnées | `true` |

**🎉 Félicitations ! Votre serveur MCP SonarQube est maintenant opérationnel.**