#!/usr/bin/env python3
"""
Script de diagnostic pour SonarQube MCP.

Vérifie toute la configuration et identifie les problèmes.
"""

import os
import sys
import requests
from pathlib import Path

# Couleurs pour le terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def check_mark(condition):
    return f"{GREEN}✓{RESET}" if condition else f"{RED}✗{RESET}"

def print_section(title):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_result(name, status, value="", note=""):
    status_icon = check_mark(status)
    print(f"{status_icon} {name}: ", end="")
    if value:
        if status:
            print(f"{GREEN}{value}{RESET}", end="")
        else:
            print(f"{RED}{value}{RESET}", end="")
    if note:
        print(f" {YELLOW}({note}){RESET}", end="")
    print()

def main():
    print(f"\n{BLUE}╔═══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║     Diagnostic SonarQube MCP - Vérification complète      ║{RESET}")
    print(f"{BLUE}╚═══════════════════════════════════════════════════════════╝{RESET}")
    
    all_ok = True
    
    # 1. Vérification des variables d'environnement
    print_section("1. Variables d'environnement")
    
    url = os.getenv('SONARQUBE_URL')
    token = os.getenv('SONARQUBE_TOKEN')
    project_key = os.getenv('SONARQUBE_PROJECT_KEY')
    
    url_ok = bool(url)
    token_ok = bool(token)
    
    print_result("SONARQUBE_URL", url_ok, url or "NON DÉFINIE")
    print_result("SONARQUBE_TOKEN", token_ok, 
                f"{'***' + token[-6:] if token and len(token) > 6 else 'NON DÉFINIE'}")
    print_result("SONARQUBE_PROJECT_KEY", bool(project_key), 
                project_key or "Non définie", "optionnel")
    
    if not url_ok:
        all_ok = False
        print(f"\n{RED}⚠️  SONARQUBE_URL non définie !{RESET}")
        print(f"{YELLOW}Solution:{RESET}")
        print(f"  export SONARQUBE_URL=\"https://sonarqube.example.com\"")
    
    if not token_ok:
        all_ok = False
        print(f"\n{RED}⚠️  SONARQUBE_TOKEN non défini !{RESET}")
        print(f"{YELLOW}Solution:{RESET}")
        print(f"  export SONARQUBE_TOKEN=\"votre_token_ici\"")
        return
    
    # 2. Vérification de l'installation Python
    print_section("2. Installation Python")
    
    try:
        import requests
        requests_ok = True
        print_result("Module requests", True, requests.__version__)
    except ImportError:
        requests_ok = False
        all_ok = False
        print_result("Module requests", False, "NON INSTALLÉ")
        print(f"{YELLOW}Solution: pip install requests{RESET}")
        return
    
    try:
        import yaml
        yaml_ok = True
        print_result("Module PyYAML", True, yaml.__version__)
    except ImportError:
        yaml_ok = True  # Optionnel
        print_result("Module PyYAML", True, "Non installé", "optionnel")
    
    # 3. Vérification de la structure du projet
    print_section("3. Structure du projet")
    
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    structure_checks = [
        ("Répertoire src/", src_dir.exists()),
        ("src/__init__.py", (src_dir / "__init__.py").exists()),
        ("src/config.py", (src_dir / "config.py").exists()),
        ("src/api.py", (src_dir / "api.py").exists()),
        ("src/models.py", (src_dir / "models.py").exists()),
        ("src/commands.py", (src_dir / "commands.py").exists()),
        ("sonarqube_mcp_server.py", (project_root / "sonarqube_mcp_server.py").exists()),
        ("sonarqube_cli.py", (project_root / "sonarqube_cli.py").exists()),
    ]
    
    for name, exists in structure_checks:
        print_result(name, exists, "Présent" if exists else "MANQUANT")
        if not exists:
            all_ok = False
    
    # 4. Test de connexion au serveur SonarQube
    print_section("4. Test de connexion SonarQube")
    
    if not url or not token:
        print(f"{RED}Impossible de tester sans URL et TOKEN{RESET}")
        return
    
    # Normaliser l'URL
    url_clean = url.rstrip('/')
    
    # Test 1: Ping simple (sans authentification)
    print(f"\n{BLUE}Test 1: Connexion au serveur...{RESET}")
    try:
        response = requests.get(f"{url_clean}/api/system/status", timeout=10)
        server_reachable = response.status_code in [200, 401, 403]
        print_result("Serveur accessible", server_reachable, 
                    f"Code {response.status_code}")
    except requests.exceptions.RequestException as e:
        server_reachable = False
        all_ok = False
        print_result("Serveur accessible", False, f"Erreur: {str(e)}")
        return
    
    # Test 2: Authentification
    print(f"\n{BLUE}Test 2: Authentification...{RESET}")
    try:
        response = requests.get(
            f"{url_clean}/api/authentication/validate",
            auth=(token, ''),
            timeout=10
        )
        auth_ok = response.status_code == 200
        
        if auth_ok:
            try:
                data = response.json()
                print_result("Authentification", True, "Valide")
                if 'valid' in data:
                    print(f"  → Valid: {GREEN}{data['valid']}{RESET}")
            except:
                print_result("Authentification", True, "Réponse reçue")
        else:
            all_ok = False
            print_result("Authentification", False, 
                        f"Code {response.status_code}")
            if response.status_code == 401:
                print(f"{RED}  → Token invalide ou expiré{RESET}")
            elif response.status_code == 403:
                print(f"{RED}  → Token refusé (permissions insuffisantes ?){RESET}")
            
            print(f"\n{YELLOW}Actions à faire :{RESET}")
            print(f"  1. Vérifier votre token sur https://sonarqube.example.com")
            print(f"  2. Mon compte → Sécurité → Tokens")
            print(f"  3. Générer un nouveau token si nécessaire")
            return
    
    except requests.exceptions.RequestException as e:
        all_ok = False
        print_result("Authentification", False, f"Erreur: {str(e)}")
        return
    
    # Test 3: API Projects (test simple)
    print(f"\n{BLUE}Test 3: Accès à l'API Projects...{RESET}")
    try:
        response = requests.get(
            f"{url_clean}/api/projects/search",
            auth=(token, ''),
            params={'ps': 1},
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                project_count = data.get('paging', {}).get('total', 0)
                print_result("API Projects", True, 
                            f"{project_count} projet(s) accessible(s)")
            except:
                print_result("API Projects", True, "Accessible")
        else:
            print_result("API Projects", False, f"Code {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print_result("API Projects", False, f"Erreur: {str(e)}")
    
    # Test 4: Projet spécifique si défini
    if project_key:
        print(f"\n{BLUE}Test 4: Accès au projet '{project_key}'...{RESET}")
        try:
            response = requests.get(
                f"{url_clean}/api/projects/search",
                auth=(token, ''),
                params={'projects': project_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                components = data.get('components', [])
                if components:
                    project = components[0]
                    print_result("Projet trouvé", True, project.get('name', project_key))
                    print(f"  → Clé: {project.get('key')}")
                    print(f"  → Visibilité: {project.get('visibility', 'N/A')}")
                    
                    # Test des issues du projet
                    print(f"\n{BLUE}Test 5: Issues du projet...{RESET}")
                    response = requests.get(
                        f"{url_clean}/api/issues/search",
                        auth=(token, ''),
                        params={'componentKeys': project_key, 'resolved': 'false', 'ps': 1},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        issue_count = data.get('total', 0)
                        print_result("Issues accessibles", True, 
                                    f"{issue_count} issue(s)")
                    else:
                        print_result("Issues accessibles", False, 
                                    f"Code {response.status_code}")
                else:
                    print_result("Projet trouvé", False, "Projet non trouvé ou non accessible")
            else:
                print_result("Projet trouvé", False, f"Code {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print_result("Projet accessible", False, f"Erreur: {str(e)}")
    
    # Résumé final
    print_section("Résumé")
    
    if all_ok and auth_ok:
        print(f"\n{GREEN}✓ Tous les tests sont passés !{RESET}")
        print(f"\n{GREEN}Le MCP SonarQube est correctement configuré et fonctionnel.{RESET}")
        print(f"\nVous pouvez maintenant utiliser:")
        print(f"  • CLI: python3 sonarqube_cli.py <commande>")
        print(f"  • MCP dans Cursor")
        
        print(f"\n{BLUE}Commandes de test :{RESET}")
        print(f"  python3 sonarqube_cli.py projects")
        if project_key:
            print(f"  python3 sonarqube_cli.py issues {project_key}")
            print(f"  python3 sonarqube_cli.py project-info {project_key}")
    else:
        print(f"\n{RED}✗ Des problèmes ont été détectés.{RESET}")
        print(f"\n{YELLOW}Consultez les messages ci-dessus pour les résoudre.{RESET}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

