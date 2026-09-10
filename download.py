"""
version 0.4
0.1 - Downloads a YouTube link, converts to mp3, and tags it (artist/title).
0.2 - Auto-parses "Artist - Title" from the video title; Also use --artist/--song arg override.
0.3 - Renames the file to "Song - Artist.mp3" after tagging.
0.4 - Looks up album + cover art via the iTunes Search API.

../../..>  python download.py "<youtube_url>"
../../..>  python download.py "<youtube_url>" --song "X" --artist "Y"
../../..>  python download.py "<youtube_url>" --no-lookup
"""

import argparse
import os
import re
import sys
from urllib.request import urlopen

import requests
import yt_dlp
from tqdm import tqdm
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TALB, APIC

_pbar = None  # active tqdm bar, tracked across hook calls


def _progress_hook(d: dict):
    global _pbar

    if d["status"] == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        if _pbar is None and total:
            _pbar = tqdm(total=total, unit="B", unit_scale=True, desc="Downloading")
        if _pbar:
            _pbar.n = d.get("downloaded_bytes", 0)
            _pbar.refresh()
    elif d["status"] == "finished" and _pbar:
        _pbar.close()
        _pbar = None


def download_audio(url: str, output_dir: str) -> tuple[str, str]:
    """
    Downloads audio from `url` and converts it to mp3 using yt-dlp + ffmpeg.
    Returns (mp3_path, video_title).
    """
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "progress_hooks": [_progress_hook],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        mp3_path = os.path.splitext(filename)[0] + ".mp3"

    return mp3_path, info.get("title", "")


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


def tag_mp3(mp3_path: str, artist: str, song: str, album: str = "", artwork_url: str = ""):
    """Writes artist/title/album/cover art ID3 tags to the mp3 file."""
    try:
        tags = ID3(mp3_path)
    except ID3NoHeaderError:
        tags = ID3()

    tags["TIT2"] = TIT2(encoding=3, text=song)
    tags["TPE1"] = TPE1(encoding=3, text=artist)
    if album:
        tags["TALB"] = TALB(encoding=3, text=album)

    if artwork_url:
        try:
            image_data = urlopen(artwork_url, timeout=5).read()
            tags["APIC"] = APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=image_data)
        except Exception:
            pass

    tags.save(mp3_path, v2_version=3)


def sanitize_filename(name: str) -> str:
    """Strips characters that aren't valid in filenames on Windows/macOS/Linux."""
    return re.sub(r'[<>:"/\\|?*]', "", name).strip()


def rename_file(mp3_path: str, artist: str, song: str) -> str:
    """
    Renames the mp3 to "Song - Artist.mp3". Appends a number if that
    name is already taken, so an existing file is never overwritten.
    """
    directory = os.path.dirname(mp3_path)
    base_name = sanitize_filename(f"{song} - {artist}")
    new_path = os.path.join(directory, f"{base_name}.mp3")

    counter = 1
    while os.path.exists(new_path) and new_path != mp3_path:
        new_path = os.path.join(directory, f"{base_name} ({counter}).mp3")
        counter += 1

    os.rename(mp3_path, new_path)
    return new_path


def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube link as a tagged mp3."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--song", help="Override auto-detected song title")
    parser.add_argument("--artist", help="Override auto-detected artist")
    parser.add_argument("--output-dir", default="downloads", help="Where to save the mp3")
    parser.add_argument("--no-lookup", action="store_true", help="Skip iTunes lookup (no album/cover art)")
    args = parser.parse_args()

    print(f"Downloading: {args.url}")
    mp3_path, video_title = download_audio(args.url, args.output_dir)

    if args.artist and args.song:
        artist, song = args.artist, args.song
    else:
        artist, song = parse_title(video_title)
        if args.artist:
            artist = args.artist
        if args.song:
            song = args.song

    album, artwork_url = "", ""
    if not args.no_lookup:
        itunes_data = lookup_itunes(artist, song)
        album = itunes_data.get("album", "")
        artwork_url = itunes_data.get("artwork_url", "")

    tag_mp3(mp3_path, artist, song, album, artwork_url)
    mp3_path = rename_file(mp3_path, artist, song)

    print(f"Tagged as: {song} - {artist}" + (f" [{album}]" if album else ""))
    print(f"Done: {mp3_path}")


if __name__ == "__main__":
    sys.exit(main())