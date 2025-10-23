"""Exemple de filtres avancés pour les issues."""

from src.config import SonarQubeConfig
from src.api import SonarQubeAPI
from src.models import IssueType, Severity

# Configuration
config = SonarQubeConfig.from_env()
api = SonarQubeAPI(config)

# Filtrer par type et sévérité
project_key = 'MonProjet'
bugs_critiques = api.issues.search(
    project_keys=[project_key],
    types=[IssueType.BUG],
    severities=[Severity.BLOCKER, Severity.CRITICAL],
    resolved=False
)

print(f"\n🐛 Bugs critiques à corriger: {len(bugs_critiques['issues'])}\n")

for issue in bugs_critiques['issues'][:10]:
    file_location = f" ({issue.component.split(':')[-1]})" if issue.component else ""
    print(f"  [{issue.severity.value}] {issue.message}{file_location}")





