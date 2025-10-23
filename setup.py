"""Configuration d'installation pour SonarQube MCP."""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Lire les requirements
requirements = (this_directory / "requirements.txt").read_text(encoding='utf-8').splitlines()
# Filtrer les commentaires et lignes vides
requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name="sonarqube-mcp",
    version="2.0.0",
    author="SonarQube MCP Contributors",
    description="Model Context Provider pour SonarQube - Intégration propre et modulaire",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SEPTEO-OPENSOURCE/MCP_SonarQube.git",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.11.1',
            'black>=23.7.0',
            'flake8>=6.1.0',
            'mypy>=1.5.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'sonarqube-cli=sonarqube_cli:main',
            'sonarqube-mcp=sonarqube_mcp_server:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)




