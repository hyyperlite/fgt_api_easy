"""
ML Components for FortiGate API Client

This package provides machine learning capabilities for intelligent data processing,
context classification, and natural language querying of FortiGate API responses.

All ML operations are performed locally without external API calls to ensure data privacy.
"""

from .context_classifier import EndpointContextClassifier
from .display_optimizer import IntelligentDisplayEngine
from .query_processor import QueryProcessor
from .model_trainer import MLModelTrainer

__all__ = [
    'EndpointContextClassifier',
    'IntelligentDisplayEngine', 
    'QueryProcessor',
    'MLModelTrainer'
]
