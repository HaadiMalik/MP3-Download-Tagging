"""
Handles writing ID3 tags and renaming the mp3 file to match.
"""

import os
import re
from urllib.request import urlopen

from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TALB, APIC


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