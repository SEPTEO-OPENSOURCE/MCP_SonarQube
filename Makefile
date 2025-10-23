# Makefile pour SonarQube MCP

.PHONY: help install test lint format clean run-server run-cli

help:
	@echo "Commandes disponibles :"
	@echo "  make install      - Installer les dépendances"
	@echo "  make test         - Exécuter les tests"
	@echo "  make lint         - Vérifier le code (flake8, mypy)"
	@echo "  make format       - Formater le code (black)"
	@echo "  make clean        - Nettoyer les fichiers temporaires"
	@echo "  make run-server   - Lancer le serveur MCP"
	@echo "  make run-cli      - Lancer le CLI (avec ARGS)"
	@echo "  make coverage     - Générer le rapport de couverture"

install:
	pip install -r requirements.txt

test:
	pytest -v

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	mypy src/

format:
	black src/ tests/ *.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

run-server:
	python3 sonarqube_mcp_server.py

run-cli:
	python3 sonarqube_cli.py $(ARGS)

coverage:
	pytest --cov=src --cov-report=html
	@echo "Rapport de couverture généré dans htmlcov/index.html"

# Exemples d'utilisation du CLI
example-health:
	python3 sonarqube_cli.py health

example-mine:
	python3 sonarqube_cli.py mine

example-bugs:
	python3 sonarqube_cli.py bugs




