"""Data collection module for Tidal API."""

from typing import Any, Dict, List, Optional

import tidalapi
from rich.console import Console
from rich.progress import Progress

console = Console()


class TidalCollector:
    """Class to collect data from Tidal API."""

    def __init__(self, session: tidalapi.Session, silent: bool = False):
        """Initialize with an authenticated session.

        Args:
            session: Authenticated Tidal session
            silent: If True, suppress progress output
        """
        self.session = session
        self.user = session.user
        self.silent = silent

    def get_favorite_tracks(self) -> List[Dict[str, Any]]:
        """Get user's favorite tracks.

        Returns:
            List of track dictionaries
        """
        if self.silent:
            favorites = self.user.favorites
            tracks = favorites.tracks()

            result = []
            for track in tracks:
                result.append(
                    {
                        "id": track.id,
                        "title": track.name,
                        "artists": [artist.name for artist in track.artists],
                        "album": track.album.name
                        if hasattr(track, "album") and track.album
                        else "Unknown",
                        "duration": track.duration
                        if hasattr(track, "duration")
                        else None,
                    }
                )
            return result
        else:
            with Progress() as progress:
                task = progress.add_task(
                    "[cyan]Fetching favorite tracks...", total=None
                )

                favorites = self.user.favorites
                tracks = favorites.tracks()

                progress.update(task, total=len(tracks))

                result = []
                for track in tracks:
                    result.append(
                        {
                            "id": track.id,
                            "title": track.name,
                            "artists": [artist.name for artist in track.artists],
                            "album": track.album.name
                            if hasattr(track, "album") and track.album
                            else "Unknown",
                            "duration": track.duration
                            if hasattr(track, "duration")
                            else None,
                        }
                    )
                    progress.update(task, advance=1)

                return result

    def get_playlists(self) -> List[Dict[str, Any]]:
        """Get user's playlists.

        Returns:
            List of playlist dictionaries
        """
        playlists = self.user.playlists()
        return [
            {"id": p.id, "name": p.name, "description": p.description}
            for p in playlists
        ]

    def get_playlist_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
        """Get tracks from a specific playlist.

        Args:
            playlist_id: ID of the playlist

        Returns:
            List of track dictionaries
        """
        if self.silent:
            playlist = self.session.playlist(playlist_id)
            tracks = playlist.tracks()

            result = []
            for track in tracks:
                result.append(
                    {
                        "id": track.id,
                        "title": track.name,
                        "artists": [artist.name for artist in track.artists],
                        "album": track.album.name
                        if hasattr(track, "album") and track.album
                        else "Unknown",
                        "duration": track.duration
                        if hasattr(track, "duration")
                        else None,
                    }
                )
            return result
        else:
            with Progress() as progress:
                playlist = self.session.playlist(playlist_id)
                tracks = playlist.tracks()

                task = progress.add_task(
                    "[cyan]Fetching playlist tracks...", total=len(tracks)
                )

                result = []
                for track in tracks:
                    result.append(
                        {
                            "id": track.id,
                            "title": track.name,
                            "artists": [artist.name for artist in track.artists],
                            "album": track.album.name
                            if hasattr(track, "album") and track.album
                            else "Unknown",
                            "duration": track.duration
                            if hasattr(track, "duration")
                            else None,
                        }
                    )
                    progress.update(task, advance=1)

                return result

    def _format_track_results(self, tracks: List[Any]) -> List[Dict[str, Any]]:
        """Format track results into dictionaries.

        Args:
            tracks: List of track objects

        Returns:
            List of formatted track dictionaries
        """
        return [
            {
                "id": track.id,
                "title": track.name,
                "artists": [artist.name for artist in track.artists],
                "album": track.album.name
                if hasattr(track, "album") and track.album
                else "Unknown",
                "duration": track.duration if hasattr(track, "duration") else None,
            }
            for track in tracks
        ]

    def search_tracks(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for tracks by name, artist, or album.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of track dictionaries
        """
        if self.silent:
            tracks = self.session.search(query, models=tidalapi.media.Track).items
            return self._format_track_results(tracks[:limit])
        else:
            with Progress() as progress:
                task = progress.add_task("[cyan]Searching tracks...", total=None)

                tracks = self.session.search(query, models=tidalapi.media.Track).items
                progress.update(task, total=min(len(tracks), limit))

                results = self._format_track_results(tracks[:limit])
                progress.update(task, advance=len(results))

                return results

    def get_track_by_id(self, track_id: str) -> Optional[Dict[str, Any]]:
        """Get a track by its ID.

        Args:
            track_id: Tidal track ID

        Returns:
            Track dictionary or None if not found
        """
        try:
            track = self.session.get_track(track_id)
            return {
                "id": track.id,
                "title": track.name,
                "artists": [artist.name for artist in track.artists],
                "album": track.album.name
                if hasattr(track, "album") and track.album
                else "Unknown",
                "duration": track.duration if hasattr(track, "duration") else None,
            }
        except Exception as e:
            if not self.silent:
                console.print(
                    f"[yellow]Failed to get track {track_id}: {str(e)}[/yellow]"
                )
            return None

    def get_playlist_by_id(self, playlist_id: str) -> Optional[Any]:
        """Get a playlist object by its ID.

        Args:
            playlist_id: ID of the playlist

        Returns:
            Playlist or UserPlaylist object (if owned by user) or None if not found
        """
        try:
            # Get the playlist using session.playlist() which returns a Playlist object
            playlist = self.session.playlist(playlist_id)

            # Use the factory method to convert to UserPlaylist if it's owned by the user
            # This is necessary to access deletion methods like clear(), remove_by_id(), etc.
            return playlist.factory()

        except Exception as e:
            if not self.silent:
                console.print(
                    f"[yellow]Error accessing playlist {playlist_id}: {str(e)}[/yellow]"
                )
            return None

    def create_playlist(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new playlist.

        Args:
            name: Playlist name
            description: Optional playlist description

        Returns:
            Created playlist dictionary or None if failed
        """
        try:
            # Create the playlist using the user object
            playlist = self.user.create_playlist(name, description)

            return {
                "id": playlist.id,
                "name": playlist.name,
                "description": playlist.description
                if hasattr(playlist, "description")
                else "",
            }

        except Exception as e:
            if not self.silent:
                console.print(f"[yellow]Failed to create playlist: {str(e)}[/yellow]")
            return None

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        """Add tracks to an existing playlist.

        Args:
            playlist_id: ID of the playlist
            track_ids: List of track IDs to add

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the playlist object
            playlist = self.get_playlist_by_id(playlist_id)

            if not playlist:
                if not self.silent:
                    console.print(
                        f"[yellow]Playlist with ID {playlist_id} not found[/yellow]"
                    )
                return False

            # Convert track_ids to integers if they're strings
            int_track_ids = []
            for track_id in track_ids:
                try:
                    int_track_ids.append(int(track_id))
                except ValueError:
                    if not self.silent:
                        console.print(
                            f"[yellow]Invalid track ID format: {track_id}[/yellow]"
                        )

            if not int_track_ids:
                if not self.silent:
                    console.print("[yellow]No valid track IDs to add[/yellow]")
                return False

            # Use the add method as documented
            if not self.silent:
                console.print(f"Adding {len(int_track_ids)} tracks to playlist...")

            playlist.add(int_track_ids)

            if not self.silent:
                console.print(
                    f"[bold green]Successfully added {len(int_track_ids)} tracks to playlist[/bold green]"
                )

            return True

        except Exception as e:
            if not self.silent:
                console.print(
                    f"[yellow]Failed to add tracks to playlist: {str(e)}[/yellow]"
                )
            return False

    def remove_all_favorite_tracks(self) -> bool:
        """Remove all tracks from the user's favorites.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all favorite tracks
            favorites = self.user.favorites
            tracks = favorites.tracks()

            if not tracks:
                if not self.silent:
                    console.print("[yellow]No favorite tracks found to remove[/yellow]")
                return True  # Already empty, so technically successful

            if not self.silent:
                console.print(f"Removing {len(tracks)} tracks from favorites...")

            # Remove each track from favorites
            success_count = 0
            for track in tracks:
                try:
                    favorites.remove_track(track.id)
                    success_count += 1
                    if not self.silent:
                        console.print(f"Removed track: {track.name}")
                except Exception as e:
                    if not self.silent:
                        console.print(
                            f"[yellow]Failed to remove track {track.id}: {str(e)}[/yellow]"
                        )

            if not self.silent:
                console.print(
                    f"[bold green]Successfully removed {success_count} out of {len(tracks)} tracks from favorites[/bold green]"
                )

            return success_count == len(tracks)

        except Exception as e:
            if not self.silent:
                console.print(f"[red]Failed to remove favorite tracks: {str(e)}[/red]")
            return False

    def clear_playlist(self, playlist_id: str) -> bool:
        """Remove all tracks from a user-owned playlist.

        This method uses the tidalapi UserPlaylist.clear() method to remove all tracks.
        Note: This only works for playlists owned by the authenticated user.

        Args:
            playlist_id: ID of the playlist to clear

        Returns:
            True if successful, False otherwise
        """
        try:
            playlist = self.get_playlist_by_id(playlist_id)

            if not playlist:
                if not self.silent:
                    console.print(
                        f"[yellow]Playlist with ID {playlist_id} not found[/yellow]"
                    )
                return False

            # Check if this is a UserPlaylist (user-owned playlist)
            # Only UserPlaylist objects have the clear() method
            if not hasattr(playlist, 'clear'):
                if not self.silent:
                    console.print(
                        "[yellow]Cannot clear this playlist. You can only clear playlists that you own.[/yellow]"
                    )
                return False

            # Get current track count
            num_tracks = playlist.num_tracks

            if num_tracks == 0:
                if not self.silent:
                    console.print("[yellow]Playlist is already empty[/yellow]")
                return True

            if not self.silent:
                console.print(f"Clearing {num_tracks} tracks from playlist...")

            # Use the UserPlaylist.clear() method
            success = playlist.clear()

            if success and not self.silent:
                console.print(
                    f"[bold green]Successfully cleared all {num_tracks} tracks from playlist[/bold green]"
                )

            return success

        except Exception as e:
            if not self.silent:
                console.print(f"[red]Failed to clear playlist: {str(e)}[/red]")
            return False

    def reorder_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        """Reorder all tracks in a user-owned playlist based on the provided track IDs.

        This method clears the playlist and re-adds tracks in the specified order.
        Note: This only works for playlists owned by the authenticated user.

        Args:
            playlist_id: ID of the playlist to reorder
            track_ids: List of track IDs in the desired order

        Returns:
            True if successful, False otherwise
        """
        try:
            # First, clear the playlist
            if not self.clear_playlist(playlist_id):
                if not self.silent:
                    console.print("[yellow]Failed to clear playlist before reordering[/yellow]")
                return False

            # Convert to list if not already
            if not isinstance(track_ids, list):
                track_ids = list(track_ids)

            if not track_ids:
                if not self.silent:
                    console.print("[yellow]No tracks to add to playlist[/yellow]")
                return True

            # Add tracks back in the specified order
            success = self.add_tracks_to_playlist(playlist_id, track_ids)

            if success and not self.silent:
                console.print(
                    f"[bold green]Successfully reordered playlist with {len(track_ids)} tracks[/bold green]"
                )

            return success

        except Exception as e:
            if not self.silent:
                console.print(f"[red]Failed to reorder playlist: {str(e)}[/red]")
            return False
