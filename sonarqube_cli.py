#!/usr/bin/env python3
"""
Interface CLI pour SonarQube MCP.

Permet de tester les commandes directement en ligne de commande.
"""

import sys
import argparse
import logging

# Reconfigure stdout/stderr to handle Unicode properly on Windows
# Only do this if we're in an interactive terminal, not when called via subprocess
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer') and sys.stdout.isatty():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from src.config import SonarQubeConfig
from src.api import SonarQubeAPI
from src.commands import CommandHandler


# Configuration du logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)


def print_help():
    """Affiche l'aide complète."""
    help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SonarQube MCP - Interface CLI                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage: python3 sonarqube_cli.py <commande> [arguments...]

📋 COMMANDES DISPONIBLES:

┌─ Issues ─────────────────────────────────────────────────────────────────────┐
│ issues <project_key> [file_path]                                            │
│ my-issues <project_key> <assignee>                                          │
│ mine [assignee]                         - Raccourci pour projet par défaut  │
│ issue-changelog <issue_key>                                                 │
│ issues-by-type <project_key> <type> [assignee]                             │
│ issues-by-severity <project_key> <severity> [assignee]                     │
│ bugs [project_key]                      - Raccourci pour BUG                │
│ vulnerabilities [project_key]           - Raccourci pour VULNERABILITY      │
│ code-smells [project_key]               - Raccourci pour CODE_SMELL         │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ Métriques ──────────────────────────────────────────────────────────────────┐
│ measures <project_key> [metric1,metric2,...]                                │
│ metrics <project_key> [metric1,metric2,...]    - Alias de measures          │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ Sécurité ───────────────────────────────────────────────────────────────────┐
│ hotspots <project_key> [status]                                             │
│ security-hotspots <project_key> [status]       - Alias de hotspots          │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ Projets ────────────────────────────────────────────────────────────────────┐
│ project-info <project_key>                                                  │
│ projects [search_term]                                                      │
│ quality-gate <project_key>                                                  │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ Utilisateurs ───────────────────────────────────────────────────────────────┐
│ users <search_term>                                                         │
│ search-users <search_term>              - Alias de users                    │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ Règles ─────────────────────────────────────────────────────────────────────┐
│ rule <rule_key>                                                             │
│ rules [search_term]                                                         │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ Système ────────────────────────────────────────────────────────────────────┐
│ health                                   - Vérifie la santé du serveur      │
│ version                                  - Version du serveur SonarQube     │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ Aide ───────────────────────────────────────────────────────────────────────┐
│ help [command]                           - Affiche l'aide                   │
│ commands                                 - Alias de help                    │
└──────────────────────────────────────────────────────────────────────────────┘

🔧 CONFIGURATION:

Variables d'environnement :
  SONARQUBE_URL          : URL du serveur SonarQube (requis)
  SONARQUBE_TOKEN        : Token d'authentification (requis)
  SONARQUBE_PROJECT_KEY  : Projet par défaut (optionnel)
  SONARQUBE_USER         : Utilisateur par défaut (optionnel)

Fichier de configuration :
  Utilisez --config <fichier.yaml> pour charger une configuration personnalisée.

📚 EXEMPLES:

  # Récupérer ses issues
  python3 sonarqube_cli.py my-issues MyProject developer-user

  # Métriques d'un projet
  python3 sonarqube_cli.py measures MyProject

  # Tous les bugs critiques
  python3 sonarqube_cli.py issues-by-severity MyProject CRITICAL

  # Hotspots de sécurité
  python3 sonarqube_cli.py hotspots MyProject

═══════════════════════════════════════════════════════════════════════════════
"""
    # Handle encoding for Windows console (cp1252) that can't display Unicode characters
    try:
        print(help_text)
    except (UnicodeEncodeError, AttributeError):
        # Fallback: encode to bytes with 'replace' error handling, then decode for safe printing
        encoding = getattr(sys.stdout, 'encoding', None) or 'utf-8'
        safe_text = help_text.encode(encoding, errors='replace').decode(encoding)
        print(safe_text)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description='Interface CLI pour SonarQube MCP',
        add_help=False
    )
    parser.add_argument(
        '--config',
        help='Fichier de configuration YAML',
        default=None
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mode verbeux'
    )
    parser.add_argument(
        'command',
        nargs='?',
        help='Commande à exécuter'
    )
    parser.add_argument(
        'args',
        nargs='*',
        help='Arguments de la commande'
    )
    
    args = parser.parse_args()
    
    # Configuration du logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Afficher l'aide si aucune commande
    if not args.command or args.command in ['help', '--help', '-h']:
        if not args.args:
            print_help()
            return 0
        # Aide pour une commande spécifique sera gérée par le handler
    
    try:
        # Initialiser la configuration
        config = SonarQubeConfig.from_env(config_file=args.config)
        
        # Initialiser l'API et le gestionnaire de commandes
        api = SonarQubeAPI(config)
        handler = CommandHandler(api, config)
        
        # Exécuter la commande
        result = handler.execute(args.command, args.args)
        
        # Afficher le résultat
        print(result.to_json())
        
        return 0 if result.success else 1
    
    except ValueError as e:
        # Handle Unicode encoding errors for Windows console
        try:
            print(f"Erreur de configuration: {e}", file=sys.stderr)
            print("\nAssurez-vous que les variables d'environnement sont définies:", file=sys.stderr)
            print("  export SONARQUBE_URL='https://sonarqube.example.com'", file=sys.stderr)
            print("  export SONARQUBE_TOKEN='votre_token'", file=sys.stderr)
        except (UnicodeEncodeError, AttributeError):
            # Fallback: encode error message with 'replace' to avoid crashes
            encoding = getattr(sys.stderr, 'encoding', None) or 'utf-8'
            error_msg = str(e).encode(encoding, errors='replace').decode(encoding)
            print(f"Erreur de configuration: {error_msg}", file=sys.stderr)
            print("\nAssurez-vous que les variables d'environnement sont definies:", file=sys.stderr)
            print("  export SONARQUBE_URL='https://sonarqube.example.com'", file=sys.stderr)
            print("  export SONARQUBE_TOKEN='votre_token'", file=sys.stderr)
        return 1
    
    except Exception as e:
        try:
            print(f"Erreur: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
        except (UnicodeEncodeError, AttributeError):
            # Fallback: encode error message with 'replace' to avoid crashes
            encoding = getattr(sys.stderr, 'encoding', None) or 'utf-8'
            error_msg = str(e).encode(encoding, errors='replace').decode(encoding)
            print(f"Erreur: {error_msg}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

