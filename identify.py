"""
Handles identifying track metadata: parsing the video title and
looking up additional info (album, cover art) via iTunes or MusicBrainz.
"""

import re
import time

import requests

_MUSICBRAINZ_USER_AGENT = "MP3-Download-Tagging/0.9 (personal use script)"
_last_musicbrainz_call = 0.0


def parse_title(raw_title: str) -> tuple[str, str]:
    """
    Attempting to split and parse video title into (artist, song).
    Falls back to ("Unknown Artist", raw_title) if nothing matches.
    """
    junk = [r"\(official.*?\)", r"\[official.*?\]", r"\(lyrics?.*?\)",
            r"\[lyrics?.*?\]", r"\(audio.*?\)", r"\[audio.*?\]"]
    cleaned = raw_title
    for pattern in junk:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip(" -_|–—")

    for sep in (" - ", " – ", " — "):
        if sep in cleaned:
            artist, song = cleaned.split(sep, 1)
            return artist.strip(), song.strip()

    if " | " in cleaned:
        song, artist = cleaned.split(" | ", 1)
        return artist.strip(), song.strip()

    return "Unknown Artist", cleaned.strip()


def lookup_itunes(artist: str, song: str) -> dict:
    """
    Queries the free iTunes Search API for album, artwork, year, track
    number (as "track/total"), album artist, and genre. Returns {} if
    no match or request fails.
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
        release_date = top.get("releaseDate", "")

        track_num = top.get("trackNumber")
        track_count = top.get("trackCount")
        track_number = f"{track_num}/{track_count}" if track_num and track_count else str(track_num or "")

        return {
            "album": top.get("collectionName", ""),
            "artwork_url": top.get("artworkUrl100", "").replace("100x100", "600x600"),
            "year": release_date[:4] if release_date else "",
            "track_number": track_number,
            "album_artist": top.get("artistName", ""),
            "genre": top.get("primaryGenreName", ""),
        }
    except requests.RequestException:
        return {}


def lookup_musicbrainz(artist: str, song: str) -> dict:
    """
    Queries MusicBrainz for album/year/album artist, then Cover Art
    Archive for artwork. Returns {} if no match or a request fails.
    """
    global _last_musicbrainz_call
    elapsed = time.time() - _last_musicbrainz_call
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)

    headers = {"User-Agent": _MUSICBRAINZ_USER_AGENT}
    try:
        resp = requests.get(
            "https://musicbrainz.org/ws/2/recording",
            params={"query": f'artist:"{artist}" AND recording:"{song}"', "fmt": "json", "limit": 1},
            headers=headers,
            timeout=5,
        )
        _last_musicbrainz_call = time.time()
        resp.raise_for_status()
        recordings = resp.json().get("recordings", [])
        if not recordings or not recordings[0].get("releases"):
            return {}

        release = recordings[0]["releases"][0]
        release_id = release.get("id", "")
        album = release.get("title", "")
        year = release.get("date", "")[:4]
        album_artist = recordings[0].get("artist-credit", [{}])[0].get("name", "")

        artwork_url = ""
        if release_id:
            art_resp = requests.get(
                f"https://coverartarchive.org/release/{release_id}/front-500",
                headers=headers, timeout=5,
            )
            if art_resp.status_code == 200:
                artwork_url = art_resp.url

        return {"album": album, "artwork_url": artwork_url, "year": year,
                "track_number": "", "album_artist": album_artist, "genre": ""}
    except requests.RequestException:
        return {}


def identify_track(artist: str, song: str) -> dict:
    """
    Tries iTunes first, falls back to MusicBrainz if iTunes has no album
    or artwork. Merges fields, preferring whichever source has each one.
    """
    result = lookup_itunes(artist, song)
    if result.get("album") and result.get("artwork_url"):
        return result

    mb_result = lookup_musicbrainz(artist, song)
    fields = ["album", "artwork_url", "year", "track_number", "album_artist", "genre"]
    return {field: result.get(field) or mb_result.get(field, "") for field in fields}