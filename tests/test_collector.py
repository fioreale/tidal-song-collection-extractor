"""Unit tests for TidalCollector class."""

import unittest
from unittest.mock import MagicMock, patch

from src.tidal_extractor.collector import TidalCollector


class MockTrack:
    """Mock Tidal track object."""

    def __init__(self, track_id, name, artists, album_name=None, duration=None):
        self.id = track_id
        self.name = name
        self.artists = [MockArtist(artist) for artist in artists]
        self.album = MockAlbum(album_name) if album_name else None
        self.duration = duration


class MockArtist:
    """Mock Tidal artist object."""

    def __init__(self, name):
        self.name = name


class MockAlbum:
    """Mock Tidal album object."""

    def __init__(self, name):
        self.name = name


class MockPlaylist:
    """Mock Tidal playlist object."""

    def __init__(self, playlist_id, name, description=""):
        self.id = playlist_id
        self.name = name
        self.description = description

    def add(self, track_ids):
        """Mock add method."""
        pass


class MockFavorites:
    """Mock Tidal favorites object."""

    def __init__(self, tracks):
        self._tracks = tracks
        self.remove_track = MagicMock()

    def tracks(self):
        """Return mock tracks."""
        return self._tracks


class TestTidalCollector(unittest.TestCase):
    """Test TidalCollector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock()
        self.mock_user = MagicMock()
        self.mock_session.user = self.mock_user
        self.collector = TidalCollector(self.mock_session, silent=True)

    def test_init(self):
        """Test TidalCollector initialization."""
        self.assertEqual(self.collector.session, self.mock_session)
        self.assertEqual(self.collector.user, self.mock_user)
        self.assertTrue(self.collector.silent)

    def test_get_favorite_tracks_silent_mode(self):
        """Test getting favorite tracks in silent mode."""
        # Create mock tracks
        mock_tracks = [
            MockTrack(123, "Song 1", ["Artist A"], "Album 1", 180),
            MockTrack(456, "Song 2", ["Artist B", "Artist C"], "Album 2", 240),
        ]

        # Mock favorites
        mock_favorites = MockFavorites(mock_tracks)
        self.mock_user.favorites = mock_favorites

        # Get favorite tracks
        result = self.collector.get_favorite_tracks()

        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 123)
        self.assertEqual(result[0]["title"], "Song 1")
        self.assertEqual(result[0]["artists"], ["Artist A"])
        self.assertEqual(result[0]["album"], "Album 1")
        self.assertEqual(result[0]["duration"], 180)

        self.assertEqual(result[1]["id"], 456)
        self.assertEqual(result[1]["title"], "Song 2")
        self.assertEqual(result[1]["artists"], ["Artist B", "Artist C"])
        self.assertEqual(result[1]["album"], "Album 2")
        self.assertEqual(result[1]["duration"], 240)

    def test_get_favorite_tracks_missing_album(self):
        """Test getting favorite tracks with missing album info."""
        # Create mock track without album
        mock_tracks = [MockTrack(123, "Song 1", ["Artist A"], None, 180)]

        mock_favorites = MockFavorites(mock_tracks)
        self.mock_user.favorites = mock_favorites

        result = self.collector.get_favorite_tracks()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["album"], "Unknown")

    def test_get_favorite_tracks_missing_duration(self):
        """Test getting favorite tracks with missing duration."""
        # Create mock track without duration
        mock_track = MockTrack(123, "Song 1", ["Artist A"], "Album 1", None)
        # Remove duration attribute
        delattr(mock_track, "duration")

        mock_favorites = MockFavorites([mock_track])
        self.mock_user.favorites = mock_favorites

        result = self.collector.get_favorite_tracks()

        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["duration"])

    @patch("src.tidal_extractor.collector.Progress")
    def test_get_favorite_tracks_not_silent(self, mock_progress_class):
        """Test getting favorite tracks in non-silent mode (with Progress bar)."""
        mock_tracks = [
            MockTrack(123, "Song 1", ["Artist A"], "Album 1", 180),
            MockTrack(456, "Song 2", ["Artist B"], "Album 2", 240),
        ]

        mock_favorites = MockFavorites(mock_tracks)
        self.mock_user.favorites = mock_favorites

        # Create non-silent collector
        collector = TidalCollector(self.mock_session, silent=False)

        # Mock Progress context manager
        mock_progress = MagicMock()
        mock_progress_class.return_value.__enter__.return_value = mock_progress

        result = collector.get_favorite_tracks()

        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 123)

        # Verify Progress was used
        mock_progress_class.assert_called_once()
        mock_progress.add_task.assert_called_once()
        self.assertEqual(mock_progress.update.call_count, 3)  # total=2 + 2x advance=1

    def test_get_playlists(self):
        """Test getting user's playlists."""
        mock_playlists = [
            MockPlaylist("pl1", "Playlist 1", "Description 1"),
            MockPlaylist("pl2", "Playlist 2", "Description 2"),
        ]

        self.mock_user.playlists.return_value = mock_playlists

        result = self.collector.get_playlists()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "pl1")
        self.assertEqual(result[0]["name"], "Playlist 1")
        self.assertEqual(result[0]["description"], "Description 1")
        self.assertEqual(result[1]["id"], "pl2")
        self.assertEqual(result[1]["name"], "Playlist 2")

    def test_get_playlist_tracks_silent_mode(self):
        """Test getting playlist tracks in silent mode."""
        mock_tracks = [
            MockTrack(123, "Song 1", ["Artist A"], "Album 1", 180),
            MockTrack(456, "Song 2", ["Artist B"], "Album 2", 240),
        ]

        mock_playlist = MagicMock()
        mock_playlist.tracks.return_value = mock_tracks
        self.mock_session.playlist.return_value = mock_playlist

        result = self.collector.get_playlist_tracks("pl1")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 123)
        self.assertEqual(result[0]["title"], "Song 1")
        self.assertEqual(result[1]["id"], 456)
        self.mock_session.playlist.assert_called_once_with("pl1")
        mock_playlist.tracks.assert_called_once()

    @patch("src.tidal_extractor.collector.Progress")
    def test_get_playlist_tracks_not_silent(self, mock_progress_class):
        """Test getting playlist tracks in non-silent mode (with Progress bar)."""
        mock_tracks = [
            MockTrack(123, "Song 1", ["Artist A"], "Album 1", 180),
            MockTrack(456, "Song 2", ["Artist B"], "Album 2", 240),
        ]

        mock_playlist = MagicMock()
        mock_playlist.tracks.return_value = mock_tracks
        self.mock_session.playlist.return_value = mock_playlist

        # Create non-silent collector
        collector = TidalCollector(self.mock_session, silent=False)

        # Mock Progress context manager
        mock_progress = MagicMock()
        mock_progress_class.return_value.__enter__.return_value = mock_progress

        result = collector.get_playlist_tracks("pl1")

        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 123)

        # Verify Progress was used
        mock_progress_class.assert_called_once()
        mock_progress.add_task.assert_called_once()
        self.assertEqual(mock_progress.update.call_count, 2)  # 2x advance=1
        self.mock_session.playlist.assert_called_once_with("pl1")
        mock_playlist.tracks.assert_called_once()

    def test_format_track_results(self):
        """Test _format_track_results method."""
        mock_tracks = [
            MockTrack(123, "Song 1", ["Artist A"], "Album 1", 180),
            MockTrack(456, "Song 2", ["Artist B", "Artist C"], None, None),
        ]

        result = self.collector._format_track_results(mock_tracks)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 123)
        self.assertEqual(result[0]["title"], "Song 1")
        self.assertEqual(result[0]["artists"], ["Artist A"])
        self.assertEqual(result[0]["album"], "Album 1")
        self.assertEqual(result[0]["duration"], 180)

        # Second track with no album
        self.assertEqual(result[1]["album"], "Unknown")
        self.assertIsNone(result[1]["duration"])

    def test_search_tracks_silent_mode(self):
        """Test searching tracks in silent mode."""
        mock_tracks = [
            MockTrack(123, "Found Song 1", ["Artist A"], "Album 1", 180),
            MockTrack(456, "Found Song 2", ["Artist B"], "Album 2", 240),
        ]

        mock_search_result = MagicMock()
        mock_search_result.items = mock_tracks
        self.mock_session.search.return_value = mock_search_result

        result = self.collector.search_tracks("test query", limit=50)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Found Song 1")
        self.mock_session.search.assert_called_once()

    def test_search_tracks_with_limit(self):
        """Test searching tracks with result limit."""
        mock_tracks = [
            MockTrack(i, f"Song {i}", ["Artist"], "Album", 180) for i in range(100)
        ]

        mock_search_result = MagicMock()
        mock_search_result.items = mock_tracks
        self.mock_session.search.return_value = mock_search_result

        result = self.collector.search_tracks("test query", limit=10)

        # Should only return 10 results
        self.assertEqual(len(result), 10)

    @patch("src.tidal_extractor.collector.Progress")
    def test_search_tracks_not_silent(self, mock_progress_class):
        """Test searching tracks in non-silent mode (with Progress bar)."""
        mock_tracks = [
            MockTrack(123, "Found Song 1", ["Artist A"], "Album 1", 180),
            MockTrack(456, "Found Song 2", ["Artist B"], "Album 2", 240),
        ]

        mock_search_result = MagicMock()
        mock_search_result.items = mock_tracks
        self.mock_session.search.return_value = mock_search_result

        # Create non-silent collector
        collector = TidalCollector(self.mock_session, silent=False)

        # Mock Progress context manager
        mock_progress = MagicMock()
        mock_progress_class.return_value.__enter__.return_value = mock_progress

        result = collector.search_tracks("test query", limit=50)

        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Found Song 1")

        # Verify Progress was used
        mock_progress_class.assert_called_once()
        mock_progress.add_task.assert_called_once()
        self.assertEqual(mock_progress.update.call_count, 2)  # total + advance

    def test_get_track_by_id_success(self):
        """Test getting a track by ID successfully."""
        mock_track = MockTrack(123, "Test Song", ["Artist A"], "Album 1", 180)
        self.mock_session.get_track.return_value = mock_track

        result = self.collector.get_track_by_id("123")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 123)
        self.assertEqual(result["title"], "Test Song")
        self.mock_session.get_track.assert_called_once_with("123")

    def test_get_track_by_id_failure(self):
        """Test getting a track by ID when it fails."""
        self.mock_session.get_track.side_effect = Exception("Track not found")

        result = self.collector.get_track_by_id("999")

        self.assertIsNone(result)

    def test_get_playlist_by_id_success(self):
        """Test getting a playlist by ID successfully."""
        mock_playlist = MockPlaylist("pl2", "Playlist 2", "Description 2")
        mock_user_playlist = MockPlaylist("pl2", "Playlist 2", "Description 2")

        # Mock the session.playlist() call
        mock_playlist_obj = MagicMock()
        mock_playlist_obj.factory.return_value = mock_user_playlist
        self.mock_session.playlist.return_value = mock_playlist_obj

        result = self.collector.get_playlist_by_id("pl2")

        self.assertIsNotNone(result)
        self.assertEqual(result.id, "pl2")
        self.assertEqual(result.name, "Playlist 2")
        self.mock_session.playlist.assert_called_once_with("pl2")

    def test_get_playlist_by_id_not_found(self):
        """Test getting a playlist by ID when it doesn't exist."""
        # Mock session.playlist() to raise an exception when playlist not found
        self.mock_session.playlist.side_effect = Exception("Playlist not found")

        result = self.collector.get_playlist_by_id("pl999")

        self.assertIsNone(result)
        self.mock_session.playlist.assert_called_once_with("pl999")

    def test_get_playlist_by_id_exception(self):
        """Test getting a playlist by ID when an exception occurs."""
        # Mock session.playlist() to raise an exception
        self.mock_session.playlist.side_effect = Exception("API error")

        result = self.collector.get_playlist_by_id("pl1")

        self.assertIsNone(result)
        self.mock_session.playlist.assert_called_once_with("pl1")

    def test_create_playlist_success(self):
        """Test creating a playlist successfully."""
        mock_playlist = MockPlaylist("new_pl", "New Playlist", "New Description")
        self.mock_user.create_playlist.return_value = mock_playlist

        result = self.collector.create_playlist("New Playlist", "New Description")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "new_pl")
        self.assertEqual(result["name"], "New Playlist")
        self.assertEqual(result["description"], "New Description")
        self.mock_user.create_playlist.assert_called_once_with(
            "New Playlist", "New Description"
        )

    def test_create_playlist_failure(self):
        """Test creating a playlist when it fails."""
        self.mock_user.create_playlist.side_effect = Exception("Creation failed")

        result = self.collector.create_playlist("New Playlist")

        self.assertIsNone(result)

    def test_add_tracks_to_playlist_success(self):
        """Test adding tracks to playlist successfully."""
        mock_playlist = MockPlaylist("pl1", "Test Playlist")

        with patch.object(
            self.collector, "get_playlist_by_id", return_value=mock_playlist
        ):
            result = self.collector.add_tracks_to_playlist("pl1", ["123", "456", "789"])

        self.assertTrue(result)

    def test_add_tracks_to_playlist_not_found(self):
        """Test adding tracks to a non-existent playlist."""
        with patch.object(self.collector, "get_playlist_by_id", return_value=None):
            result = self.collector.add_tracks_to_playlist("pl999", ["123"])

        self.assertFalse(result)

    def test_add_tracks_to_playlist_invalid_ids(self):
        """Test adding tracks with invalid track IDs."""
        mock_playlist = MockPlaylist("pl1", "Test Playlist")

        with patch.object(
            self.collector, "get_playlist_by_id", return_value=mock_playlist
        ):
            result = self.collector.add_tracks_to_playlist(
                "pl1", ["invalid", "not_a_number"]
            )

        # Should fail since no valid IDs
        self.assertFalse(result)

    def test_add_tracks_to_playlist_mixed_ids(self):
        """Test adding tracks with mix of valid and invalid IDs."""
        mock_playlist = MockPlaylist("pl1", "Test Playlist")

        with patch.object(
            self.collector, "get_playlist_by_id", return_value=mock_playlist
        ):
            result = self.collector.add_tracks_to_playlist(
                "pl1", ["123", "invalid", "456"]
            )

        # Should succeed with valid IDs
        self.assertTrue(result)

    def test_add_tracks_to_playlist_exception(self):
        """Test adding tracks when an exception occurs."""
        mock_playlist = MockPlaylist("pl1", "Test Playlist")
        mock_playlist.add = MagicMock(side_effect=Exception("API error"))

        with patch.object(
            self.collector, "get_playlist_by_id", return_value=mock_playlist
        ):
            result = self.collector.add_tracks_to_playlist("pl1", ["123"])

        self.assertFalse(result)

    def test_remove_all_favorite_tracks_success(self):
        """Test removing all favorite tracks successfully."""
        mock_tracks = [
            MockTrack(123, "Song 1", ["Artist A"], "Album 1", 180),
            MockTrack(456, "Song 2", ["Artist B"], "Album 2", 240),
        ]

        mock_favorites = MockFavorites(mock_tracks)
        self.mock_user.favorites = mock_favorites

        result = self.collector.remove_all_favorite_tracks()

        self.assertTrue(result)
        # Verify remove_track was called for each track
        self.assertEqual(mock_favorites.remove_track.call_count, 2)

    def test_remove_all_favorite_tracks_empty(self):
        """Test removing favorite tracks when there are none."""
        mock_favorites = MockFavorites([])
        self.mock_user.favorites = mock_favorites

        result = self.collector.remove_all_favorite_tracks()

        # Should succeed since there's nothing to remove
        self.assertTrue(result)

    def test_remove_all_favorite_tracks_partial_failure(self):
        """Test removing favorite tracks with some failures."""
        mock_tracks = [
            MockTrack(123, "Song 1", ["Artist A"], "Album 1", 180),
            MockTrack(456, "Song 2", ["Artist B"], "Album 2", 240),
        ]

        mock_favorites = MockFavorites(mock_tracks)
        # Make remove_track fail on second call
        mock_favorites.remove_track = MagicMock(
            side_effect=[None, Exception("Failed to remove")]
        )
        self.mock_user.favorites = mock_favorites

        result = self.collector.remove_all_favorite_tracks()

        # Should return False since not all tracks were removed
        self.assertFalse(result)

    def test_remove_all_favorite_tracks_exception(self):
        """Test removing favorite tracks when an exception occurs."""
        self.mock_user.favorites = MagicMock()
        self.mock_user.favorites.tracks.side_effect = Exception("API error")

        result = self.collector.remove_all_favorite_tracks()

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
