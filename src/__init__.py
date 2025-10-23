"""
SonarQube MCP - Model Context Provider pour SonarQube

Un connecteur Python modulaire et propre pour intégrer SonarQube 
dans les IDEs alimentés par l'IA.
"""

__version__ = "4.0.0"
__author__ = "SonarQube MCP Contributors"

from .config import SonarQubeConfig
from .api import SonarQubeAPI
from .commands import CommandHandler

__all__ = [
    "SonarQubeConfig",
    "SonarQubeAPI", 
    "CommandHandler",
]




