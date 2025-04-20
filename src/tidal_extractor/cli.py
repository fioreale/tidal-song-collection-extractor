"""Command-line interface for Tidal Extractor."""

import sys

import click
from rich.console import Console
from rich.prompt import Prompt

from tidal_extractor.auth import authenticate
from tidal_extractor.collector import TidalCollector
from tidal_extractor.formatter import TrackFormatter

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
    type=click.Choice(["simple", "detailed"]),
    default="simple",
    help="Output format when saving to file",
)
def favorites(output, format):
    """Extract and print your favorite tracks."""
    session = authenticate()
    if not session:
        sys.exit(1)

    collector = TidalCollector(session)
    tracks = collector.get_favorite_tracks()

    if not tracks:
        console.print("[yellow]No favorite tracks found.[/yellow]")
        return

    if output:
        TrackFormatter.save_tracks_to_file(tracks, output, format)
    else:
        TrackFormatter.print_tracks_table(tracks, "Your Favorite Tracks")


@cli.command()
def playlists():
    """List your playlists."""
    session = authenticate()
    if not session:
        sys.exit(1)

    collector = TidalCollector(session)
    playlists = collector.get_playlists()

    if not playlists:
        console.print("[yellow]No playlists found.[/yellow]")
        return

    console.print("[bold]Your Playlists:[/bold]")
    for i, playlist in enumerate(playlists, 1):
        console.print(f"{i}. {playlist['name']}")


@cli.command()
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
def playlist(output, format):
    """Extract and print tracks from a specific playlist."""
    session = authenticate()
    if not session:
        sys.exit(1)

    collector = TidalCollector(session)
    playlists = collector.get_playlists()

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
        tracks = collector.get_playlist_tracks(selected["id"])

        if not tracks:
            console.print("[yellow]No tracks found in this playlist.[/yellow]")
            return

        if output:
            TrackFormatter.save_tracks_to_file(tracks, output, format)
        else:
            TrackFormatter.print_tracks_table(tracks, f"Tracks in '{selected['name']}'")

    except ValueError:
        console.print("[red]Invalid input.[/red]")


def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
