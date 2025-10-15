"""Output formatting module."""

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
        tracks: List[Dict[str, Any]], filename: str, format_type: str = "simple"
    ) -> None:
        """Save tracks to a file.

        Args:
            tracks: List of track dictionaries
            filename: Output filename
            format_type: Format type ('simple', 'detailed', 'ids')
        """
        with open(filename, "w", encoding="utf-8") as f:
            if format_type == "simple":
                TrackFormatter._write_simple_format(tracks, f)
            elif format_type == "detailed":
                TrackFormatter._write_detailed_format(tracks, f)
            elif format_type == "ids":
                TrackFormatter._write_ids_only_format(tracks, f)
            else:
                raise ValueError(f"Unknown format type: {format_type}")

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
