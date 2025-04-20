"""Core functionality for Tidal Extractor."""

from typing import Any, Dict, List

from .auth import authenticate
from .collector import TidalCollector
from .formatter import TrackFormatter


class TidalExtractor:
    """Main class for extracting data from Tidal."""

    def __init__(self, silent: bool = False):
        """Initialize the extractor.

        Args:
            silent: If True, suppress console output
        """
        self.session = None
        self.collector = None
        self.silent = silent

    def connect(self) -> bool:
        """Connect to Tidal API.

        Returns:
            bool: True if connection successful, False otherwise
        """
        self.session = authenticate(silent=self.silent)
        if self.session:
            self.collector = TidalCollector(self.session, silent=self.silent)
            return True
        return False

    def get_favorite_tracks(self) -> List[Dict[str, Any]]:
        """Get user's favorite tracks.

        Returns:
            List of track dictionaries
        """
        if not self.collector:
            if not self.connect():
                return []

        return self.collector.get_favorite_tracks()

    def get_playlists(self) -> List[Dict[str, Any]]:
        """Get user's playlists.

        Returns:
            List of playlist dictionaries
        """
        if not self.collector:
            if not self.connect():
                return []

        return self.collector.get_playlists()

    def get_playlist_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
        """Get tracks from a specific playlist.

        Args:
            playlist_id: ID of the playlist

        Returns:
            List of track dictionaries
        """
        if not self.collector:
            if not self.connect():
                return []

        return self.collector.get_playlist_tracks(playlist_id)

    def print_tracks(self, tracks: List[Dict[str, Any]], title: str = "Tracks") -> None:
        """Print tracks to console.

        Args:
            tracks: List of track dictionaries
            title: Table title
        """
        if not self.silent:
            TrackFormatter.print_tracks_table(tracks, title)

    def save_tracks(
        self, tracks: List[Dict[str, Any]], filename: str, format_type: str = "simple"
    ) -> None:
        """Save tracks to a file.

        Args:
            tracks: List of track dictionaries
            filename: Output filename
            format_type: Format type ('simple', 'detailed')
        """
        TrackFormatter.save_tracks_to_file(tracks, filename, format_type)
