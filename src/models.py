"""
Modèles de données pour les entités SonarQube.

Définit les structures de données pour Issues, Métriques, Règles, etc.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IssueType(str, Enum):
    """Types d'issues SonarQube."""
    BUG = "BUG"
    VULNERABILITY = "VULNERABILITY"
    CODE_SMELL = "CODE_SMELL"
    SECURITY_HOTSPOT = "SECURITY_HOTSPOT"


class Severity(str, Enum):
    """Niveaux de sévérité SonarQube."""
    BLOCKER = "BLOCKER"
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"


class HotspotStatus(str, Enum):
    """Statuts des hotspots de sécurité."""
    TO_REVIEW = "TO_REVIEW"
    REVIEWED = "REVIEWED"
    SAFE = "SAFE"


class IssueStatus(str, Enum):
    """Statuts des issues SonarQube."""
    OPEN = "OPEN"
    CONFIRMED = "CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    ACCEPTED = "ACCEPTED"
    FIXED = "FIXED"
    IN_SANDBOX = "IN_SANDBOX"


@dataclass
class TextRange:
    """Plage de texte pour localiser une issue dans le code."""
    start_line: int
    end_line: int
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None


@dataclass
class Issue:
    """
    Représente une issue SonarQube.
    
    Attributs principaux pour identifier et gérer une issue détectée
    par l'analyse de qualité du code.
    """
    key: str
    rule: str
    severity: Severity
    component: str
    message: str
    type: IssueType
    status: str
    line: Optional[int] = None
    text_range: Optional[TextRange] = None
    flows: List[Dict[str, Any]] = field(default_factory=list)
    effort: Optional[str] = None
    debt: Optional[str] = None
    assignee: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    creation_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Issue":
        """Crée une instance depuis une réponse API."""
        text_range = None
        if 'textRange' in data:
            tr = data['textRange']
            text_range = TextRange(
                start_line=tr['startLine'],
                end_line=tr['endLine'],
                start_offset=tr.get('startOffset'),
                end_offset=tr.get('endOffset')
            )
        
        return cls(
            key=data['key'],
            rule=data['rule'],
            severity=Severity(data['severity']),
            component=data['component'],
            message=data['message'],
            type=IssueType(data['type']),
            status=data['status'],
            line=data.get('line'),
            text_range=text_range,
            flows=data.get('flows', []),
            effort=data.get('effort'),
            debt=data.get('debt'),
            assignee=data.get('assignee'),
            author=data.get('author'),
            tags=data.get('tags', []),
            creation_date=data.get('creationDate'),
            update_date=data.get('updateDate'),
        )


@dataclass
class Measure:
    """Représente une métrique SonarQube."""
    metric: str
    value: Optional[str] = None
    best_value: Optional[bool] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Measure":
        """Crée une instance depuis une réponse API."""
        return cls(
            metric=data['metric'],
            value=data.get('value'),
            best_value=data.get('bestValue')
        )


@dataclass
class Component:
    """Représente un composant SonarQube (projet, fichier, etc.)."""
    key: str
    name: str
    qualifier: str
    measures: List[Measure] = field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Component":
        """Crée une instance depuis une réponse API."""
        measures = [
            Measure.from_api_response(m) 
            for m in data.get('measures', [])
        ]
        return cls(
            key=data['key'],
            name=data['name'],
            qualifier=data['qualifier'],
            measures=measures
        )


@dataclass
class Rule:
    """Représente une règle SonarQube."""
    key: str
    name: str
    lang: str
    type: str
    severity: Severity
    html_desc: Optional[str] = None
    markdown_desc: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Rule":
        """Crée une instance depuis une réponse API."""
        return cls(
            key=data['key'],
            name=data['name'],
            lang=data['lang'],
            type=data['type'],
            severity=Severity(data['severity']),
            html_desc=data.get('htmlDesc'),
            markdown_desc=data.get('mdDesc'),
            tags=data.get('tags', [])
        )


@dataclass
class Hotspot:
    """Représente un hotspot de sécurité SonarQube."""
    key: str
    component: str
    security_category: str
    vulnerability_probability: str
    status: HotspotStatus
    line: Optional[int] = None
    message: Optional[str] = None
    assignee: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Hotspot":
        """Crée une instance depuis une réponse API."""
        return cls(
            key=data['key'],
            component=data['component'],
            security_category=data['securityCategory'],
            vulnerability_probability=data['vulnerabilityProbability'],
            status=HotspotStatus(data['status']),
            line=data.get('line'),
            message=data.get('message'),
            assignee=data.get('assignee')
        )


@dataclass
class User:
    """Représente un utilisateur SonarQube."""
    login: str
    name: str
    email: Optional[str] = None
    active: bool = True
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "User":
        """Crée une instance depuis une réponse API."""
        return cls(
            login=data['login'],
            name=data['name'],
            email=data.get('email'),
            active=data.get('active', True)
        )


@dataclass
class Project:
    """Représente un projet SonarQube."""
    key: str
    name: str
    qualifier: str = "TRK"
    visibility: Optional[str] = None
    last_analysis_date: Optional[datetime] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Project":
        """Crée une instance depuis une réponse API."""
        return cls(
            key=data['key'],
            name=data['name'],
            qualifier=data.get('qualifier', 'TRK'),
            visibility=data.get('visibility'),
            last_analysis_date=data.get('lastAnalysisDate')
        )




