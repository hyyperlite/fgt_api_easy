#!/usr/bin/env python3
"""
Defines the canonical UserIntent dataclass for the AI/ML pipeline.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class UserIntent:
    """
    A structured representation of a user's command, classified by the AI.
    """
    original_query: str = ""
    method: str = "get"
    endpoint: str = ""
    format_type: str = "auto"
    output_style: str = "default"
    requested_fields: List[str] = field(default_factory=list)
    filter_conditions: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    endpoint_confidence: float = 0.0
    format_confidence: float = 0.0
    field_confidence: float = 0.0
    filter_confidence: float = 0.0
