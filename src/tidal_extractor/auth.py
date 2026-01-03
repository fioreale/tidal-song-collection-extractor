"""Authentication module for Tidal API."""

import platform
import subprocess
import webbrowser

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

            # Try to open browser automatically
            try:
                console.print("Opening login page in browser...")

                # Ensure URL has proper protocol
                url = login.verification_uri_complete
                if not url.startswith(('http://', 'https://')):
                    url = f"https://{url}"

                # On macOS, use the 'open' command directly for better reliability
                if platform.system() == "Darwin":
                    subprocess.run(["open", url], check=False)
                else:
                    # On other platforms, use webbrowser
                    opened = webbrowser.open_new_tab(url)
                    if not opened:
                        console.print("[yellow]Could not automatically open browser. Please open the URL manually.[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Could not open browser: {e}[/yellow]")
                console.print("[yellow]Please open the URL manually.[/yellow]")

            console.print("Waiting for authorization...")

        else:
            # Even in silent mode, try to open the browser
            try:
                # Ensure URL has proper protocol
                url = login.verification_uri_complete
                if not url.startswith(('http://', 'https://')):
                    url = f"https://{url}"

                if platform.system() == "Darwin":
                    subprocess.run(["open", url], check=False)
                else:
                    webbrowser.open_new_tab(url)
            except:
                pass

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
