from urllib.parse import quote_plus
import webbrowser


def build_datasheet_search_url(query: str) -> str:
    """Build a Google search URL for loudspeaker driver datasheets."""
    search_query = f"{query} loudspeaker driver datasheet PDF"
    encoded_query = quote_plus(search_query)
    return f"https://www.google.com/search?q={encoded_query}"


def open_datasheet_search(query: str) -> None:
    """Open a browser search for a driver datasheet."""
    url = build_datasheet_search_url(query)
    webbrowser.open(url)