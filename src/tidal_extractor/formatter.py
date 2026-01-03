"""Output formatting module."""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO

from rich.console import Console
from rich.table import Table

console = Console()


class TrackFormatter:
    """Format track data for different outputs."""

    @staticmethod
    def format_duration(seconds: Optional[int]) -> str:
        """Format duration in seconds to MM:SS format.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        if seconds is None:
            return "Unknown"

        minutes, seconds = divmod(seconds, 60)
        return f"{minutes}:{seconds:02d}"

    @staticmethod
    def print_tracks_table(tracks: List[Dict[str, Any]], title: str = "Tracks") -> None:
        """Print tracks in a rich table.

        Args:
            tracks: List of track dictionaries
            title: Table title
        """
        table = Table(title=title)

        table.add_column("#", justify="right", style="dim")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Artist(s)", style="yellow")
        table.add_column("Album", style="blue")
        table.add_column("Duration", justify="right")

        for i, track in enumerate(tracks, 1):
            artists = ", ".join(track["artists"])
            duration = TrackFormatter.format_duration(track["duration"])

            table.add_row(
                str(i),
                str(track["id"]),
                track["title"],
                artists,
                track["album"],
                duration,
            )

        console.print(table)

    @staticmethod
    def save_tracks_to_file(
        tracks: List[Dict[str, Any]],
        filename: str,
        csv_fields: Optional[List[str]] = None,
    ) -> None:
        """Save tracks to a CSV file.

        Args:
            tracks: List of track dictionaries
            filename: Output filename
            csv_fields: List of fields to include in CSV (default: all fields)
        """
        if csv_fields is None:
            csv_fields = ["id", "title", "artists", "album", "duration"]

        TrackFormatter._write_csv_format(tracks, filename, csv_fields)

        console.print(
            f"[bold green]Saved {len(tracks)} tracks to {filename}[/bold green]"
        )

    @staticmethod
    def _write_simple_format(tracks: List[Dict[str, Any]], file: TextIO) -> None:
        """Write tracks in simple format.

        Args:
            tracks: List of track dictionaries
            file: File object to write to
        """
        for i, track in enumerate(tracks, 1):
            artists = ", ".join(track["artists"])
            file.write(f"{i}. [{track['id']}] {track['title']} - {artists}\n")

    @staticmethod
    def _write_detailed_format(tracks: List[Dict[str, Any]], file: TextIO) -> None:
        """Write tracks in detailed format.

        Args:
            tracks: List of track dictionaries
            file: File object to write to
        """
        for i, track in enumerate(tracks, 1):
            artists = ", ".join(track["artists"])
            duration = TrackFormatter.format_duration(track["duration"])

            file.write(f"Track #{i}\n")
            file.write(f"ID: {track['id']}\n")
            file.write(f"Title: {track['title']}\n")
            file.write(f"Artist(s): {artists}\n")
            file.write(f"Album: {track['album']}\n")
            file.write(f"Duration: {duration}\n")
            file.write("-" * 40 + "\n")

    @staticmethod
    def _write_ids_only_format(tracks: List[Dict[str, Any]], file: TextIO) -> None:
        """Write only track IDs to file.

        Args:
            tracks: List of track dictionaries
            file: File object to write to
        """
        for track in tracks:
            file.write(f"{track['id']}\n")

    @staticmethod
    def _write_csv_format(
        tracks: List[Dict[str, Any]], filename: str, csv_fields: List[str]
    ) -> None:
        """Write tracks in CSV format.

        Args:
            tracks: List of track dictionaries
            filename: Output filename
            csv_fields: List of fields to include in CSV
        """
        if not tracks:
            return

        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_fields)
            writer.writeheader()

            for track in tracks:
                row = {}
                for field in csv_fields:
                    if field == "artists":
                        # Join artists list into a single string
                        row[field] = ", ".join(track.get("artists", []))
                    elif field == "duration":
                        # Keep duration as seconds for CSV (easier to process)
                        row[field] = track.get("duration", "")
                    else:
                        row[field] = track.get(field, "")
                writer.writerow(row)

    @staticmethod
    def load_tracks_from_csv(filename: str) -> List[Dict[str, Any]]:
        """Load tracks from a CSV file.

        Args:
            filename: Input CSV filename

        Returns:
            List of track dictionaries

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV file is invalid
        """
        file_path = Path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {filename}")

        tracks = []
        with open(filename, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            # Validate required fields
            required_fields = {"id", "title"}
            if not required_fields.issubset(set(reader.fieldnames or [])):
                raise ValueError(
                    f"CSV must contain at least 'id' and 'title' columns. "
                    f"Found: {reader.fieldnames}"
                )

            for row in reader:
                track = {
                    "id": int(row["id"]) if row.get("id") else None,
                    "title": row.get("title", ""),
                    "artists": (
                        [a.strip() for a in row["artists"].split(",")]
                        if row.get("artists")
                        else []
                    ),
                    "album": row.get("album", ""),
                    "duration": int(row["duration"]) if row.get("duration") else None,
                }
                tracks.append(track)

        console.print(
            f"[bold green]Loaded {len(tracks)} tracks from {filename}[/bold green]"
        )
        return tracks
