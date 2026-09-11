"""
Handles downloading audio from YouTube and converting it to mp3.
"""

import os

import yt_dlp
from tqdm import tqdm

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