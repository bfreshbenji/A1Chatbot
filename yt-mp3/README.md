# YouTube → MP3

Paste a YouTube link, get an MP3 (with title tag and cover art). Runs on your
own computer: a small Python server does the download with
[yt-dlp](https://github.com/yt-dlp/yt-dlp) and converts it with ffmpeg.

## Setup (once)

1. Install Python 3.9+.
2. `pip install -r requirements.txt`
3. Install ffmpeg: `brew install ffmpeg` (Mac), `winget install ffmpeg` (Windows),
   or `sudo apt install ffmpeg` (Linux).

## Use it

**Web page:** run `python app.py`. Your browser opens at
http://127.0.0.1:8765. Paste a link, pick a quality, click **Download MP3**.

**Command line:** `python app.py "https://www.youtube.com/watch?v=..."`
saves MP3s into a `downloads` folder. You can pass several links.

## If downloads start failing

YouTube changes often; update yt-dlp: `pip install -U yt-dlp`.

Only download audio you own or have permission to use, and respect YouTube's
Terms of Service.
