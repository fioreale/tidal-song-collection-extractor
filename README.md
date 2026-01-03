# Tidal Management Suite

A Python CLI tool to manage and export your Tidal music collection with support for favorites, playlists, and CSV exports.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management.

```bash
# Clone the repository
git clone https://github.com/fioreale/tidal-song-collection-extractor.git
cd tidal-song-collection-extractor

# Install with uv
uv sync

# Or using pip
pip install -e .
```

## Quick Start

All commands require Tidal authentication on first use. Run the entry point:

```bash
python main.py [COMMAND]
```

### Core Commands

**Favorites**
```bash
python main.py favorites                           # Display favorites
python main.py favorites -o tracks.csv             # Export to CSV
python main.py favorites --from-csv tracks.csv     # Load from CSV
python main.py empty-favorites                     # Clear all favorites (destructive!)
```

**Playlists**
```bash
python main.py playlists                           # List all playlists
python main.py playlist list                       # Select and display playlist
python main.py playlist list --id PLAYLIST_ID      # Display specific playlist
python main.py playlist create "Name" -t TRACK_ID  # Create with tracks
python main.py playlist add PLAYLIST_ID TRACK_ID   # Add tracks to playlist
python main.py all-playlists -o all.csv            # Export all playlists
```

**Search**
```bash
python main.py search "query"                      # Search favorites & playlists
python main.py search "query" --from-csv file.csv  # Search within CSV
```

### CSV Export Options

Control CSV output with field selection:

```bash
python main.py favorites -o tracks.csv -f "id,title,artists"
python main.py favorites -o tracks.csv -f "title,album,duration"
```

Available fields: `id`, `title`, `artists`, `album`, `duration`, `playlist`, `source`

## Programmatic Usage

```python
from tidal_extractor import TidalExtractor

extractor = TidalExtractor()
if extractor.connect():
    tracks = extractor.get_favorite_tracks()
    extractor.save_tracks(tracks, "favorites.csv", fields=["id", "title", "artists"])
```

**Track structure:**
```python
{
    'id': str,
    'title': str,
    'artists': list[str],
    'album': str,
    'duration': int  # seconds
}
```

## Project Structure

```
tidal-song-collection-extractor/
├── main.py                  # CLI entry point
├── pyproject.toml           # Dependencies & config
├── uv.lock                  # Lock file
├── src/tidal_extractor/     # Core package
│   ├── __init__.py
│   ├── auth.py              # Tidal authentication
│   ├── cli.py               # CLI utilities
│   ├── collector.py         # Data collection
│   ├── core.py              # Main extractor logic
│   └── formatter.py         # CSV/output formatting
└── tests/
    ├── __init__.py
    └── test_formatter_csv.py
```

## Development

**Setup**
```bash
uv sync --dev
```

**Run tests**
```bash
uv run pytest
```

**Add dependencies**
```bash
uv add package-name
uv sync
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for new functionality
4. Ensure all tests pass: `uv run pytest`
5. Format code consistently with existing style
6. Submit a pull request to `master`

**Code Guidelines:**
- Python 3.8+
- Use type hints where applicable
- Keep functions focused and testable
- Add docstrings for public APIs

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Dependencies

- [tidalapi](https://github.com/tamland/python-tidal) - Tidal API client
- [click](https://click.palletsprojects.com/) - CLI framework
- [rich](https://rich.readthedocs.io/) - Terminal formatting
- [uv](https://github.com/astral-sh/uv) - Package management

---

**Maintainer:** [@fioreale](https://github.com/fioreale)
**Issues:** [GitHub Issues](https://github.com/fioreale/tidal-song-collection-extractor/issues)