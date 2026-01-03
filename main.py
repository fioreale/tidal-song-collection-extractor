#!/usr/bin/env python3
"""Command-line interface for Tidal Extractor."""

import signal
import sys
from datetime import datetime
from pathlib import Path

import click
import questionary
from questionary import Style
from rich.console import Console
from rich.progress import Progress
from rich.prompt import (
    Confirm,  # Add this import
    Prompt,
)
from rich.table import Table

from tidal_extractor import TidalExtractor

console = Console()

# Custom style for questionary menus
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
])

# Global session state
session_active = False
session_extractor = None


@click.group()
def cli():
    """Extract and print song lists from your Tidal collection."""
    pass


@cli.command()
@click.option(
    "--output", "-o", help="Output CSV file (if not specified, prints to console)"
)
@click.option(
    "--csv-fields",
    "-f",
    help="Comma-separated list of fields to include in CSV (default: id,title,artists,album,duration)",
)
@click.option(
    "--from-csv",
    help="Load and display tracks from a CSV file instead of fetching from Tidal",
)
def favorites(output, csv_fields, from_csv):
    """Extract and print your favorite tracks."""
    extractor = TidalExtractor()

    if from_csv:
        # Load tracks from CSV file
        from tidal_extractor.formatter import TrackFormatter

        try:
            tracks = TrackFormatter.load_tracks_from_csv(from_csv)
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            sys.exit(1)
    else:
        # Fetch tracks from Tidal
        if not extractor.connect():
            sys.exit(1)

        tracks = extractor.get_favorite_tracks()

    if not tracks:
        console.print("[yellow]No favorite tracks found.[/yellow]")
        return

    if output:
        fields = csv_fields.split(",") if csv_fields else None
        extractor.save_tracks(tracks, output, fields)
    else:
        extractor.print_tracks(tracks, "Your Favorite Tracks")


@cli.command()
def playlists():
    """List your playlists."""
    extractor = TidalExtractor()

    if not extractor.connect():
        sys.exit(1)

    playlists = extractor.get_playlists()

    if not playlists:
        console.print("[yellow]No playlists found.[/yellow]")
        return

    console.print("[bold]Your Playlists:[/bold]")
    for i, playlist in enumerate(playlists, 1):
        console.print(f"{i}. {playlist['name']}")


@cli.group()
def playlist():
    """Playlist management commands."""
    pass


@playlist.command(name="list")
@click.option(
    "--output", "-o", help="Output CSV file (if not specified, prints to console)"
)
@click.option(
    "--csv-fields",
    "-f",
    help="Comma-separated list of fields to include in CSV (default: id,title,artists,album,duration)",
)
@click.option(
    "--id", help="Playlist ID (if not specified, you will be prompted to choose)"
)
@click.option(
    "--from-csv",
    help="Load and display tracks from a CSV file instead of fetching from Tidal",
)
def list_playlist(output, csv_fields, id, from_csv):
    """Extract and print tracks from a specific playlist."""
    extractor = TidalExtractor()

    if from_csv:
        # Load tracks from CSV file
        from tidal_extractor.formatter import TrackFormatter

        try:
            tracks = TrackFormatter.load_tracks_from_csv(from_csv)
            playlist_name = "CSV File"
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            sys.exit(1)
    else:
        # Fetch tracks from Tidal
        if not extractor.connect():
            sys.exit(1)

        if id:
            # Use the provided playlist ID
            playlist_id = id
            playlist_name = "Selected Playlist"
        else:
            # Let the user choose a playlist
            playlists = extractor.get_playlists()

            if not playlists:
                console.print("[yellow]No playlists found.[/yellow]")
                return

            console.print("[bold]Your Playlists:[/bold]")
            for i, playlist in enumerate(playlists, 1):
                console.print(f"{i}. {playlist['name']}")

            try:
                choice = int(Prompt.ask("Enter playlist number", default="1"))
                if choice < 1 or choice > len(playlists):
                    console.print("[red]Invalid playlist number.[/red]")
                    return

                selected = playlists[choice - 1]
                playlist_id = selected["id"]
                playlist_name = selected["name"]

            except ValueError:
                console.print("[red]Invalid input.[/red]")
                return

        tracks = extractor.get_playlist_tracks(playlist_id)

    if not tracks:
        console.print("[yellow]No tracks found in this playlist.[/yellow]")
        return

    if output:
        fields = csv_fields.split(",") if csv_fields else None
        extractor.save_tracks(tracks, output, fields)
    else:
        extractor.print_tracks(tracks, f"Tracks in '{playlist_name}'")


@playlist.command()
@click.argument("name")
@click.option("--description", "-d", help="Playlist description")
@click.option(
    "--tracks",
    "-t",
    multiple=True,
    help="Track IDs to add (can be used multiple times)",
)
@click.option(
    "--search",
    "-s",
    multiple=True,
    help="Search queries to find tracks (can be used multiple times)",
)
def create(name, description, tracks, search):
    """Create a new playlist and optionally add tracks."""
    extractor = TidalExtractor()

    if not extractor.connect():
        sys.exit(1)

    # Create the playlist
    playlist = extractor.collector.create_playlist(name, description)
    console.print(f"[bold green]Created playlist: {playlist['name']}[/bold green]")

    # Add tracks if provided
    if tracks:
        success = extractor.collector.add_tracks_to_playlist(
            playlist["id"], list(tracks)
        )
        if success:
            console.print(
                f"[bold green]Added {len(tracks)} tracks to playlist[/bold green]"
            )

    # Search and add tracks if queries provided
    if search:
        all_track_ids = []
        for query in search:
            results = extractor.collector.search_tracks(query)
            if results:
                track_ids = [track["id"] for track in results]
                all_track_ids.extend(track_ids)
                console.print(
                    f"[bold green]Found {len(results)} tracks for query: {query}[/bold green]"
                )

        if all_track_ids:
            success = extractor.collector.add_tracks_to_playlist(
                playlist["id"], all_track_ids
            )
            if success:
                console.print(
                    f"[bold green]Added {len(all_track_ids)} tracks from search results[/bold green]"
                )


@playlist.command()
@click.argument("playlist_id")
@click.argument("track_ids", nargs=-1)
def add(playlist_id, track_ids):
    """Add tracks to an existing playlist."""
    extractor = TidalExtractor()

    if not extractor.connect():
        sys.exit(1)

    success = extractor.collector.add_tracks_to_playlist(playlist_id, track_ids)
    if success:
        console.print(
            f"[bold green]Added {len(track_ids)} tracks to playlist {playlist_id}[/bold green]"
        )


@cli.command()
@click.option("--output", "-o", required=True, help="Output CSV file")
@click.option(
    "--csv-fields",
    "-f",
    help="Comma-separated list of fields to include in CSV (default: id,title,artists,album,duration)",
)
def all_playlists(output, csv_fields):
    """Extract and save tracks from all playlists."""
    extractor = TidalExtractor()

    if not extractor.connect():
        sys.exit(1)

    playlists = extractor.get_playlists()

    if not playlists:
        console.print("[yellow]No playlists found.[/yellow]")
        return

    all_tracks = []

    for playlist in playlists:
        console.print(f"Processing playlist: [cyan]{playlist['name']}[/cyan]")
        tracks = extractor.get_playlist_tracks(playlist["id"])

        # Add playlist name to each track
        for track in tracks:
            track["playlist"] = playlist["name"]

        all_tracks.extend(tracks)

    if not all_tracks:
        console.print("[yellow]No tracks found in any playlist.[/yellow]")
        return

    fields = csv_fields.split(",") if csv_fields else None
    extractor.save_tracks(all_tracks, output, fields)
    console.print(
        f"[bold green]Saved {len(all_tracks)} tracks from {len(playlists)} playlists to {output}[/bold green]"
    )


@cli.command()
@click.argument("query")
@click.option(
    "--output", "-o", help="Output CSV file (if not specified, prints to console)"
)
@click.option(
    "--csv-fields",
    "-f",
    help="Comma-separated list of fields to include in CSV (default: id,title,artists,album,duration)",
)
@click.option(
    "--from-csv",
    help="Search within a CSV file instead of fetching from Tidal",
)
def search(query, output, csv_fields, from_csv):
    """Search for tracks in your favorites and playlists."""
    extractor = TidalExtractor()

    if from_csv:
        # Load and search tracks from CSV file
        from tidal_extractor.formatter import TrackFormatter

        try:
            all_tracks = TrackFormatter.load_tracks_from_csv(from_csv)
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            sys.exit(1)

        # Search within loaded tracks
        all_matches = []
        for track in all_tracks:
            if (
                query.lower() in track["title"].lower()
                or any(query.lower() in artist.lower() for artist in track["artists"])
                or query.lower() in track["album"].lower()
            ):
                all_matches.append(track)
    else:
        # Fetch and search tracks from Tidal
        if not extractor.connect():
            sys.exit(1)

        # Search in favorites
        console.print("Searching in favorites...")
        favorites = extractor.get_favorite_tracks()
        favorite_matches = []

        for track in favorites:
            if (
                query.lower() in track["title"].lower()
                or any(query.lower() in artist.lower() for artist in track["artists"])
                or query.lower() in track["album"].lower()
            ):
                track["source"] = "Favorites"
                favorite_matches.append(track)

        # Search in playlists
        console.print("Searching in playlists...")
        playlists = extractor.get_playlists()
        playlist_matches = []

        for playlist in playlists:
            tracks = extractor.get_playlist_tracks(playlist["id"])
            for track in tracks:
                if (
                    query.lower() in track["title"].lower()
                    or any(
                        query.lower() in artist.lower() for artist in track["artists"]
                    )
                    or query.lower() in track["album"].lower()
                ):
                    track["source"] = f"Playlist: {playlist['name']}"
                    playlist_matches.append(track)

        # Combine results
        all_matches = favorite_matches + playlist_matches

    if not all_matches:
        console.print(f"[yellow]No tracks found matching '{query}'.[/yellow]")
        return

    if output:
        fields = csv_fields.split(",") if csv_fields else None
        extractor.save_tracks(all_matches, output, fields)
    else:
        extractor.print_tracks(all_matches, f"Tracks matching '{query}'")


@cli.command()
def print_all():
    """Print all favorite tracks to console."""
    extractor = TidalExtractor()

    if not extractor.connect():
        sys.exit(1)

    tracks = extractor.get_favorite_tracks()

    if not tracks:
        console.print("[yellow]No favorite tracks found.[/yellow]")
        return

    # Print in a simple format
    console.print("[bold]Your Favorite Tracks:[/bold]")
    for i, track in enumerate(tracks, 1):
        artists = ", ".join(track["artists"])
        console.print(f"{i}. {track['title']} - {artists}")


@cli.command()
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def empty_favorites(force):
    """Remove all tracks from your favorites collection.

    This is a destructive operation that cannot be undone.
    """
    extractor = TidalExtractor()

    if not extractor.connect():
        sys.exit(1)

    # Get current count of favorite tracks
    tracks = extractor.get_favorite_tracks()
    count = len(tracks)

    if count == 0:
        console.print("[yellow]Your favorites collection is already empty.[/yellow]")
        return

    # Display warning
    console.print("\n[bold red]⚠️  WARNING: DESTRUCTIVE OPERATION  ⚠️[/bold red]")
    console.print(
        f"You are about to remove all {count} tracks from your favorites collection."
    )
    console.print("[bold red]This action cannot be undone![/bold red]\n")

    if not force:
        confirm = Confirm.ask(
            "[bold yellow]Are you absolutely sure you want to remove all your favorites?[/bold yellow]"
        )
        if not confirm:
            console.print("Operation cancelled.")
            return
    else:
        # Even with force, show a warning
        console.print(
            "[bold yellow]Using --force flag to bypass confirmation check.[/bold yellow]"
        )
        console.print("Proceeding with emptying favorites...")

    # Show progress indication
    with Progress() as progress:
        task = progress.add_task("[red]Emptying favorites...", total=None)

        # Perform the operation
        success = extractor.empty_favorites()

        progress.update(task, completed=True)

    if success:
        console.print(
            f"[bold green]Successfully removed all {count} tracks from your favorites collection.[/bold green]"
        )
    else:
        console.print(
            "[bold red]Failed to completely empty your favorites collection.[/bold red]"
        )
        console.print(
            "Some tracks may have been removed. Check your collection for details."
        )


@cli.command()
def interactive():
    """Start an interactive session for running multiple commands.

    Authenticate once and run multiple commands without restarting.
    Use arrow keys to navigate menus. Press Ctrl+C to exit (with confirmation).
    """
    global session_active, session_extractor

    # Display welcome message
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   Tidal Extractor - Interactive Session Mode[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]\n")

    # Authenticate once
    console.print("[yellow]Authenticating with Tidal...[/yellow]")
    session_extractor = TidalExtractor()

    if not session_extractor.connect():
        console.print("[bold red]Authentication failed. Exiting interactive mode.[/bold red]")
        sys.exit(1)

    console.print("[bold green]✓ Authentication successful![/bold green]")
    console.print("[dim]Use arrow keys (↑/↓) to navigate, Enter to select[/dim]\n")
    session_active = True

    # Main interactive loop with menu
    while session_active:
        try:
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "📋 View Favorites",
                    "🎵 View Playlists",
                    "🔍 Search Tracks",
                    "💾 Export Favorites to CSV",
                    "📥 Export Playlist to CSV",
                    "📂 Import CSV to Create Playlist",
                    "🔄 Reorder Playlist from CSV",
                    "🗑️  Empty Favorites",
                    "❌ Exit"
                ],
                style=custom_style,
                qmark="🎼"
            ).ask()

            if not action:  # User pressed Ctrl+C
                handle_exit_confirmation()
                continue

            if "Exit" in action:
                handle_exit_confirmation()
            elif "View Favorites" in action:
                view_favorites()
            elif "View Playlists" in action:
                view_playlists()
            elif "Search Tracks" in action:
                search_tracks()
            elif "Export Favorites" in action:
                export_favorites()
            elif "Export Playlist" in action:
                export_playlist()
            elif "Import CSV to Create Playlist" in action:
                import_csv_to_playlist()
            elif "Reorder Playlist" in action:
                reorder_playlist_from_csv()
            elif "Empty Favorites" in action:
                empty_favorites_interactive()

        except (EOFError, KeyboardInterrupt):
            handle_exit_confirmation()
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            console.print("[yellow]Press Enter to continue...[/yellow]")
            input()

    console.print("\n[yellow]Session ended. Goodbye! 👋[/yellow]")


def handle_exit_confirmation():
    """Handle exit confirmation."""
    global session_active
    try:
        confirm = questionary.confirm(
            "Are you sure you want to exit?",
            default=False,
            style=custom_style
        ).ask()
        if confirm:
            session_active = False
    except (EOFError, KeyboardInterrupt):
        console.print("\n[bold red]Exiting immediately...[/bold red]")
        session_active = False


def view_favorites():
    """View favorite tracks with option to export selection."""
    tracks = session_extractor.get_favorite_tracks()
    if not tracks:
        console.print("[yellow]No favorite tracks found.[/yellow]")
        return

    session_extractor.print_tracks(tracks, "Your Favorite Tracks")
    console.print(f"\n[dim]Total: {len(tracks)} tracks[/dim]")

    # Ask if user wants to export
    export_choice = questionary.confirm(
        "Would you like to export these tracks to CSV?",
        default=False,
        style=custom_style
    ).ask()

    if export_choice:
        export_tracks_to_csv(tracks, "favorites")


def view_playlists():
    """View playlists and select one to view tracks."""
    playlists = session_extractor.get_playlists()
    if not playlists:
        console.print("[yellow]No playlists found.[/yellow]")
        return

    # Create choices for playlist selection
    playlist_choices = [
        f"{i+1}. {p['name']} (ID: {p['id']})"
        for i, p in enumerate(playlists)
    ]
    playlist_choices.append("← Back to Main Menu")

    selected = questionary.select(
        "Select a playlist to view:",
        choices=playlist_choices,
        style=custom_style
    ).ask()

    if not selected or "Back to Main Menu" in selected:
        return

    # Extract index from selection
    idx = int(selected.split(".")[0]) - 1
    playlist = playlists[idx]

    # Get and display tracks
    tracks = session_extractor.get_playlist_tracks(playlist["id"])
    if not tracks:
        console.print(f"[yellow]No tracks found in '{playlist['name']}'.[/yellow]")
        return

    session_extractor.print_tracks(tracks, f"Playlist: {playlist['name']}")
    console.print(f"\n[dim]Total: {len(tracks)} tracks[/dim]")

    # Ask if user wants to export
    export_choice = questionary.confirm(
        "Would you like to export these tracks to CSV?",
        default=False,
        style=custom_style
    ).ask()

    if export_choice:
        export_tracks_to_csv(tracks, f"playlist_{playlist['name']}")


def search_tracks():
    """Search for tracks in favorites and playlists."""
    query = questionary.text(
        "Enter search query:",
        style=custom_style
    ).ask()

    if not query:
        return

    console.print(f"\n[cyan]Searching for '{query}'...[/cyan]")

    # Search in favorites
    favorites = session_extractor.get_favorite_tracks()
    favorite_matches = [
        {**track, "source": "Favorites"}
        for track in favorites
        if query.lower() in track["title"].lower()
        or any(query.lower() in artist.lower() for artist in track["artists"])
        or query.lower() in track["album"].lower()
    ]

    # Search in playlists
    playlists = session_extractor.get_playlists()
    playlist_matches = []

    for playlist in playlists:
        tracks = session_extractor.get_playlist_tracks(playlist["id"])
        for track in tracks:
            if (
                query.lower() in track["title"].lower()
                or any(query.lower() in artist.lower() for artist in track["artists"])
                or query.lower() in track["album"].lower()
            ):
                track["source"] = f"Playlist: {playlist['name']}"
                playlist_matches.append(track)

    all_matches = favorite_matches + playlist_matches

    if not all_matches:
        console.print(f"[yellow]No tracks found matching '{query}'.[/yellow]")
        return

    session_extractor.print_tracks(all_matches, f"Search results for '{query}'")
    console.print(f"\n[dim]Total: {len(all_matches)} matches[/dim]")

    # Ask if user wants to export
    export_choice = questionary.confirm(
        "Would you like to export these results to CSV?",
        default=False,
        style=custom_style
    ).ask()

    if export_choice:
        export_tracks_to_csv(all_matches, f"search_{query}")


def export_favorites():
    """Export all favorites to CSV."""
    tracks = session_extractor.get_favorite_tracks()
    if not tracks:
        console.print("[yellow]No favorite tracks to export.[/yellow]")
        return

    export_tracks_to_csv(tracks, "favorites")


def export_playlist():
    """Export a selected playlist to CSV."""
    playlists = session_extractor.get_playlists()
    if not playlists:
        console.print("[yellow]No playlists found.[/yellow]")
        return

    # Create choices for playlist selection
    playlist_choices = [
        f"{i+1}. {p['name']}"
        for i, p in enumerate(playlists)
    ]
    playlist_choices.append("← Cancel")

    selected = questionary.select(
        "Select a playlist to export:",
        choices=playlist_choices,
        style=custom_style
    ).ask()

    if not selected or "Cancel" in selected:
        return

    # Extract index from selection
    idx = int(selected.split(".")[0]) - 1
    playlist = playlists[idx]

    # Get tracks
    tracks = session_extractor.get_playlist_tracks(playlist["id"])
    if not tracks:
        console.print(f"[yellow]No tracks found in '{playlist['name']}'.[/yellow]")
        return

    export_tracks_to_csv(tracks, f"playlist_{playlist['name']}")


def export_tracks_to_csv(tracks, default_name):
    """Export tracks to CSV file with user-specified filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"{default_name}_{timestamp}.csv"

    filename = questionary.text(
        "Enter filename for export:",
        default=default_filename,
        style=custom_style
    ).ask()

    if not filename:
        console.print("[yellow]Export cancelled.[/yellow]")
        return

    # Ensure .csv extension
    if not filename.endswith('.csv'):
        filename += '.csv'

    try:
        session_extractor.save_tracks(tracks, filename)
        console.print(f"[bold green]✓ Successfully exported {len(tracks)} tracks to '{filename}'[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error exporting tracks: {str(e)}[/bold red]")


def import_csv_to_playlist():
    """Import tracks from CSV file and create a new playlist."""
    csv_file = questionary.text(
        "Enter CSV file path:",
        style=custom_style
    ).ask()

    if not csv_file:
        console.print("[yellow]Import cancelled.[/yellow]")
        return

    # Load tracks from CSV
    try:
        from tidal_extractor.formatter import TrackFormatter
        tracks = TrackFormatter.load_tracks_from_csv(csv_file)
    except FileNotFoundError:
        console.print(f"[bold red]Error: CSV file '{csv_file}' not found[/bold red]")
        return
    except ValueError as e:
        console.print(f"[bold red]Error: Invalid CSV file - {str(e)}[/bold red]")
        return

    if not tracks:
        console.print("[yellow]No tracks found in CSV file.[/yellow]")
        return

    # Get playlist details from user
    playlist_name = questionary.text(
        "Enter new playlist name:",
        style=custom_style
    ).ask()

    if not playlist_name:
        console.print("[yellow]Playlist creation cancelled.[/yellow]")
        return

    playlist_description = questionary.text(
        "Enter playlist description (optional):",
        default="",
        style=custom_style
    ).ask()

    # Create playlist
    console.print(f"\n[cyan]Creating playlist '{playlist_name}'...[/cyan]")
    playlist = session_extractor.collector.create_playlist(playlist_name, playlist_description)

    if not playlist:
        console.print("[bold red]Failed to create playlist[/bold red]")
        return

    # Add tracks to playlist
    track_ids = [str(track["id"]) for track in tracks]
    console.print(f"[cyan]Adding {len(track_ids)} tracks to playlist...[/cyan]")
    success = session_extractor.collector.add_tracks_to_playlist(playlist["id"], track_ids)

    if success:
        console.print(
            f"[bold green]✓ Successfully created playlist '{playlist_name}' with {len(track_ids)} tracks[/bold green]"
        )
    else:
        console.print(
            f"[bold red]Partially failed to add all tracks. Some tracks may not have been added.[/bold red]"
        )


def reorder_playlist_from_csv():
    """Reorder an existing playlist based on track order from a CSV file.

    This function clears a user-owned playlist and re-adds tracks in the order
    specified in the CSV file. Only works for playlists owned by the authenticated user.
    """
    # Get list of playlists
    playlists = session_extractor.get_playlists()
    if not playlists:
        console.print("[yellow]No playlists found.[/yellow]")
        return

    # Let user select a playlist
    playlist_choices = [
        f"{i+1}. {p['name']} (ID: {p['id']})"
        for i, p in enumerate(playlists)
    ]
    playlist_choices.append("← Cancel")

    selected = questionary.select(
        "Select a playlist to reorder:",
        choices=playlist_choices,
        style=custom_style
    ).ask()

    if not selected or "Cancel" in selected:
        return

    # Extract index from selection
    idx = int(selected.split(".")[0]) - 1
    playlist = playlists[idx]

    # Get CSV file path
    csv_file = questionary.text(
        "Enter CSV file path:",
        style=custom_style
    ).ask()

    if not csv_file:
        console.print("[yellow]Reorder cancelled.[/yellow]")
        return

    # Load tracks from CSV
    try:
        from tidal_extractor.formatter import TrackFormatter
        csv_tracks = TrackFormatter.load_tracks_from_csv(csv_file)
    except FileNotFoundError:
        console.print(f"[bold red]Error: CSV file '{csv_file}' not found[/bold red]")
        return
    except ValueError as e:
        console.print(f"[bold red]Error: Invalid CSV file - {str(e)}[/bold red]")
        return

    if not csv_tracks:
        console.print("[yellow]No tracks found in CSV file.[/yellow]")
        return

    # Show warning about destructive operation
    current_tracks = session_extractor.get_playlist_tracks(playlist["id"])
    console.print("\n[bold red]⚠️  WARNING: DESTRUCTIVE OPERATION  ⚠️[/bold red]")
    console.print(
        f"You are about to reorder '{playlist['name']}' with {len(current_tracks)} track(s)."
    )
    console.print(f"The new order will have {len(csv_tracks)} track(s) from the CSV.")
    console.print("[bold red]This action will clear and rebuild the playlist![/bold red]\n")

    # Confirm with user
    confirm = questionary.confirm(
        "Are you absolutely sure you want to proceed?",
        default=False,
        style=custom_style
    ).ask()

    if not confirm:
        console.print("[yellow]Reorder cancelled.[/yellow]")
        return

    # Perform reorder
    track_ids = [str(track["id"]) for track in csv_tracks]
    console.print(f"\n[cyan]Reordering playlist with {len(track_ids)} tracks...[/cyan]")
    success = session_extractor.reorder_playlist(playlist["id"], track_ids)

    if success:
        console.print(
            f"[bold green]✓ Successfully reordered playlist '{playlist['name']}' with {len(track_ids)} tracks[/bold green]"
        )
    else:
        console.print(
            f"[bold red]Failed to reorder playlist. The playlist may be in an inconsistent state.[/bold red]"
        )


def empty_favorites_interactive():
    """Empty favorites with confirmation."""
    tracks = session_extractor.get_favorite_tracks()
    count = len(tracks)

    if count == 0:
        console.print("[yellow]Your favorites collection is already empty.[/yellow]")
        return

    console.print("\n[bold red]⚠️  WARNING: DESTRUCTIVE OPERATION  ⚠️[/bold red]")
    console.print(f"You are about to remove all {count} tracks from your favorites collection.")
    console.print("[bold red]This action cannot be undone![/bold red]\n")

    confirm = questionary.confirm(
        "Are you absolutely sure you want to remove all your favorites?",
        default=False,
        style=custom_style
    ).ask()

    if not confirm:
        console.print("[yellow]Operation cancelled.[/yellow]")
        return

    with Progress() as progress:
        task = progress.add_task("[red]Emptying favorites...", total=None)
        success = session_extractor.empty_favorites()
        progress.update(task, completed=True)

    if success:
        console.print(f"[bold green]Successfully removed all {count} tracks.[/bold green]")
    else:
        console.print("[bold red]Failed to completely empty favorites.[/bold red]")


# Global flag to track exit intent
exit_requested = False


def signal_handler(sig, frame):
    """Handle Ctrl+C signal with confirmation."""
    global exit_requested, session_active

    # If in interactive mode, let the interactive loop handle it
    if session_active:
        raise KeyboardInterrupt()

    if exit_requested:
        # User pressed Ctrl+C twice, force exit
        console.print("\n[bold red]Exiting immediately...[/bold red]")
        sys.exit(0)

    try:
        console.print()  # New line for better formatting
        confirm = Confirm.ask(
            "[bold yellow]Are you sure you want to exit?[/bold yellow]",
            default=False
        )
        if confirm:
            console.print("[yellow]Exiting...[/yellow]")
            sys.exit(0)
        else:
            console.print("[green]Continuing...[/green]")
            exit_requested = False
    except (KeyboardInterrupt, EOFError):
        # If user presses Ctrl+C during confirmation, mark for immediate exit next time
        exit_requested = True
        console.print("\n[yellow]Press Ctrl+C again to exit immediately.[/yellow]")


if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)
