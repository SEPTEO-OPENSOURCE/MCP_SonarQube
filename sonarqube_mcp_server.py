#!/usr/bin/env python3
"""
Point d'entrée du serveur MCP SonarQube.

Implémente le Model Context Protocol pour exposer les fonctionnalités
SonarQube aux IDE alimentés par l'IA.
"""

import sys
import logging
import os
import re
from pathlib import Path
from datetime import datetime

from src.config import SonarQubeConfig
from src.mcp import MCPServer


class TokenSanitizingFilter(logging.Filter):
    """Filtre pour masquer les tokens sensibles dans les logs."""
    
    SENSITIVE_PATTERNS = [
        # Pattern 1: token="value" ou token: value
        (r'(token|authorization|password|secret|api[_-]?key)["\']?\s*[:=]\s*["\']?([^"\'\s]{10,})["\']?', 
         r'\1: ***MASKED***'),
        # Pattern 2: Bearer tokens
        (r'Bearer\s+([^\s]{20,})', r'Bearer ***MASKED***'),
        # Pattern 3: SonarQube tokens (format squ_...)
        (r'squ_[a-f0-9]{40}', r'squ_***MASKED***'),
        # Pattern 4: Auth headers (capture tout après "Authorization:")
        (r'(Authorization:\s+)(.+)', r'\1***MASKED***'),
    ]
    
    def filter(self, record):
        """Masque les tokens dans le message de log."""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            msg = record.msg
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
            record.msg = msg
        
        # Masquer aussi dans args si présents
        if hasattr(record, 'args') and record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in self.SENSITIVE_PATTERNS:
                        arg = re.sub(pattern, replacement, arg, flags=re.IGNORECASE)
                sanitized_args.append(arg)
            record.args = tuple(sanitized_args)
        
        return True


def setup_logging():
    """Configure le logging de manière portable et sécurisée."""
    log_dir = Path(os.getenv('SONARQUBE_LOG_DIR', 
                              str(Path.home() / '.sonarqube_mcp' / 'logs')))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"sonarqube_mcp_{datetime.now():%Y%m%d}.log"
    log_level = os.getenv('SONARQUBE_LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr)
        ]
    )
    return log_file


def apply_token_filter():
    """Applique le filtre de sanitization à tous les handlers."""
    token_filter = TokenSanitizingFilter()
    for handler in logging.root.handlers:
        handler.addFilter(token_filter)


# Configuration du logging
log_file_path = setup_logging()
apply_token_filter()
logger = logging.getLogger(__name__)
logger.info(f"Logs écrits dans: {log_file_path}")


def main():
    """Point d'entrée principal du serveur MCP."""
    try:
        logger.info("Démarrage du serveur MCP SonarQube v4.0.0")
        
        # Charger la configuration
        config = SonarQubeConfig.from_env()
        
        # Créer et lancer le serveur
        server = MCPServer(config)
        server.run()
    
    except Exception as e:
        logger.error(f"Impossible de démarrer le serveur: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
