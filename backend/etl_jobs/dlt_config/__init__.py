"""
DLT configuration package for ETL pipeline.

This package contains:
- Type definitions for sources and destinations
- Factory functions for creating source and destination instances  
- Registry system for extensible pipeline components
"""

from .types import SourceType, DestinationType
from .factories import get_source_factory, get_destination_factory

__all__ = [
    "SourceType",
    "DestinationType", 
    "get_source_factory",
    "get_destination_factory"
]