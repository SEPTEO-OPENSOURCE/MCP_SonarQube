"""Exemple d'utilisation basique du client API SonarQube."""

from src.config import SonarQubeConfig
from src.api import SonarQubeAPI

# Configuration depuis environnement
config = SonarQubeConfig.from_env()
api = SonarQubeAPI(config)

# Récupérer mes issues
issues = api.issues.search(
    project_keys=['MonProjet'],
    assignees=['mon-login'],
    resolved=False
)

print(f"Vous avez {len(issues['issues'])} issues à résoudre:")
for issue in issues['issues'][:5]:
    print(f"  - {issue.rule}: {issue.message} ({issue.severity})")





