"""Exemple de dashboard de métriques simple."""

from src.config import SonarQubeConfig
from src.api import SonarQubeAPI

# Configuration
config = SonarQubeConfig.from_env()
api = SonarQubeAPI(config)

# Récupérer les métriques
project_key = 'MonProjet'
component = api.measures.get_component(project_key)

print(f"\n📊 Métriques de qualité - {component.name}\n" + "=" * 60)

for measure in component.measures:
    print(f"{measure.metric.ljust(30)}: {measure.value}")

print("=" * 60)





