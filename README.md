# MP3-Download-Tagging

A simple tool to download audio from YouTube and save it as a tagged mp3.  
**Note: Intended for personal use**

## Status

v0.3 — downloads, converts to mp3, tags with artist/title, and renames the file to "Song - Artist.mp3".

## Setup

```bash
git clone https://github.com/HaadiMalik/MP3-Download-Tagging.git
cd MP3-Download-Tagging
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

You'll also need **ffmpeg** installed and on your PATH (used for audio conversion):
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Windows: download from ffmpeg.org and add it to PATH

## Usage

```bash
python download.py "<youtube_url>"
```

Override auto-detected metadata if it guesses wrong:

```bash
python download.py "<youtube_url>" --song "Song Title" --artist "Artist Name"
```

Files are saved to `downloads/` by default:

```bash
python download.py "<youtube_url>" --output-dir path/to/folder
```

## Version history

- **0.1** — Downloads a YouTube link and converts it to mp3. No tagging yet.
- **0.2** — Auto-parses "Artist - Song" from the video title and writes artist/title ID3 tags. `--artist`/`--song` args override the
  parsed values (skips parsing entirely if both are given).
- **0.3** — Renames the tagged file to "Song - Artist.mp3", sanitizing characters invalid in filenames and avoiding overwrites.

## License

MIT