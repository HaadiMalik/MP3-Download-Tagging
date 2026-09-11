"""
Handles identifying track metadata: parsing the video title and
looking up additional info (album, cover art) via iTunes.
"""

import re

import requests


def parse_title(raw_title: str) -> tuple[str, str]:
    """
    Attempting to split and parse video title into (artist, song).
    Strips messy information like "(Official Video)" and expects an "Artist - Song" pattern.
    Falls back to ("Unknown Artist", raw_title) if the hyphen isn't found.
    """
    junk = [r"\(official.*?\)", r"\[official.*?\]", r"\(lyrics?.*?\)",
            r"\[lyrics?.*?\]", r"\(audio.*?\)", r"\[audio.*?\]"]
    cleaned = raw_title
    for pattern in junk:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip(" -_|")

    if " - " in cleaned:
        artist, song = cleaned.split(" - ", 1)
        return artist.strip(), song.strip()
    return "Unknown Artist", cleaned.strip()


def lookup_itunes(artist: str, song: str) -> dict:
    """
    Queries the free iTunes Search API for album name and cover art.
    Returns {} if no match is found or the request fails.
    """
    try:
        resp = requests.get(
            "https://itunes.apple.com/search",
            params={"term": f"{artist} {song}", "media": "music", "limit": 1},
            timeout=5,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            return {}

        top = results[0]
        return {
            "album": top.get("collectionName", ""),
            "artwork_url": top.get("artworkUrl100", "").replace("100x100", "600x600"),
        }
    except requests.RequestException:
        return {}