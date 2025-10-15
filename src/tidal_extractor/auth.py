"""Authentication module for Tidal API."""

import tidalapi
from rich.console import Console
from rich.panel import Panel

console = Console()


def authenticate(silent=False):
    """Authenticate with Tidal and return session object.

    Args:
        silent (bool): If True, suppress console output

    Returns:
        tidalapi.Session: Authenticated session or None if authentication fails
    """
    session = tidalapi.Session()

    try:
        if not silent:
            console.print(Panel("Authenticating with Tidal...", title="Authentication"))

        login, future = session.login_oauth()

        if not silent:
            console.print(
                f"Please visit: [bold blue]{login.verification_uri_complete}[/bold blue]"
            )
            console.print("Waiting for authorization...")

        future.result()  # Wait for the user to authorize

        if session.check_login():
            if not silent:
                console.print("[bold green]Successfully logged in![/bold green]")
            return session
        else:
            if not silent:
                console.print("[bold red]Login failed![/bold red]")
            return None
    except Exception as e:
        if not silent:
            console.print(f"[bold red]Authentication error: {str(e)}[/bold red]")
        return None
