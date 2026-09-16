# MP3-Download-Tagging

A simple tool to download audio from YouTube and save it as a tagged mp3.
**Note: Intended for personal use**

## Status

v0.9 — downloads, converts to mp3, tags with artist/title/album/cover art/year/track number/album artist/genre, and renames the file.
Metadata is looked up via iTunes first, falling back to MusicBrainz + Cover Art Archive if iTunes has no match. Title parsing now handles
more real-world YouTube title formats.

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
python main.py "<youtube_url>"
```

Override auto-detected metadata if it guesses wrong:

```bash
python main.py "<youtube_url>" --song "Song Title" --artist "Artist Name"
```

Skip the iTunes lookup (no album/cover art):

```bash
python main.py "<youtube_url>" --no-lookup
```

Files are saved to `downloads/` by default:

```bash
python main.py "<youtube_url>" --output-dir path/to/folder
```

## Version history

- **0.1** — Downloads a YouTube link and converts it to mp3. No tagging yet.
- **0.2** — Auto-parses "Artist - Song" from the video title and writes artist/title ID3 tags. `--artist`/`--song` args override the
  parsed values (skips parsing entirely if both are given).
- **0.3** — Renames the tagged file to "Song - Artist.mp3", sanitizing characters invalid in filenames and avoiding overwrites.
- **0.4** — Looks up album name and cover art via the iTunes Search API.  `--no-lookup` skips this and falls back to title/artist-only tagging.
- **0.5** — Split into `main.py`/`download.py`/`identify.py`/`tagging.py` for readability. No functional changes; run with `python main.py`.
- **0.6** — Falls back to MusicBrainz + Cover Art Archive when iTunes has no album or artwork for a track.
- **0.7** — Also tags year, track number, and album artist.
- **0.8** — Also tags genre; track number now formatted as "track/total" when both are available from iTunes.
- **0.9** — `parse_title()` now handles en-dash/em-dash separators and falls back to a "Song | Artist" pattern when no dash separator is found.

## License

MIT