"""
version 0.1
Just downloads a YouTube link and converts it to mp3. No tagging yet

../../..>  python download.py "<youtube_url>"
"""

import argparse
import os
import sys

import yt_dlp
from tqdm import tqdm

_pbar = None  # active tqdm bar, tracked across hook calls


def _progress_hook(d: dict):
    """Feeds yt-dlp's download progress into a tqdm bar."""
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


def download_audio(url: str, output_dir: str) -> str:
    """
    Downloads audio from `url` and converts it to mp3 using yt-dlp + ffmpeg.
    Returns the path to the resulting mp3 file.
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

    return mp3_path


def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube link as an mp3."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--output-dir", default="downloads", help="Where to save the mp3")
    args = parser.parse_args()

    print(f"Downloading: {args.url}")
    mp3_path = download_audio(args.url, args.output_dir)
    print(f"Done: {mp3_path}")


if __name__ == "__main__":
    sys.exit(main())