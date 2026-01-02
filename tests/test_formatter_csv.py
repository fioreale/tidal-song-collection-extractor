"""Unit tests for CSV export and import functionality."""

import os
import tempfile
import unittest
from pathlib import Path

from src.tidal_extractor.formatter import TrackFormatter


class TestCSVExport(unittest.TestCase):
    """Test CSV export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_tracks = [
            {
                "id": 123456,
                "title": "Test Song 1",
                "artists": ["Artist A", "Artist B"],
                "album": "Test Album 1",
                "duration": 180,
            },
            {
                "id": 789012,
                "title": "Test Song 2",
                "artists": ["Artist C"],
                "album": "Test Album 2",
                "duration": 240,
            },
            {
                "id": 345678,
                "title": "Test Song 3",
                "artists": ["Artist D", "Artist E", "Artist F"],
                "album": "Test Album 3",
                "duration": 200,
            },
        ]
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        for file in Path(self.temp_dir).glob("*.csv"):
            file.unlink()
        os.rmdir(self.temp_dir)

    def test_export_all_fields(self):
        """Test exporting CSV with all fields (default)."""
        output_file = os.path.join(self.temp_dir, "test_all_fields.csv")
        TrackFormatter.save_tracks_to_file(self.test_tracks, output_file)

        # Verify file exists
        self.assertTrue(os.path.exists(output_file))

        # Verify content
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check header
        self.assertIn("id,title,artists,album,duration", lines[0])

        # Check number of rows (header + data)
        self.assertEqual(len(lines), len(self.test_tracks) + 1)

    def test_export_custom_fields(self):
        """Test exporting CSV with custom fields."""
        output_file = os.path.join(self.temp_dir, "test_custom_fields.csv")
        custom_fields = ["id", "title", "artists"]
        TrackFormatter.save_tracks_to_file(
            self.test_tracks, output_file, csv_fields=custom_fields
        )

        # Verify file exists
        self.assertTrue(os.path.exists(output_file))

        # Verify content
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check header contains only custom fields
        header = lines[0].strip()
        self.assertEqual(header, "id,title,artists")

        # Verify album and duration are not in the file
        file_content = "".join(lines)
        self.assertNotIn("album", file_content.lower().replace("id,title,artists", ""))
        self.assertNotIn("Test Album", file_content)

    def test_export_empty_tracks(self):
        """Test exporting empty track list."""
        output_file = os.path.join(self.temp_dir, "test_empty.csv")
        TrackFormatter.save_tracks_to_file([], output_file)

        # File should not be created or should be empty
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(content, "")

    def test_artists_formatting(self):
        """Test that multiple artists are properly formatted in CSV."""
        output_file = os.path.join(self.temp_dir, "test_artists.csv")
        TrackFormatter.save_tracks_to_file(self.test_tracks, output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check that artists are comma-separated in the CSV
        # First track has "Artist A, Artist B"
        self.assertIn("Artist A, Artist B", lines[1])
        # Third track has three artists
        self.assertIn("Artist D, Artist E, Artist F", lines[3])


class TestCSVImport(unittest.TestCase):
    """Test CSV import functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_tracks = [
            {
                "id": 123456,
                "title": "Test Song 1",
                "artists": ["Artist A", "Artist B"],
                "album": "Test Album 1",
                "duration": 180,
            },
            {
                "id": 789012,
                "title": "Test Song 2",
                "artists": ["Artist C"],
                "album": "Test Album 2",
                "duration": 240,
            },
        ]
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        for file in Path(self.temp_dir).glob("*.csv"):
            file.unlink()
        os.rmdir(self.temp_dir)

    def test_import_all_fields(self):
        """Test importing CSV with all fields."""
        output_file = os.path.join(self.temp_dir, "test_import.csv")

        # First export
        TrackFormatter.save_tracks_to_file(self.test_tracks, output_file)

        # Then import
        imported_tracks = TrackFormatter.load_tracks_from_csv(output_file)

        # Verify number of tracks
        self.assertEqual(len(imported_tracks), len(self.test_tracks))

        # Verify data integrity
        for original, imported in zip(self.test_tracks, imported_tracks):
            self.assertEqual(original["id"], imported["id"])
            self.assertEqual(original["title"], imported["title"])
            self.assertEqual(original["artists"], imported["artists"])
            self.assertEqual(original["album"], imported["album"])
            self.assertEqual(original["duration"], imported["duration"])

    def test_import_missing_file(self):
        """Test importing from non-existent file."""
        with self.assertRaises(FileNotFoundError):
            TrackFormatter.load_tracks_from_csv("nonexistent.csv")

    def test_import_invalid_csv_missing_required_fields(self):
        """Test importing CSV without required fields."""
        output_file = os.path.join(self.temp_dir, "test_invalid.csv")

        # Create invalid CSV (missing 'title' field)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("id,album\n")
            f.write("123,Test Album\n")

        with self.assertRaises(ValueError) as context:
            TrackFormatter.load_tracks_from_csv(output_file)

        self.assertIn("id", str(context.exception).lower())
        self.assertIn("title", str(context.exception).lower())

    def test_import_partial_fields(self):
        """Test importing CSV with only required fields."""
        output_file = os.path.join(self.temp_dir, "test_partial.csv")

        # Create CSV with only required fields
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("id,title\n")
            f.write("123456,Test Song\n")

        imported_tracks = TrackFormatter.load_tracks_from_csv(output_file)

        # Verify track was imported
        self.assertEqual(len(imported_tracks), 1)
        self.assertEqual(imported_tracks[0]["id"], 123456)
        self.assertEqual(imported_tracks[0]["title"], "Test Song")

        # Verify optional fields have default values
        self.assertEqual(imported_tracks[0]["artists"], [])
        self.assertEqual(imported_tracks[0]["album"], "")
        self.assertIsNone(imported_tracks[0]["duration"])

    def test_import_artists_parsing(self):
        """Test that artists are properly parsed from CSV."""
        output_file = os.path.join(self.temp_dir, "test_artists_import.csv")

        # Export and import
        TrackFormatter.save_tracks_to_file(self.test_tracks, output_file)
        imported_tracks = TrackFormatter.load_tracks_from_csv(output_file)

        # Verify artists are properly parsed as lists
        self.assertEqual(imported_tracks[0]["artists"], ["Artist A", "Artist B"])
        self.assertEqual(imported_tracks[1]["artists"], ["Artist C"])


class TestCSVRoundTrip(unittest.TestCase):
    """Test round-trip export and import."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_tracks = [
            {
                "id": 111,
                "title": "Song with special chars: àéîôù",
                "artists": ["Artist 1", "Artist 2"],
                "album": "Album with, comma",
                "duration": 150,
            },
            {
                "id": 222,
                "title": 'Song with "quotes"',
                "artists": ["Artist 3"],
                "album": "Normal Album",
                "duration": 200,
            },
        ]
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        for file in Path(self.temp_dir).glob("*.csv"):
            file.unlink()
        os.rmdir(self.temp_dir)

    def test_roundtrip_all_fields(self):
        """Test that data survives export-import cycle."""
        output_file = os.path.join(self.temp_dir, "test_roundtrip.csv")

        # Export
        TrackFormatter.save_tracks_to_file(self.test_tracks, output_file)

        # Import
        imported_tracks = TrackFormatter.load_tracks_from_csv(output_file)

        # Verify exact match
        self.assertEqual(len(imported_tracks), len(self.test_tracks))
        for original, imported in zip(self.test_tracks, imported_tracks):
            self.assertEqual(original["id"], imported["id"])
            self.assertEqual(original["title"], imported["title"])
            self.assertEqual(original["artists"], imported["artists"])
            self.assertEqual(original["album"], imported["album"])
            self.assertEqual(original["duration"], imported["duration"])

    def test_roundtrip_custom_fields(self):
        """Test round-trip with custom fields."""
        output_file = os.path.join(self.temp_dir, "test_roundtrip_custom.csv")
        custom_fields = ["id", "title"]

        # Export with custom fields
        TrackFormatter.save_tracks_to_file(
            self.test_tracks, output_file, csv_fields=custom_fields
        )

        # Import
        imported_tracks = TrackFormatter.load_tracks_from_csv(output_file)

        # Verify only exported fields are preserved
        self.assertEqual(len(imported_tracks), len(self.test_tracks))
        for original, imported in zip(self.test_tracks, imported_tracks):
            self.assertEqual(original["id"], imported["id"])
            self.assertEqual(original["title"], imported["title"])
            # Other fields should have default values
            self.assertEqual(imported["artists"], [])
            self.assertEqual(imported["album"], "")
            self.assertIsNone(imported["duration"])


if __name__ == "__main__":
    unittest.main()
