"""
ML Components Package

This package initializes the AI/ML components for the FortiGate API client.
It has been updated to support the new, enhanced AI pipeline.
"""

# Canonical UserIntent dataclass, shared across components
from .user_intent import UserIntent

# Core components of the enhanced AI pipeline
from .enhanced_intent_classifier import classify_user_intent
from .ai_formatter import AIDataFormatter

# Natural Language Interface for interactive mode
from .natural_language_interface import NaturalLanguageInterface, interactive_session

__all__ = [
    'UserIntent',
    'classify_user_intent',
    'AIDataFormatter',
    'NaturalLanguageInterface',
    'interactive_session'
]
