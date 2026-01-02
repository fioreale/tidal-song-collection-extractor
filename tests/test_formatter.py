"""Unit tests for TrackFormatter class (non-CSV functionality)."""

import os
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from src.tidal_extractor.formatter import TrackFormatter


class TestFormatDuration(unittest.TestCase):
    """Test format_duration method."""

    def test_format_duration_valid(self):
        """Test formatting valid duration."""
        self.assertEqual(TrackFormatter.format_duration(180), "3:00")
        self.assertEqual(TrackFormatter.format_duration(240), "4:00")
        self.assertEqual(TrackFormatter.format_duration(65), "1:05")
        self.assertEqual(TrackFormatter.format_duration(3661), "61:01")

    def test_format_duration_zero(self):
        """Test formatting zero duration."""
        self.assertEqual(TrackFormatter.format_duration(0), "0:00")

    def test_format_duration_none(self):
        """Test formatting None duration."""
        self.assertEqual(TrackFormatter.format_duration(None), "Unknown")

    def test_format_duration_edge_cases(self):
        """Test formatting edge case durations."""
        self.assertEqual(TrackFormatter.format_duration(1), "0:01")
        self.assertEqual(TrackFormatter.format_duration(59), "0:59")
        self.assertEqual(TrackFormatter.format_duration(60), "1:00")
        self.assertEqual(TrackFormatter.format_duration(61), "1:01")


class TestPrintTracksTable(unittest.TestCase):
    """Test print_tracks_table method."""

    def test_print_tracks_table(self):
        """Test printing tracks table."""
        test_tracks = [
            {
                "id": 123,
                "title": "Test Song",
                "artists": ["Artist A", "Artist B"],
                "album": "Test Album",
                "duration": 180,
            }
        ]

        # Capture console output
        with patch("src.tidal_extractor.formatter.console.print") as mock_print:
            TrackFormatter.print_tracks_table(test_tracks, title="Test Tracks")

            # Verify print was called
            mock_print.assert_called_once()

    def test_print_tracks_table_empty(self):
        """Test printing empty tracks table."""
        with patch("src.tidal_extractor.formatter.console.print") as mock_print:
            TrackFormatter.print_tracks_table([], title="Empty Tracks")

            # Should still print table (with no rows)
            mock_print.assert_called_once()

    def test_print_tracks_table_multiple_tracks(self):
        """Test printing table with multiple tracks."""
        test_tracks = [
            {
                "id": 123,
                "title": "Song 1",
                "artists": ["Artist A"],
                "album": "Album 1",
                "duration": 180,
            },
            {
                "id": 456,
                "title": "Song 2",
                "artists": ["Artist B", "Artist C"],
                "album": "Album 2",
                "duration": None,
            },
        ]

        with patch("src.tidal_extractor.formatter.console.print") as mock_print:
            TrackFormatter.print_tracks_table(test_tracks)

            # Verify print was called
            mock_print.assert_called_once()


class TestWriteFormats(unittest.TestCase):
    """Test various write format methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_tracks = [
            {
                "id": 123,
                "title": "Test Song 1",
                "artists": ["Artist A", "Artist B"],
                "album": "Test Album 1",
                "duration": 180,
            },
            {
                "id": 456,
                "title": "Test Song 2",
                "artists": ["Artist C"],
                "album": "Test Album 2",
                "duration": 240,
            },
        ]

    def test_write_simple_format(self):
        """Test _write_simple_format method."""
        output = StringIO()
        TrackFormatter._write_simple_format(self.test_tracks, output)

        content = output.getvalue()
        self.assertIn("1. [123] Test Song 1 - Artist A, Artist B", content)
        self.assertIn("2. [456] Test Song 2 - Artist C", content)

    def test_write_simple_format_empty(self):
        """Test _write_simple_format with empty track list."""
        output = StringIO()
        TrackFormatter._write_simple_format([], output)

        content = output.getvalue()
        self.assertEqual(content, "")

    def test_write_detailed_format(self):
        """Test _write_detailed_format method."""
        output = StringIO()
        TrackFormatter._write_detailed_format(self.test_tracks, output)

        content = output.getvalue()

        # Check first track details
        self.assertIn("Track #1", content)
        self.assertIn("ID: 123", content)
        self.assertIn("Title: Test Song 1", content)
        self.assertIn("Artist(s): Artist A, Artist B", content)
        self.assertIn("Album: Test Album 1", content)
        self.assertIn("Duration: 3:00", content)

        # Check second track details
        self.assertIn("Track #2", content)
        self.assertIn("ID: 456", content)
        self.assertIn("Duration: 4:00", content)

        # Check separator
        self.assertIn("-" * 40, content)

    def test_write_detailed_format_with_none_duration(self):
        """Test _write_detailed_format with None duration."""
        tracks = [
            {
                "id": 123,
                "title": "Test Song",
                "artists": ["Artist A"],
                "album": "Test Album",
                "duration": None,
            }
        ]

        output = StringIO()
        TrackFormatter._write_detailed_format(tracks, output)

        content = output.getvalue()
        self.assertIn("Duration: Unknown", content)

    def test_write_ids_only_format(self):
        """Test _write_ids_only_format method."""
        output = StringIO()
        TrackFormatter._write_ids_only_format(self.test_tracks, output)

        content = output.getvalue()
        lines = content.strip().split("\n")

        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "123")
        self.assertEqual(lines[1], "456")

    def test_write_ids_only_format_empty(self):
        """Test _write_ids_only_format with empty track list."""
        output = StringIO()
        TrackFormatter._write_ids_only_format([], output)

        content = output.getvalue()
        self.assertEqual(content, "")


class TestCSVFormatEdgeCases(unittest.TestCase):
    """Test edge cases for CSV format writing."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        for file in Path(self.temp_dir).glob("*.csv"):
            file.unlink()
        os.rmdir(self.temp_dir)

    def test_write_csv_format_with_empty_artists(self):
        """Test CSV export with empty artists list."""
        tracks = [
            {
                "id": 123,
                "title": "Test Song",
                "artists": [],
                "album": "Test Album",
                "duration": 180,
            }
        ]

        output_file = os.path.join(self.temp_dir, "test_empty_artists.csv")
        TrackFormatter.save_tracks_to_file(tracks, output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check that artists field is empty (just commas)
        self.assertIn("123,Test Song,,Test Album,180", lines[1])

    def test_write_csv_format_with_missing_fields(self):
        """Test CSV export with missing optional fields."""
        tracks = [
            {
                "id": 123,
                "title": "Test Song",
                # Missing artists, album, duration
            }
        ]

        output_file = os.path.join(self.temp_dir, "test_missing_fields.csv")
        TrackFormatter.save_tracks_to_file(tracks, output_file)

        # Should not raise an error
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check that missing fields are empty
        self.assertIn("123,Test Song,,,", lines[1])

    def test_load_csv_with_extra_fields(self):
        """Test loading CSV with extra fields."""
        output_file = os.path.join(self.temp_dir, "test_extra_fields.csv")

        # Create CSV with extra fields
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("id,title,artists,album,duration,extra_field\n")
            f.write("123,Test Song,Artist A,Test Album,180,extra_value\n")

        # Should load successfully, ignoring extra field
        tracks = TrackFormatter.load_tracks_from_csv(output_file)

        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["id"], 123)
        self.assertEqual(tracks[0]["title"], "Test Song")

    def test_load_csv_with_empty_artists(self):
        """Test loading CSV with empty artists field."""
        output_file = os.path.join(self.temp_dir, "test_empty_artists_import.csv")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("id,title,artists\n")
            f.write("123,Test Song,\n")

        tracks = TrackFormatter.load_tracks_from_csv(output_file)

        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["artists"], [])

    def test_load_csv_with_single_artist(self):
        """Test loading CSV with single artist (no comma)."""
        output_file = os.path.join(self.temp_dir, "test_single_artist.csv")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("id,title,artists\n")
            f.write("123,Test Song,Single Artist\n")

        tracks = TrackFormatter.load_tracks_from_csv(output_file)

        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["artists"], ["Single Artist"])

    def test_load_csv_with_whitespace_in_artists(self):
        """Test loading CSV handles whitespace in artist names."""
        output_file = os.path.join(self.temp_dir, "test_whitespace_artists.csv")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("id,title,artists\n")
            # Quote the field to keep the commas inside
            f.write('123,Test Song,"  Artist A  ,  Artist B  "\n')

        tracks = TrackFormatter.load_tracks_from_csv(output_file)

        # Should strip whitespace
        self.assertEqual(tracks[0]["artists"], ["Artist A", "Artist B"])

    def test_load_csv_invalid_id(self):
        """Test loading CSV with invalid ID field."""
        output_file = os.path.join(self.temp_dir, "test_invalid_id.csv")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("id,title\n")
            f.write("not_a_number,Test Song\n")

        # Should raise ValueError when trying to convert to int
        with self.assertRaises(ValueError):
            TrackFormatter.load_tracks_from_csv(output_file)

    def test_load_csv_invalid_duration(self):
        """Test loading CSV with invalid duration field."""
        output_file = os.path.join(self.temp_dir, "test_invalid_duration.csv")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("id,title,duration\n")
            f.write("123,Test Song,not_a_number\n")

        # Should raise ValueError when trying to convert duration to int
        with self.assertRaises(ValueError):
            TrackFormatter.load_tracks_from_csv(output_file)


if __name__ == "__main__":
    unittest.main()
