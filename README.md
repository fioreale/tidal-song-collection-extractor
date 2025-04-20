# Tidal Song Collection Extractor

A Python tool to extract and print song lists from your Tidal collection. This project is structured as a Rye project for modern Python development.

## Installation

### Using Rye

This project uses [Rye](https://rye-up.com/) for dependency management and packaging.

```bash
# Clone the repository
git clone https://github.com/yourusername/tidal-extractor.git
cd tidal-extractor

# Install with Rye
rye sync
```

### Manual Installation

If you don't have Rye installed:

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Command-Line Usage

The `tidal-extractor` command provides various subcommands to interact with your Tidal collection.

### Authentication

All commands will automatically handle authentication with Tidal. You'll be prompted to visit a URL to authorize the application.

### Basic Commands

#### Print your favorite tracks

```bash
tidal-extractor favorites
```

#### Print all favorite tracks in a simple list format

```bash
tidal-extractor print-all
```

#### List your playlists

```bash
tidal-extractor playlists
```

#### Print tracks from a specific playlist

```bash
tidal-extractor playlist
```

You'll be prompted to select a playlist from your collection.

### Playlist Management

#### List tracks in a playlist
```bash
tidal-extractor playlist list
```

#### Create a new playlist
```bash
# Create an empty playlist
tidal-extractor playlist create "My New Playlist" --description "Optional description"

# Create and add specific tracks
tidal-extractor playlist create "My Playlist" -t track_id1 -t track_id2

# Create and add tracks from search
tidal-extractor playlist create "Rock Mix" -s "metallica" -s "iron maiden"

# Combine direct tracks and search
tidal-extractor playlist create "Mixed Playlist" -t track_id1 -s "search query"
```

#### Add tracks to an existing playlist
```bash
# Add specific tracks
tidal-extractor playlist add playlist_id track_id1 track_id2 track_id3

# Example
tidal-extractor playlist add 12345678 87654321 98765432
```

### Output Options

Most commands support saving the output to a file and different output formats:

#### Save your favorite tracks to a file

```bash
tidal-extractor favorites --output favorites.txt
```

#### Save with specific format

```bash
tidal-extractor favorites --output favorites.txt --format detailed
```

The `--format` option accepts:
- `simple` (default): Displays a table with track information including IDs
- `detailed`: Multiple lines per track with all available metadata
- `ids`: Only track IDs, one per line

### Output Formats

#### Simple Format (default)
```bash
tidal-extractor favorites
```
This will display a table with all track information including IDs.

#### Detailed Format
```bash
tidal-extractor favorites --output tracks.txt --format detailed
```
This will save a detailed text file with all track information.

#### IDs Only Format
```bash
tidal-extractor favorites --output track_ids.txt --format ids
```
This will save a file containing only the track IDs, one per line.

### Advanced Commands

#### Save tracks from a specific playlist using its ID

```bash
tidal-extractor playlist --id YOUR_PLAYLIST_ID --output playlist_tracks.txt
```

#### Save tracks from all playlists

```bash
tidal-extractor all-playlists --output all_playlists.txt
```

#### Search for tracks across your collection

```bash
tidal-extractor search "query string"
```

This searches your favorites and all playlists for tracks matching the query in title, artist, or album.

#### Save search results to a file

```bash
tidal-extractor search "query string" --output search_results.txt
```

### Global Options

These options can be used with any command:

```bash
# Show help information
tidal-extractor --help

# Show help for a specific command
tidal-extractor favorites --help

# Show version information
tidal-extractor --version
```

## Using as a Python Module

You can also use the package programmatically in your Python code:

```python
from tidal_extractor import TidalExtractor

# Create an extractor instance
extractor = TidalExtractor()

# Connect to Tidal (this will prompt for authentication)
if extractor.connect():
    # Get favorite tracks
    tracks = extractor.get_favorite_tracks()
    
    # Print tracks to console
    extractor.print_tracks(tracks, "My Favorite Tracks")
    
    # Save tracks to a file
    extractor.save_tracks(tracks, "favorites.txt", "simple")
    
    # Get playlists
    playlists = extractor.get_playlists()
    
    # Get tracks from a specific playlist
    if playlists:
        playlist_id = playlists[0]['id']
        playlist_tracks = extractor.get_playlist_tracks(playlist_id)
        
        # Print playlist tracks
        extractor.print_tracks(playlist_tracks, f"Tracks in '{playlists[0]['name']}'")
```

### Silent Mode

For programmatic usage, you can enable silent mode to suppress console output:

```python
extractor = TidalExtractor(silent=True)
```

### Track Data Structure

Each track is represented as a dictionary with the following fields:

```python
{
    'id': 'track_id',
    'title': 'Track Title',
    'artists': ['Artist 1', 'Artist 2'],
    'album': 'Album Name',
    'duration': 180  # in seconds
}
```

## Rye Project Structure

This project follows the Rye project structure:

```
tidal-extractor/
├── pyproject.toml        # Project metadata and dependencies
├── README.md             # This file
├── src/
│   └── tidal_extractor/  # Source code
│       ├── __init__.py
│       ├── auth.py
│       ├── collector.py
│       ├── formatter.py
│       └── core.py
├── tests/                # Test files
└── main.py               # CLI entry point
```

## Development

### Running Tests

```bash
rye test
```

### Building the Package

```bash
rye build
```

### Updating Dependencies

```bash
rye add package-name
rye sync
```

## Configuration for Rye

The `pyproject.toml` file contains all the configuration for the project:

```toml
[project]
name = "tidal-extractor"
version = "0.1.0"
description = "A tool to extract and print song lists from Tidal"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
dependencies = [
    "tidalapi>=0.7.0",
    "rich>=12.0.0",
    "click>=8.0.0",
]
requires-python = ">=3.7"
readme = "README.md"
license = {text = "MIT"}

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.rye]
managed = true
dev-dependencies = [
    "pytest>=7.0.0",
]

[tool.hatch.metadata]
allow-direct-references = true

[tool.hatch.build.targets.wheel]
packages = ["src/tidal_extractor"]
```

## Examples

### Example 1: Export favorite tracks in different formats

```python
from tidal_extractor import TidalExtractor

extractor = TidalExtractor()
if extractor.connect():
    # Get favorite tracks
    tracks = extractor.get_favorite_tracks()
    
    # Save in simple format (default)
    extractor.save_tracks(tracks, "favorites_simple.txt")
    
    # Save in detailed format
    extractor.save_tracks(tracks, "favorites_detailed.txt", format="detailed")
    
    # Save only track IDs
    extractor.save_tracks(tracks, "favorite_ids.txt", format="ids")
```

### Example 2: Export all favorite tracks to a CSV file

```python
from tidal_extractor import TidalExtractor
import csv

extractor = TidalExtractor()
if extractor.connect():
    tracks = extractor.get_favorite_tracks()
    
    with open('favorites.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Artists', 'Album', 'Duration'])
        
        for track in tracks:
            writer.writerow([
                track['title'],
                ', '.join(track['artists']),
                track['album'],
                track['duration']
            ])
    
    print(f"Exported {len(tracks)} tracks to favorites.csv")
```

### Example 3: Find duplicate tracks across playlists

```python
from tidal_extractor import TidalExtractor
from collections import defaultdict

extractor = TidalExtractor()
if extractor.connect():
    playlists = extractor.get_playlists()
    
    track_occurrences = defaultdict(list)
    
    for playlist in playlists:
        tracks = extractor.get_playlist_tracks(playlist['id'])
        for track in tracks:
            key = (track['title'], ', '.join(track['artists']))
            track_occurrences[key].append(playlist['name'])
    
    duplicates = {k: v for k, v in track_occurrences.items() if len(v) > 1}
    
    print(f"Found {len(duplicates)} duplicate tracks across playlists:")
    for (title, artists), playlists in duplicates.items():
        print(f"'{title}' by {artists} appears in: {', '.join(playlists)}")
```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Ensure you have an active Tidal subscription
2. Try clearing your browser cookies and cache
3. Check your internet connection

### Rate Limiting

Tidal may rate-limit API requests. If you encounter errors:

1. Add delays between requests
2. Reduce the number of concurrent requests
3. Try again later

### Missing Tracks

Some tracks might not be available through the API due to:

1. Regional restrictions
2. Licensing issues
3. API limitations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [tidalapi](https://github.com/tamland/python-tidal) - Python client for the Tidal API
- [Rye](https://rye-up.com/) - Python packaging tool
- [Click](https://click.palletsprojects.com/) - Command-line interface creation kit
- [Rich](https://rich.readthedocs.io/) - Terminal formatting library