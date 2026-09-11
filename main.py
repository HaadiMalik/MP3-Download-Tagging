"""
version 0.6
0.1 - Downloads a YouTube link, converts to mp3, and tags it (artist/title).
0.2 - Auto-parses "Artist - Title" from the video title; Also use --artist/--song arg override.
0.3 - Renames the file to "Song - Artist.mp3" after tagging.
0.4 - Looks up album + cover art via the iTunes Search API.
0.5 - Split into main.py/download.py/identify.py/tagging.py. No behavior changes.
0.6 - Falls back to MusicBrainz + Cover Art Archive if iTunes has no match.

../../..>  python main.py "<youtube_url>"
../../..>  python main.py "<youtube_url>" --song "X" --artist "Y"
../../..>  python main.py "<youtube_url>" --no-lookup
"""

import argparse
import sys

from download import download_audio
from identify import parse_title, identify_track
from tagging import tag_mp3, rename_file


def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube link as a tagged mp3."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--song", help="Override auto-detected song title")
    parser.add_argument("--artist", help="Override auto-detected artist")
    parser.add_argument("--output-dir", default="downloads", help="Where to save the mp3")
    parser.add_argument("--no-lookup", action="store_true", help="Skip metadata lookup (no album/cover art)")
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
        result = identify_track(artist, song)
        album = result.get("album", "")
        artwork_url = result.get("artwork_url", "")

    tag_mp3(mp3_path, artist, song, album, artwork_url)
    mp3_path = rename_file(mp3_path, artist, song)

    print(f"Tagged as: {song} - {artist}" + (f" [{album}]" if album else ""))
    print(f"Done: {mp3_path}")


if __name__ == "__main__":
    sys.exit(main())