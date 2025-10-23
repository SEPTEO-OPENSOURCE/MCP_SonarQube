"""Utilitaires de validation et sécurité."""

import re
from pathlib import Path
from typing import Optional


class ValidationError(ValueError):
    """Erreur de validation d'input."""
    pass


def validate_file_path(path: str) -> str:
    """
    Valide un chemin de fichier pour éviter path traversal.
    
    Args:
        path: Chemin à valider
    
    Returns:
        Chemin validé et normalisé
    
    Raises:
        ValidationError: Si le chemin est invalide
    
    Examples:
        >>> validate_file_path("lib/main.dart")
        'lib/main.dart'
        >>> validate_file_path("../etc/passwd")
        ValidationError: Path traversal interdit (..)
    """
    if not path:
        raise ValidationError("Chemin vide")
    
    if path.startswith('/') or path.startswith('\\'):
        raise ValidationError("Chemins absolus interdits")
    
    if '..' in path:
        raise ValidationError("Path traversal interdit (..)")
    
    normalized = Path(path).as_posix()
    
    if re.search(r'[<>:"|?*]', normalized):
        raise ValidationError("Caractères invalides dans le chemin")
    
    return normalized


def validate_project_key(key: str) -> str:
    """
    Valide une clé de projet SonarQube.
    
    Args:
        key: Clé de projet à valider
    
    Returns:
        Clé validée
    
    Raises:
        ValidationError: Si la clé est invalide
    
    Examples:
        >>> validate_project_key("My.Project-Key_123")
        'My.Project-Key_123'
        >>> validate_project_key("bad!key")
        ValidationError: Clé de projet invalide
    """
    if not key:
        raise ValidationError("Clé de projet vide")
    
    if not re.match(r'^[a-zA-Z0-9._-]+$', key):
        raise ValidationError(
            f"Clé de projet invalide: '{key}'. "
            "Utilisez seulement lettres, chiffres, points, tirets, underscores."
        )
    
    if len(key) > 400:
        raise ValidationError("Clé de projet trop longue (max 400 caractères)")
    
    return key


def validate_rule_key(key: str) -> str:
    """
    Valide une clé de règle SonarQube (format: language:rule_id).
    
    Args:
        key: Clé de règle à valider
    
    Returns:
        Clé validée
    
    Raises:
        ValidationError: Si la clé est invalide
    
    Examples:
        >>> validate_rule_key("dart:S1192")
        'dart:S1192'
        >>> validate_rule_key("invalid")
        ValidationError: Format de règle invalide
    """
    if not key:
        raise ValidationError("Clé de règle vide")
    
    if ':' not in key:
        raise ValidationError(
            f"Format de règle invalide: '{key}'. "
            "Format attendu: 'language:rule_id' (ex: dart:S1192)"
        )
    
    language, rule_id = key.split(':', 1)
    if not language or not rule_id:
        raise ValidationError("Langue ou ID de règle vide")
    
    return key


def validate_user_login(login: str) -> str:
    """
    Valide un login utilisateur SonarQube.
    
    Args:
        login: Login à valider
    
    Returns:
        Login validé
    
    Raises:
        ValidationError: Si le login est invalide
    
    Examples:
        >>> validate_user_login("john.doe")
        'john.doe'
        >>> validate_user_login("john@<script>alert('xss')</script>")
        ValidationError: Caractères invalides dans le login
    """
    if not login:
        raise ValidationError("Login vide")
    
    # Caractères autorisés: lettres, chiffres, points, tirets, underscores, @
    if not re.match(r'^[a-zA-Z0-9._@-]+$', login):
        raise ValidationError(
            f"Login invalide: '{login}'. "
            "Utilisez seulement lettres, chiffres, points, tirets, underscores, @."
        )
    
    if len(login) > 255:
        raise ValidationError("Login trop long (max 255 caractères)")
    
    return login





