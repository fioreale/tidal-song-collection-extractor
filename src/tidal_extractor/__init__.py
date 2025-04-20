"""Tidal Song Collection Extractor."""

__version__ = "0.1.0"

from .auth import authenticate
from .collector import TidalCollector
from .core import TidalExtractor
from .formatter import TrackFormatter

__all__ = ["TidalExtractor", "authenticate", "TidalCollector", "TrackFormatter"]
