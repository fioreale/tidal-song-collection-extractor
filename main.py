#!/usr/bin/env python3
"""Command-line interface for Tidal Extractor."""

import sys

import click
from rich.console import Console
from rich.progress import Progress
from rich.prompt import (
    Confirm,  # Add this import
    Prompt,
)

from tidal_extractor import TidalExtractor

console = Console()


@click.group()
def cli():
    """Extract and print song lists from your Tidal collection."""
    pass


@cli.command()
@click.option(
    "--output", "-o", help="Output file (if not specified, prints to console)"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["simple", "detailed", "ids"]),
    default="simple",
    help="Output format when saving to file",
)
def favorites(output, format):
    """Extract and print your favorite tracks."""
    extractor = TidalExtractor()

    if not extractor.connect():
        sys.exit(1)

    tracks = extractor.get_favorite_tracks()

    if not tracks:
        console.print("[yellow]No favorite tracks found.[/yellow]")
        return

    if output:
        extractor.save_tracks(tracks, output, format)
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
    "--output", "-o", help="Output file (if not specified, prints to console)"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["simple", "detailed", "ids"]),
    default="simple",
    help="Output format when saving to file",
)
@click.option(
    "--id", help="Playlist ID (if not specified, you will be prompted to choose)"
)
def list_playlist(output, format, id):
    """Extract and print tracks from a specific playlist."""
    extractor = TidalExtractor()

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
        extractor.save_tracks(tracks, output, format)
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
@click.option("--output", "-o", required=True, help="Output file")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["simple", "detailed"]),
    default="simple",
    help="Output format",
)
def all_playlists(output, format):
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

    extractor.save_tracks(all_tracks, output, format)
    console.print(
        f"[bold green]Saved {len(all_tracks)} tracks from {len(playlists)} playlists to {output}[/bold green]"
    )


@cli.command()
@click.argument("query")
@click.option(
    "--output", "-o", help="Output file (if not specified, prints to console)"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["simple", "detailed"]),
    default="simple",
    help="Output format when saving to file",
)
def search(query, output, format):
    """Search for tracks in your favorites and playlists."""
    extractor = TidalExtractor()

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
                or any(query.lower() in artist.lower() for artist in track["artists"])
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
        extractor.save_tracks(all_matches, output, format)
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


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)
