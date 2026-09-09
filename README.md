# MP3-Download-Tagging

A simple tool to download audio from YouTube and save it as an mp3.
**Note: Intended for personal use**

## Status

Early/basic version — downloads and converts to mp3 only. Automatic metadata tagging (artist, title, album, cover art) is planned next.

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

Files are saved to `downloads/` by default:

```bash
python download.py "<youtube_url>" --output-dir path/to/folder
```

## License

MIT