"""Tests pour les modèles de données."""

import pytest
from datetime import datetime

from src.models import (
    Issue, IssueType, Severity, TextRange,
    Measure, Component, Rule, Hotspot, HotspotStatus,
    User, Project
)


class TestIssue:
    """Tests pour le modèle Issue."""
    
    def test_issue_from_api_response(self):
        """Test la création depuis une réponse API."""
        data = {
            'key': 'issue-123',
            'rule': 'dart:S1192',
            'severity': 'MAJOR',
            'component': 'project:file.dart',
            'message': 'Test message',
            'type': 'CODE_SMELL',
            'status': 'OPEN',
            'line': 42,
            'textRange': {
                'startLine': 42,
                'endLine': 42,
                'startOffset': 10,
                'endOffset': 20
            },
            'effort': '5min',
            'assignee': 'user1',
            'tags': ['test', 'example']
        }
        
        issue = Issue.from_api_response(data)
        
        assert issue.key == 'issue-123'
        assert issue.rule == 'dart:S1192'
        assert issue.severity == Severity.MAJOR
        assert issue.type == IssueType.CODE_SMELL
        assert issue.line == 42
        assert issue.text_range is not None
        assert issue.text_range.start_line == 42
        assert issue.effort == '5min'
        assert issue.assignee == 'user1'
        assert len(issue.tags) == 2


class TestMeasure:
    """Tests pour le modèle Measure."""
    
    def test_measure_from_api_response(self):
        """Test la création depuis une réponse API."""
        data = {
            'metric': 'ncloc',
            'value': '1000',
            'bestValue': False
        }
        
        measure = Measure.from_api_response(data)
        
        assert measure.metric == 'ncloc'
        assert measure.value == '1000'
        assert measure.best_value is False


class TestComponent:
    """Tests pour le modèle Component."""
    
    def test_component_from_api_response(self):
        """Test la création depuis une réponse API."""
        data = {
            'key': 'project-key',
            'name': 'Project Name',
            'qualifier': 'TRK',
            'measures': [
                {'metric': 'ncloc', 'value': '1000'},
                {'metric': 'coverage', 'value': '80.5'}
            ]
        }
        
        component = Component.from_api_response(data)
        
        assert component.key == 'project-key'
        assert component.name == 'Project Name'
        assert len(component.measures) == 2
        assert component.measures[0].metric == 'ncloc'


class TestRule:
    """Tests pour le modèle Rule."""
    
    def test_rule_from_api_response(self):
        """Test la création depuis une réponse API."""
        data = {
            'key': 'dart:S1192',
            'name': 'String literals should not be duplicated',
            'lang': 'dart',
            'type': 'CODE_SMELL',
            'severity': 'CRITICAL',
            'htmlDesc': '<p>Test description</p>',
            'tags': ['brain-overload', 'design']
        }
        
        rule = Rule.from_api_response(data)
        
        assert rule.key == 'dart:S1192'
        assert rule.name == 'String literals should not be duplicated'
        assert rule.lang == 'dart'
        assert rule.severity == Severity.CRITICAL
        assert len(rule.tags) == 2


class TestHotspot:
    """Tests pour le modèle Hotspot."""
    
    def test_hotspot_from_api_response(self):
        """Test la création depuis une réponse API."""
        data = {
            'key': 'hotspot-123',
            'component': 'project:file.dart',
            'securityCategory': 'sql-injection',
            'vulnerabilityProbability': 'HIGH',
            'status': 'TO_REVIEW',
            'line': 42,
            'message': 'Potential SQL injection',
            'assignee': 'user1'
        }
        
        hotspot = Hotspot.from_api_response(data)
        
        assert hotspot.key == 'hotspot-123'
        assert hotspot.security_category == 'sql-injection'
        assert hotspot.vulnerability_probability == 'HIGH'
        assert hotspot.status == HotspotStatus.TO_REVIEW
        assert hotspot.line == 42


class TestUser:
    """Tests pour le modèle User."""
    
    def test_user_from_api_response(self):
        """Test la création depuis une réponse API."""
        data = {
            'login': 'user1',
            'name': 'User One',
            'email': 'user1@example.com',
            'active': True
        }
        
        user = User.from_api_response(data)
        
        assert user.login == 'user1'
        assert user.name == 'User One'
        assert user.email == 'user1@example.com'
        assert user.active is True


class TestProject:
    """Tests pour le modèle Project."""
    
    def test_project_from_api_response(self):
        """Test la création depuis une réponse API."""
        data = {
            'key': 'project-key',
            'name': 'Project Name',
            'qualifier': 'TRK',
            'visibility': 'private',
            'lastAnalysisDate': '2023-10-01T12:00:00+0000'
        }
        
        project = Project.from_api_response(data)
        
        assert project.key == 'project-key'
        assert project.name == 'Project Name'
        assert project.qualifier == 'TRK'
        assert project.visibility == 'private'




