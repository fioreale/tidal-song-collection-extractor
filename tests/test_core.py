"""Unit tests for TidalExtractor core functionality."""

import unittest
from unittest.mock import MagicMock, patch

from src.tidal_extractor.core import TidalExtractor


class TestTidalExtractorInit(unittest.TestCase):
    """Test TidalExtractor initialization."""

    def test_init_default_silent(self):
        """Test initialization with default silent parameter."""
        extractor = TidalExtractor()

        self.assertIsNone(extractor.session)
        self.assertIsNone(extractor.collector)
        self.assertFalse(extractor.silent)

    def test_init_silent_true(self):
        """Test initialization with silent=True."""
        extractor = TidalExtractor(silent=True)

        self.assertIsNone(extractor.session)
        self.assertIsNone(extractor.collector)
        self.assertTrue(extractor.silent)


class TestTidalExtractorConnect(unittest.TestCase):
    """Test TidalExtractor connect method."""

    @patch("src.tidal_extractor.core.authenticate")
    @patch("src.tidal_extractor.core.TidalCollector")
    def test_connect_success(self, mock_collector_class, mock_authenticate):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_authenticate.return_value = mock_session

        mock_collector = MagicMock()
        mock_collector_class.return_value = mock_collector

        extractor = TidalExtractor(silent=True)
        result = extractor.connect()

        self.assertTrue(result)
        self.assertEqual(extractor.session, mock_session)
        self.assertEqual(extractor.collector, mock_collector)
        mock_authenticate.assert_called_once_with(silent=True)
        mock_collector_class.assert_called_once_with(mock_session, silent=True)

    @patch("src.tidal_extractor.core.authenticate")
    def test_connect_failure(self, mock_authenticate):
        """Test failed connection when authentication fails."""
        mock_authenticate.return_value = None

        extractor = TidalExtractor()
        result = extractor.connect()

        self.assertFalse(result)
        self.assertIsNone(extractor.session)
        self.assertIsNone(extractor.collector)


class TestTidalExtractorGetFavoriteTracks(unittest.TestCase):
    """Test TidalExtractor get_favorite_tracks method."""

    @patch("src.tidal_extractor.core.authenticate")
    @patch("src.tidal_extractor.core.TidalCollector")
    def test_get_favorite_tracks_with_existing_collector(
        self, mock_collector_class, mock_authenticate
    ):
        """Test getting favorite tracks with already connected collector."""
        mock_session = MagicMock()
        mock_authenticate.return_value = mock_session

        mock_collector = MagicMock()
        mock_collector.get_favorite_tracks.return_value = [
            {"id": 123, "title": "Song 1"}
        ]
        mock_collector_class.return_value = mock_collector

        extractor = TidalExtractor()
        extractor.connect()

        result = extractor.get_favorite_tracks()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 123)
        mock_collector.get_favorite_tracks.assert_called_once()

    @patch("src.tidal_extractor.core.authenticate")
    @patch("src.tidal_extractor.core.TidalCollector")
    def test_get_favorite_tracks_auto_connect(
        self, mock_collector_class, mock_authenticate
    ):
        """Test getting favorite tracks with auto-connect."""
        mock_session = MagicMock()
        mock_authenticate.return_value = mock_session

        mock_collector = MagicMock()
        mock_collector.get_favorite_tracks.return_value = [
            {"id": 123, "title": "Song 1"}
        ]
        mock_collector_class.return_value = mock_collector

        extractor = TidalExtractor()
        # Don't call connect() - should auto-connect
        result = extractor.get_favorite_tracks()

        self.assertEqual(len(result), 1)
        mock_authenticate.assert_called_once_with(silent=False)

    @patch("src.tidal_extractor.core.authenticate")
    def test_get_favorite_tracks_connect_fails(self, mock_authenticate):
        """Test getting favorite tracks when connection fails."""
        mock_authenticate.return_value = None

        extractor = TidalExtractor()
        result = extractor.get_favorite_tracks()

        self.assertEqual(result, [])


class TestTidalExtractorGetPlaylists(unittest.TestCase):
    """Test TidalExtractor get_playlists method."""

    @patch("src.tidal_extractor.core.authenticate")
    @patch("src.tidal_extractor.core.TidalCollector")
    def test_get_playlists_with_existing_collector(
        self, mock_collector_class, mock_authenticate
    ):
        """Test getting playlists with already connected collector."""
        mock_session = MagicMock()
        mock_authenticate.return_value = mock_session

        mock_collector = MagicMock()
        mock_collector.get_playlists.return_value = [
            {"id": "pl1", "name": "Playlist 1"}
        ]
        mock_collector_class.return_value = mock_collector

        extractor = TidalExtractor()
        extractor.connect()

        result = extractor.get_playlists()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "pl1")
        mock_collector.get_playlists.assert_called_once()

    @patch("src.tidal_extractor.core.authenticate")
    @patch("src.tidal_extractor.core.TidalCollector")
    def test_get_playlists_auto_connect(self, mock_collector_class, mock_authenticate):
        """Test getting playlists with auto-connect."""
        mock_session = MagicMock()
        mock_authenticate.return_value = mock_session

        mock_collector = MagicMock()
        mock_collector.get_playlists.return_value = [{"id": "pl1", "name": "Playlist 1"}]
        mock_collector_class.return_value = mock_collector

        extractor = TidalExtractor()
        result = extractor.get_playlists()

        self.assertEqual(len(result), 1)

    @patch("src.tidal_extractor.core.authenticate")
    def test_get_playlists_connect_fails(self, mock_authenticate):
        """Test getting playlists when connection fails."""
        mock_authenticate.return_value = None

        extractor = TidalExtractor()
        result = extractor.get_playlists()

        self.assertEqual(result, [])


class TestTidalExtractorGetPlaylistTracks(unittest.TestCase):
    """Test TidalExtractor get_playlist_tracks method."""

    @patch("src.tidal_extractor.core.authenticate")
    @patch("src.tidal_extractor.core.TidalCollector")
    def test_get_playlist_tracks_with_existing_collector(
        self, mock_collector_class, mock_authenticate
    ):
        """Test getting playlist tracks with already connected collector."""
        mock_session = MagicMock()
        mock_authenticate.return_value = mock_session

        mock_collector = MagicMock()
        mock_collector.get_playlist_tracks.return_value = [
            {"id": 123, "title": "Song 1"}
        ]
        mock_collector_class.return_value = mock_collector

        extractor = TidalExtractor()
        extractor.connect()

        result = extractor.get_playlist_tracks("pl1")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 123)
        mock_collector.get_playlist_tracks.assert_called_once_with("pl1")

    @patch("src.tidal_extractor.core.authenticate")
    @patch("src.tidal_extractor.core.TidalCollector")
    def test_get_playlist_tracks_auto_connect(
        self, mock_collector_class, mock_authenticate
    ):
        """Test getting playlist tracks with auto-connect."""
        mock_session = MagicMock()
        mock_authenticate.return_value = mock_session

        mock_collector = MagicMock()
        mock_collector.get_playlist_tracks.return_value = [
            {"id": 123, "title": "Song 1"}
        ]
        mock_collector_class.return_value = mock_collector

        extractor = TidalExtractor()
        result = extractor.get_playlist_tracks("pl1")

        self.assertEqual(len(result), 1)

    @patch("src.tidal_extractor.core.authenticate")
    def test_get_playlist_tracks_connect_fails(self, mock_authenticate):
        """Test getting playlist tracks when connection fails."""
        mock_authenticate.return_value = None

        extractor = TidalExtractor()
        result = extractor.get_playlist_tracks("pl1")

        self.assertEqual(result, [])


class TestTidalExtractorPrintTracks(unittest.TestCase):
    """Test TidalExtractor print_tracks method."""

    @patch("src.tidal_extractor.core.TrackFormatter.print_tracks_table")
    def test_print_tracks_not_silent(self, mock_print_table):
        """Test printing tracks when not in silent mode."""
        extractor = TidalExtractor(silent=False)
        tracks = [{"id": 123, "title": "Song 1"}]

        extractor.print_tracks(tracks, "My Tracks")

        mock_print_table.assert_called_once_with(tracks, "My Tracks")

    @patch("src.tidal_extractor.core.TrackFormatter.print_tracks_table")
    def test_print_tracks_silent(self, mock_print_table):
        """Test printing tracks when in silent mode."""
        extractor = TidalExtractor(silent=True)
        tracks = [{"id": 123, "title": "Song 1"}]

        extractor.print_tracks(tracks, "My Tracks")

        mock_print_table.assert_not_called()


class TestTidalExtractorSaveTracks(unittest.TestCase):
    """Test TidalExtractor save_tracks method."""

    @patch("src.tidal_extractor.core.TrackFormatter.save_tracks_to_file")
    def test_save_tracks_default_fields(self, mock_save):
        """Test saving tracks with default fields."""
        extractor = TidalExtractor()
        tracks = [{"id": 123, "title": "Song 1"}]

        extractor.save_tracks(tracks, "output.csv")

        mock_save.assert_called_once_with(tracks, "output.csv", None)

    @patch("src.tidal_extractor.core.TrackFormatter.save_tracks_to_file")
    def test_save_tracks_custom_fields(self, mock_save):
        """Test saving tracks with custom fields."""
        extractor = TidalExtractor()
        tracks = [{"id": 123, "title": "Song 1"}]

        extractor.save_tracks(tracks, "output.csv", ["id", "title"])

        mock_save.assert_called_once_with(tracks, "output.csv", ["id", "title"])


class TestTidalExtractorEmptyFavorites(unittest.TestCase):
    """Test TidalExtractor empty_favorites method."""

    @patch("src.tidal_extractor.core.authenticate")
    @patch("src.tidal_extractor.core.TidalCollector")
    def test_empty_favorites_success(self, mock_collector_class, mock_authenticate):
        """Test emptying favorites successfully."""
        mock_session = MagicMock()
        mock_authenticate.return_value = mock_session

        mock_collector = MagicMock()
        mock_collector.remove_all_favorite_tracks.return_value = True
        mock_collector_class.return_value = mock_collector

        extractor = TidalExtractor()
        extractor.connect()

        result = extractor.empty_favorites()

        self.assertTrue(result)
        mock_collector.remove_all_favorite_tracks.assert_called_once()

    @patch("src.tidal_extractor.core.authenticate")
    @patch("src.tidal_extractor.core.TidalCollector")
    def test_empty_favorites_auto_connect(
        self, mock_collector_class, mock_authenticate
    ):
        """Test emptying favorites with auto-connect."""
        mock_session = MagicMock()
        mock_authenticate.return_value = mock_session

        mock_collector = MagicMock()
        mock_collector.remove_all_favorite_tracks.return_value = True
        mock_collector_class.return_value = mock_collector

        extractor = TidalExtractor()
        result = extractor.empty_favorites()

        self.assertTrue(result)

    @patch("src.tidal_extractor.core.authenticate")
    def test_empty_favorites_connect_fails(self, mock_authenticate):
        """Test emptying favorites when connection fails."""
        mock_authenticate.return_value = None

        extractor = TidalExtractor()
        result = extractor.empty_favorites()

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
